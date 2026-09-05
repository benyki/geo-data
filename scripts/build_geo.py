# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2.0", "pyarrow>=15"]
# ///
"""
Build the geo-data boundary datasets from Natural Earth (public domain).

Outputs
  world/admin1.{csv,json,geojson,parquet}   first-order subdivisions, with polygons
  world/countries.csv                       enriched in place (label point, fr/es, pop)
  france/departements.{csv,geojson}         101 metropolitan + DOM + COM
  france/regions.{csv,geojson}              18 modern regions, dissolved from departements

Run:  uv run scripts/build_geo.py
Source + licence: see PROVENANCE.md
"""
from __future__ import annotations

import collections
import csv
import json
import math
import os
import sys
import unicodedata
import urllib.request
from heapq import heappush, heappop
from pathlib import Path

from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
SOURCES = {
    "ne_admin1.geojson": f"{NE}/ne_10m_admin_1_states_provinces.geojson",
    "ne_admin0.geojson": f"{NE}/ne_10m_admin_0_countries.geojson",
}
R_EARTH = 6371008.8  # mean radius, metres
NULLS = {None, "", "-99", -99, -99.0, "-1"}


# ---------------------------------------------------------------- helpers
def fetch() -> None:
    CACHE.mkdir(exist_ok=True)
    for name, url in SOURCES.items():
        dest = CACHE / name
        if dest.exists():
            print(f"  cached  {name} ({dest.stat().st_size/1e6:.1f} MB)")
            continue
        print(f"  fetching {name} ...")
        urllib.request.urlretrieve(url, dest)
        print(f"  saved   {name} ({dest.stat().st_size/1e6:.1f} MB)")


def load(name: str) -> list:
    with open(CACHE / name, encoding="utf-8") as fh:
        return json.load(fh)["features"]


def clean(v):
    """Natural Earth uses -99 / -1 as null sentinels, and a few values carry
    stray whitespace (FR-IDF's region_cod has a trailing tab)."""
    if isinstance(v, str):
        v = v.strip()
    return None if v in NULLS else v


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def ring_area(ring) -> float:
    """Signed area of a lon/lat ring on a sphere, in m^2."""
    total = 0.0
    n = len(ring)
    for i in range(n):
        lon1, lat1 = ring[i][0], ring[i][1]
        lon2, lat2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        total += math.radians(lon2 - lon1) * (
            2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2))
        )
    return total * R_EARTH * R_EARTH / 2.0


def area_km2(geom) -> float:
    """Geodesic area of a shapely polygon/multipolygon, km^2. Holes subtracted."""
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    total = 0.0
    for p in polys:
        total += abs(ring_area(list(p.exterior.coords)))
        for hole in p.interiors:
            total -= abs(ring_area(list(hole.coords)))
    return round(total / 1e6, 3)


def polylabel(geom, precision: float = 0.002):
    """Pole of inaccessibility - the point furthest from any edge, inside the shape.

    Mapbox's grid-refinement algorithm. Unlike a centroid this is guaranteed to
    fall inside the polygon, which matters for crescents, archipelagos and
    anything concave.
    """
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda p: p.area)
    minx, miny, maxx, maxy = geom.bounds
    size = min(maxx - minx, maxy - miny)
    if size == 0:
        return geom.representative_point()

    def cell(cx, cy, h):
        d = geom.exterior.distance(Point(cx, cy))
        if not geom.contains(Point(cx, cy)):
            d = -d
        return (-(d + h * math.sqrt(2)), cx, cy, h, d)

    cell_size = size / 2
    queue = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            heappush(queue, cell(x + cell_size, y + cell_size, cell_size))
            y += size / 2
        x += size / 2

    best = cell(*geom.representative_point().coords[0], 0)
    while queue:
        _, cx, cy, h, d = heappop(queue)
        if d > best[4]:
            best = (_, cx, cy, h, d)
        if -_ - best[4] <= precision:
            continue
        h /= 2
        for dx, dy in ((-h, -h), (h, -h), (-h, h), (h, h)):
            heappush(queue, cell(cx + dx, cy + dy, h))
    return Point(best[1], best[2])


def label_point(geom, ne_lon, ne_lat):
    """Prefer Natural Earth's cartographic label point; repair it if it falls outside."""
    if ne_lon is not None and ne_lat is not None:
        p = Point(float(ne_lon), float(ne_lat))
        if geom.contains(p):
            return round(p.x, 6), round(p.y, 6), "natural-earth"
    p = polylabel(geom)
    return round(p.x, 6), round(p.y, 6), "polylabel"


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)}  ({len(rows)} rows, {path.stat().st_size/1e3:.0f} KB)")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
    print(f"  wrote {path.relative_to(ROOT)}  ({path.stat().st_size/1e6:.1f} MB)")


def write_geojson(path: Path, rows: list[dict], geoms: dict, key: str) -> None:
    feats = [
        {"type": "Feature", "properties": r, "geometry": mapping(geoms[r[key]])}
        for r in rows
        if r.get(key) in geoms
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh,
                  ensure_ascii=False, separators=(",", ":"))
    print(f"  wrote {path.relative_to(ROOT)}  ({len(feats)} features, {path.stat().st_size/1e6:.1f} MB)")


def write_parquet(path: Path, rows: list[dict], geoms: dict, key: str) -> None:
    """GeoParquet 1.0 - geometry as WKB, readable by DuckDB spatial."""
    from shapely import to_wkb
    cols = {k: [] for k in rows[0]}
    wkb = []
    for r in rows:
        for k in cols:
            cols[k].append(r.get(k))
        wkb.append(to_wkb(geoms[r[key]]) if r[key] in geoms else None)
    table = pa.table({**cols, "geometry": pa.array(wkb, type=pa.binary())})
    meta = {
        "version": "1.0.0",
        "primary_column": "geometry",
        "columns": {
            "geometry": {
                "encoding": "WKB",
                "geometry_types": ["Polygon", "MultiPolygon"],
                "crs": None,
            }
        },
    }
    schema = table.schema.with_metadata({b"geo": json.dumps(meta).encode()})
    pq.write_table(table.cast(schema), path, compression="zstd")
    print(f"  wrote {path.relative_to(ROOT)}  ({len(rows)} rows, {path.stat().st_size/1e6:.1f} MB)")


# ---------------------------------------------------------------- world/admin1
# Countries where Natural Earth's units sit BELOW the country's own top tier.
# For these we dissolve on the `region` parent field; the raw units become admin-2.
# Everywhere else NE's unit already is the top tier and is used as-is.
DISSOLVE = {"GB", "IT", "FR", "ES", "SI", "PH", "LV", "UG", "MT", "AZ", "HU", "BE"}

BASE_COLS = [
    "iso_3166_2", "iso_3166_2_is_official", "country_code", "country_name",
    "name", "name_en", "name_fr", "name_es", "name_local", "type",
    "admin_level", "label_lat", "label_lng", "label_source",
    "area_km2", "bbox_min_lng", "bbox_min_lat", "bbox_max_lng", "bbox_max_lat",
    "labelrank", "wikidata_id", "geonames_id", "slug",
]
ADMIN1_COLS = ["adm1_code"] + BASE_COLS[:10] + ["child_count"] + BASE_COLS[10:]
ADMIN2_COLS = ["adm2_code", "parent_code"] + BASE_COLS


def unit_row(f, iso2_by_name):
    """One Natural Earth admin-1 feature -> a flat row + its geometry."""
    p = f["properties"]
    g = shape(f["geometry"])
    if not g.is_valid:
        g = g.buffer(0)
    iso = str(p.get("iso_3166_2") or "").strip()
    lng, lat, src = label_point(g, clean(p.get("longitude")), clean(p.get("latitude")))
    minx, miny, maxx, maxy = g.bounds
    name = clean(p.get("name")) or clean(p.get("name_en")) or p["adm1_code"]
    return {
        "code": p["adm1_code"],
        "iso_3166_2": iso.replace("~", "") or None,
        "iso_3166_2_is_official": "~" not in iso and not iso.startswith("-99"),
        "country_code": clean(p.get("iso_a2")) or iso2_by_name.get(p.get("admin")),
        "country_name": clean(p.get("admin")),
        "name": name,
        "name_en": clean(p.get("name_en")),
        "name_fr": clean(p.get("name_fr")),
        "name_es": clean(p.get("name_es")),
        "name_local": clean(p.get("name_local")),
        "type": clean(p.get("type_en")) or clean(p.get("type")),
        "label_lat": lat, "label_lng": lng, "label_source": src,
        "area_km2": area_km2(g),
        "bbox_min_lng": round(minx, 6), "bbox_min_lat": round(miny, 6),
        "bbox_max_lng": round(maxx, 6), "bbox_max_lat": round(maxy, 6),
        "labelrank": clean(p.get("labelrank")),
        "wikidata_id": clean(p.get("wikidataid")),
        "geonames_id": clean(p.get("gn_id")),
        "slug": slugify(name),
        "_region": clean(p.get("region")),
        "_region_cod": clean(p.get("region_cod")),
    }, g


def build_world(feats1, iso2_by_name):
    """Return (admin1 rows, admin1 geoms, admin2 rows, admin2 geoms).

    admin-1 is one row per country's top-tier division. For the 12 countries in
    DISSOLVE that means merging Natural Earth's units up to their `region`
    parent; elsewhere the NE unit already is the top tier.
    """
    units, ugeom = [], {}
    for f in feats1:
        if not f.get("geometry"):
            continue
        r, g = unit_row(f, iso2_by_name)
        units.append(r)
        ugeom[r["code"]] = g

    a1, a1g, a2, a2g = [], {}, [], {}
    by_cc = collections.defaultdict(list)
    for r in units:
        by_cc[r["country_code"]].append(r)

    for cc, rows in by_cc.items():
        parents = {r["_region"] for r in rows if r["_region"]}
        dissolving = cc in DISSOLVE and parents
        # Units with no parent pass through as admin-1 in their own right, so a
        # single orphan (Clipperton is one for FR) cannot veto a whole country.
        for r in rows if not dissolving else [x for x in rows if not x["_region"]]:
            r = {k: v for k, v in r.items() if not k.startswith("_")}
            r["adm1_code"] = r.pop("code")
            r["admin_level"] = 1
            r["child_count"] = 0
            a1.append(r)
            a1g[r["adm1_code"]] = ugeom[r["adm1_code"]]
        if not dissolving:
            continue

        for region in sorted(parents):
            kids = [r for r in rows if r["_region"] == region]
            g = unary_union([ugeom[k["code"]] for k in kids])
            if not g.is_valid:
                g = g.buffer(0)
            code = f"{cc}-{slugify(region)}"
            lng, lat, src = label_point(g, None, None)
            minx, miny, maxx, maxy = g.bounds
            # NE's region_cod is a real ISO 3166-2 code for some countries
            # (FR-HDF, IT-21) and a GNS-style one for others (ES.CE, LV.VM),
            # so it is carried but never claimed as official.
            rc = {k["_region_cod"] for k in kids if k["_region_cod"]}
            iso = rc.pop() if len(rc) == 1 and "-" in str(next(iter(rc), "")) else None
            ranks = [int(k["labelrank"]) for k in kids if k["labelrank"] is not None]
            a1.append({
                "adm1_code": code,
                "iso_3166_2": iso,
                "iso_3166_2_is_official": False,
                "country_code": cc,
                "country_name": kids[0]["country_name"],
                "name": region,
                "name_en": region,
                "name_fr": None, "name_es": None, "name_local": None,
                "type": None,
                "admin_level": 1,
                "child_count": len(kids),
                "label_lat": lat, "label_lng": lng, "label_source": src,
                "area_km2": area_km2(g),
                "bbox_min_lng": round(minx, 6), "bbox_min_lat": round(miny, 6),
                "bbox_max_lng": round(maxx, 6), "bbox_max_lat": round(maxy, 6),
                "labelrank": min(ranks) if ranks else None,
                "wikidata_id": None, "geonames_id": None,
                "slug": slugify(region),
            })
            a1g[code] = g
            for k in kids:
                r = {x: v for x, v in k.items() if not x.startswith("_")}
                r["adm2_code"] = r.pop("code")
                r["parent_code"] = code
                r["admin_level"] = 2
                a2.append(r)
                a2g[r["adm2_code"]] = ugeom[r["adm2_code"]]

    a1.sort(key=lambda r: (r["country_code"] or "ZZ", r["name"]))
    a2.sort(key=lambda r: (r["country_code"] or "ZZ", r["name"]))
    return a1, a1g, a2, a2g


# ---------------------------------------------------------------- countries
OVERSEAS_AS_ADMIN1: dict = {}


def enrich_countries(feats0):
    """Add label point, fr/es names, population and prominence to world/countries.csv."""
    # Natural Earth reuses a sovereign's ISO code for its dependencies: Clipperton
    # and Baikonur both carry FR / KZ. Prefer the sovereign entity, then population.
    rank = {"Sovereign country": 0, "Country": 1, "Disputed": 2, "Indeterminate": 3,
            "Sovereignty": 4, "Lease": 5, "Dependency": 6}

    def score(p):
        return (rank.get(p.get("TYPE"), 9), -(p.get("POP_EST") or 0))

    def iso2(p):
        """NE stores Taiwan as ISO_A2='CN-TW'; only a real 2-letter code counts."""
        for k in ("ISO_A2", "ISO_A2_EH"):
            v = clean(p.get(k))
            if v and len(str(v)) == 2:
                return str(v)
        return None

    by_iso, by_name = {}, {}
    for f in feats0:
        p = f["properties"]
        cc = iso2(p)
        if cc and (cc not in by_iso or score(p) < score(by_iso[cc])):
            by_iso[cc] = p
        for k in ("NAME", "NAME_EN", "NAME_LONG", "GEOUNIT"):
            n = clean(p.get(k))
            if n:
                by_name.setdefault(slugify(n), p)
    path = ROOT / "world" / "countries.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    added = ["name_fr", "name_es", "label_lat", "label_lng", "population", "labelrank"]
    hit = 0
    for r in rows:
        p = by_iso.get(r["iso2"]) or by_name.get(slugify(r["name"]))
        if not p:
            # French overseas departments are admin-1 units of France in NE
            sub = OVERSEAS_AS_ADMIN1.get(r["iso2"])
            if sub:
                r["name_fr"], r["name_es"] = sub["name_fr"], sub["name_es"]
                r["label_lat"], r["label_lng"] = sub["label_lat"], sub["label_lng"]
                r["population"], r["labelrank"] = None, sub["labelrank"]
                hit += 1
                continue
            for k in added:
                r[k] = None
            continue
        hit += 1
        r["name_fr"] = clean(p.get("NAME_FR"))
        r["name_es"] = clean(p.get("NAME_ES"))
        r["label_lat"] = round(float(p["LABEL_Y"]), 6) if clean(p.get("LABEL_Y")) is not None else None
        r["label_lng"] = round(float(p["LABEL_X"]), 6) if clean(p.get("LABEL_X")) is not None else None
        r["population"] = clean(p.get("POP_EST"))
        r["labelrank"] = clean(p.get("LABELRANK"))
    cols = list(rows[0].keys())
    print(f"  matched {hit}/{len(rows)} countries against Natural Earth admin-0")
    write_csv(path, rows, cols)
    write_json(ROOT / "world" / "countries.json", rows)
    return by_iso


# ---------------------------------------------------------------- france
# Appended to whatever columns the source file already has, so the build is
# idempotent: it reads its own output and never loses a column or a row.
GEO_COLS = ["label_lat", "label_lng", "label_source", "area_km2",
            "bbox_min_lng", "bbox_min_lat", "bbox_max_lng", "bbox_max_lat"]
DEP_EXTRA = ["region_nom", "name_fr", "iso_3166_2"] + GEO_COLS
REG_EXTRA = ["name_fr", "departement_count"] + GEO_COLS

# COM territories are separate countries in Natural Earth, not French subdivisions
COM_TO_ISO = {"975": "PM", "977": "BL", "978": "MF", "984": "TF",
              "986": "WF", "987": "PF", "988": "NC"}
DOM_TO_NE = {"971": "FR-GP", "972": "FR-MQ", "973": "FR-GF", "974": "FR-RE", "976": "FR-YT"}
# Clipperton has no ISO 3166-2 code; Natural Earth carries it by adm1_code only
ADM1_BY_CODE = {"989": "CLP+00?"}

# Appended to whatever columns the source file already has, so the build is
# idempotent: it reads its own output and never loses a column or a row.
GEO_COLS = ["label_lat", "label_lng", "label_source", "area_km2",
            "bbox_min_lng", "bbox_min_lat", "bbox_max_lng", "bbox_max_lat"]
DEP_EXTRA = ["region_nom", "name_fr", "iso_3166_2"] + GEO_COLS
REG_EXTRA = ["name_fr", "departement_count"] + GEO_COLS
COL_EXTRA = ["name_fr", "iso_3166_1"] + GEO_COLS


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def attach(row: dict, g, ne_lon=None, ne_lat=None) -> None:
    lng, lat, src = label_point(g, ne_lon, ne_lat)
    minx, miny, maxx, maxy = g.bounds
    row.update({
        "label_lat": lat, "label_lng": lng, "label_source": src,
        "area_km2": area_km2(g),
        "bbox_min_lng": round(minx, 6), "bbox_min_lat": round(miny, 6),
        "bbox_max_lng": round(maxx, 6), "bbox_max_lat": round(maxy, 6),
    })


def build_france(feats1, feats0):
    """France has three levels that are genuinely different things:

      regions        18 - 13 metropolitaines + 5 DROM (each DROM is both a
                          departement and a region, which is why INSEE says 18)
      departements  101 - 96 metropolitains + the 5 DROM
      collectivites   8 - COM. Not regions and not departements: Nouvelle-Caledonie,
                          Polynesie francaise, Wallis-et-Futuna, Saint-Pierre-et-
                          Miquelon, Saint-Barthelemy, Saint-Martin, TAAF, Clipperton.

    Reads the union of its own three output files, so re-running never loses a row.
    """
    deps = read_rows(ROOT / "france" / "departements.csv")
    regs_all = read_rows(ROOT / "france" / "regions.csv") + \
        read_rows(ROOT / "france" / "collectivites.csv")
    seen = set()
    regs_all = [r for r in regs_all
                if not (r["code"] in seen or seen.add(r["code"]))]
    reg_name = {r["code"]: r["nom"] for r in regs_all}

    ne_fr = {str(f["properties"].get("iso_3166_2")): f for f in feats1
             if f["properties"].get("iso_a2") == "FR" and f.get("geometry")}
    ne_adm1 = {f["properties"].get("adm1_code"): f for f in feats1 if f.get("geometry")}
    ne_co = {}
    for f in feats0:
        p = f["properties"]
        cc = clean(p.get("ISO_A2")) or clean(p.get("ISO_A2_EH"))
        if cc and f.get("geometry"):
            ne_co.setdefault(cc, f)

    def geom_of(feat):
        g = shape(feat["geometry"])
        return g if g.is_valid else g.buffer(0)

    # --- departements: metropolitain + DROM only -------------------------
    dep_rows, dep_geoms, missing = [], {}, []
    for d in deps:
        code = d["code"]
        if code in COM_TO_ISO or code in ADM1_BY_CODE:
            continue  # a COM, handled below
        feat = ne_fr.get(f"FR-{code}") or ne_fr.get(DOM_TO_NE.get(code, ""))
        d["region_nom"] = reg_name.get(d["region"])
        if not feat:
            missing.append(f"{code} {d['nom']}")
            d.update({k: d.get(k) for k in DEP_EXTRA})
            dep_rows.append(d)
            continue
        g = geom_of(feat)
        p = feat["properties"]
        dep_geoms[code] = g
        d["name_fr"] = clean(p.get("name_fr")) or d["nom"]
        d["iso_3166_2"] = f"FR-{code}" if f"FR-{code}" in ne_fr else DOM_TO_NE.get(code)
        attach(d, g, clean(p.get("longitude")), clean(p.get("latitude")))
        dep_rows.append(d)
    if missing:
        print(f"  note: no geometry for {len(missing)} departement(s): {', '.join(missing)}")

    # --- regions: dissolve of their departements -------------------------
    reg_rows, reg_geoms, col_rows, col_geoms = [], {}, [], {}
    for r in regs_all:
        code = r["code"]
        if r.get("zone") == "com" or code in COM_TO_ISO or code in ADM1_BY_CODE:
            feat = ne_co.get(COM_TO_ISO.get(code, "")) or ne_adm1.get(ADM1_BY_CODE.get(code, ""))
            r["iso_3166_1"] = COM_TO_ISO.get(code)
            r["name_fr"] = r["nom"]
            if feat:
                g = geom_of(feat)
                col_geoms[code] = g
                p = feat["properties"]
                attach(r, g, clean(p.get("LABEL_X") or p.get("longitude")),
                       clean(p.get("LABEL_Y") or p.get("latitude")))
            col_rows.append(r)
            continue
        parts = [dep_geoms[d["code"]] for d in deps
                 if d["region"] == code and d["code"] in dep_geoms]
        r["name_fr"] = r["nom"]
        r["departement_count"] = len(parts)
        if not parts:
            print(f"  note: region {code} {r['nom']} has no departement geometry")
            reg_rows.append(r)
            continue
        g = unary_union(parts)
        if not g.is_valid:
            g = g.buffer(0)
        reg_geoms[code] = g
        attach(r, g)
        reg_rows.append(r)

    return dep_rows, dep_geoms, reg_rows, reg_geoms, col_rows, col_geoms


# ---------------------------------------------------------------- main
def main() -> int:
    print("fetching sources")
    fetch()

    print("\nloading")
    feats1 = load("ne_admin1.geojson")
    feats0 = load("ne_admin0.geojson")
    print(f"  admin-1 features: {len(feats1)}   admin-0 features: {len(feats0)}")

    print("\nbuilding world/admin1  (label points + geodesic area, this takes a minute)")
    iso2_by_name = {clean(p["properties"].get("ADMIN")): (clean(p["properties"].get("ISO_A2"))
                    or clean(p["properties"].get("ISO_A2_EH"))) for p in feats0}
    rows, geoms, a2_rows, a2_geoms = build_world(feats1, iso2_by_name)
    # French overseas departments are ISO countries in their own right but
    # admin-1 units of France in Natural Earth; index them for the enrichment step.
    for ne_code in DOM_TO_NE.values():
        match = next((r for r in rows if r["iso_3166_2"] == ne_code), None)
        if match:
            OVERSEAS_AS_ADMIN1[ne_code.split("-")[1]] = match

    print("\nenriching world/countries")
    enrich_countries(feats0)
    write_csv(ROOT / "world" / "admin1.csv", rows, ADMIN1_COLS)
    write_json(ROOT / "world" / "admin1.json", rows)
    write_geojson(ROOT / "world" / "admin1.geojson", rows, geoms, "adm1_code")
    write_parquet(ROOT / "world" / "admin1.parquet", rows, geoms, "adm1_code")
    write_csv(ROOT / "world" / "admin2.csv", a2_rows, ADMIN2_COLS)
    write_json(ROOT / "world" / "admin2.json", a2_rows)
    write_geojson(ROOT / "world" / "admin2.geojson", a2_rows, a2_geoms, "adm2_code")
    write_parquet(ROOT / "world" / "admin2.parquet", a2_rows, a2_geoms, "adm2_code")

    print("\nbuilding france/departements and france/regions")
    dep_rows, dep_geoms, reg_rows, reg_geoms, col_rows, col_geoms = build_france(feats1, feats0)
    dep_cols = list(dict.fromkeys(list(dep_rows[0].keys()) + DEP_EXTRA))
    write_csv(ROOT / "france" / "departements.csv", dep_rows, dep_cols)
    write_json(ROOT / "france" / "departements.json", dep_rows)
    write_geojson(ROOT / "france" / "departements.geojson", dep_rows, dep_geoms, "code")
    reg_cols = list(dict.fromkeys(list(reg_rows[0].keys()) + REG_EXTRA))
    write_csv(ROOT / "france" / "regions.csv", reg_rows, reg_cols)
    write_json(ROOT / "france" / "regions.json", reg_rows)
    write_geojson(ROOT / "france" / "regions.geojson", reg_rows, reg_geoms, "code")
    col_cols = list(dict.fromkeys(list(col_rows[0].keys()) + COL_EXTRA))
    write_csv(ROOT / "france" / "collectivites.csv", col_rows, col_cols)
    write_json(ROOT / "france" / "collectivites.json", col_rows)
    write_geojson(ROOT / "france" / "collectivites.geojson", col_rows, col_geoms, "code")

    print("\nsummary")
    diss = sorted({r["country_code"] for r in a2_rows})
    print(f"  admin-1 units        {len(rows)}")
    print(f"  admin-2 units        {len(a2_rows)}  ({len(diss)} countries: {', '.join(diss)})")
    print(f"  dissolved parents    {sum(1 for r in rows if r['child_count'])}")
    print(f"  countries covered    {len({r['country_code'] for r in rows if r['country_code']})}")
    print(f"  official ISO codes   {sum(1 for r in rows if r['iso_3166_2_is_official'])}")
    print(f"  label pts repaired   {sum(1 for r in rows if r['label_source']=='polylabel')}")
    print(f"  FR departements      {len(dep_rows)}")
    print(f"  FR regions           {len(reg_rows)}")
    print(f"  FR collectivites     {len(col_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
