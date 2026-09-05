# Open Geo Datasets

Curated geographical datasets for the World and France — **with boundary
polygons**, label points, localized names and computed areas.

Public domain where it matters: you can ship derived data inside a commercial,
offline app with **no attribution required**. See [LICENSE](./LICENSE) and
[PROVENANCE.md](./PROVENANCE.md).

```bash
git clone https://github.com/benyki/geo-data.git
```

## World

Files live in `world/`. Every file is available as CSV and JSON; `admin1` is
additionally published as GeoJSON and GeoParquet.

| File | Rows | Description |
| --- | --- | --- |
| `admin1.csv` / `.json` | 3,493 | Each country's **top-tier** division, attributes only |
| `admin1.geojson` / `.parquet` | 3,493 | The same units **with polygons** (GeoParquet for DuckDB) |
| `admin2.csv` / `.json` | 1,237 | Second-tier units for the 12 countries that have them, with `parent_code` |
| `admin2.geojson` / `.parquet` | 1,237 | The same, with polygons |
| `countries.csv` / `.json` | 250 | Countries with ISO codes, currency, label point, localized names |
| `cities.csv` / `.json` | 150,454 | Cities linked to subdivisions and countries |
| `major_cities.csv` / `.json` | 801 | Major cities with 2023/2024 population |
| `bucket-list.csv` | 177 | Curated travel destinations |

### Two tiers

`admin1` is one row per country's **own top-tier** division — not a fixed size.
For most countries Natural Earth's unit already is that tier and is used as-is.
For twelve countries NE sits a level too low, so those units are dissolved onto
their parent and the originals move to `admin2`:

```
GB  232 → 16     IT  110 → 20     FR  101 → 18     ES   52 → 19
SI  193 → 12     PH  118 → 17     LV  119 →  5     UG  112 →  4
MT   68 →  3     AZ   78 → 10     HU   43 →  7     BE   11 →  3
```

Everywhere else `admin2` is empty, because no second tier exists in the source.

A deliberate non-goal: units are **not** size-consistent across countries, and
cannot be. The Netherlands is 37,000 km² in total; forcing it to France's
42,000 km² per région would give it one region. Weight by `area_km2` and
`labelrank` in your application if you need a fair cross-country metric.

### `admin1` schema

| Column | Notes |
| --- | --- |
| `adm1_code` | **Primary key.** `USA-3521` for a source unit, `FR-nouvelle-aquitaine` for a dissolved one. Unique |
| `admin_level` | Always `1` here; `2` in `admin2.csv` |
| `child_count` | `0` for a source unit, else the number of `admin2` rows dissolved into it |
| `iso_3166_2` | e.g. `FR-33`, `US-CA`. Populated on all 4,596 rows. **Not unique** — see below |
| `iso_3166_2_is_official` | `False` on 188 rows where the code is synthesised, not real ISO |
| `country_code` | ISO 3166-1 alpha-2 |
| `country_name` | |
| `name`, `name_en`, `name_fr`, `name_es`, `name_local` | 99% filled for en/fr/es on source units. **Empty on the 134 dissolved parents** — Natural Earth localizes units, not their parent regions |
| `type` | `State`, `Province`, `Metropolitan department`, … |
| `label_lat`, `label_lng` | **Label anchor, guaranteed inside the polygon** |
| `label_source` | `natural-earth`, or `polylabel` for the 42 rows we repaired |
| `area_km2` | Computed geodesically from the polygon |
| `bbox_min_lng` … `bbox_max_lat` | Bounding box — use it to pre-filter spatial joins |
| `labelrank` | Prominence, lower is more prominent. Use to rank regions |
| `wikidata_id`, `geonames_id` | External join keys |
| `slug` | URL-safe |

`label_lat`/`label_lng` is a pole-of-inaccessibility style anchor, not a
centroid. All 4,596 points were verified to fall inside their own geometry.

`admin2.parent_code` is a foreign key onto `admin1.adm1_code`; `child_count`
sums to exactly the `admin2` row count. On dissolved parents `iso_3166_2` is
carried from Natural Earth's `region_cod` where it looks like a real code
(65 of 134 — France `FR-NAQ`, Italy `IT-65`, Philippines `PH-14`, Azerbaijan)
and is always flagged `iso_3166_2_is_official = False`, because the remaining
countries supply GNS-style codes (`ES.CE`, `LV.VM`) that are not ISO.

**Join on `adm1_code`, not on `iso_3166_2`.** 60 ISO codes map to more than one
row, for two legitimate reasons: Natural Earth sometimes splits one subdivision
into several features (`AF-PAR` is two Parwan polygons), and some ISO codes
genuinely cover several units (`BA-BIH` spans nine Bosnian cantons, `AU-NSW`
includes Lord Howe Island). Grouping by `iso_3166_2` will double-count.

## France

Files live in `france/`. **Régions, départements and collectivités are three
separate datasets** — they are genuinely different things, not views of one.

| File | Rows | Description |
| --- | --- | --- |
| `regions.csv` / `.json` / `.geojson` | 18 | Régions: 13 métropolitaines + 5 DROM |
| `departements.csv` / `.json` / `.geojson` | 101 | Départements: 96 métropolitains + 5 DROM, with `region` foreign key |
| `collectivites.csv` / `.json` / `.geojson` | 8 | COM: Nouvelle-Calédonie, Polynésie française, Wallis-et-Futuna, Saint-Pierre-et-Miquelon, Saint-Barthélemy, Saint-Martin, TAAF, Clipperton |
| `communes.csv` / `.json` | ~35k | Communes with population and postal codes |
| `codes-postaux.csv` / `.json` | | Postal codes mapped to communes |

Why 18 and not 13: each of the five DROM (Guadeloupe, Martinique, Guyane, La
Réunion, Mayotte) is simultaneously a département *and* a région, so INSEE counts
18 régions. Filter on `zone = 'metro'` for the 13 métropolitaines alone.

The eight COM are **not** régions and **not** départements — they are
collectivités with their own status, and most have their own ISO 3166-1 country
code (`iso_3166_1`). They used to be mixed into the regions file; they are now
separate.

Région polygons are dissolved from their départements, so a point is in a région
exactly when it is in one of that région's départements, and `departement_count`
sums to exactly 101. Computed areas agree with INSEE to within ~3%.

The original INSEE columns are preserved and the new ones appended, so the
pre-existing `latitude`/`longitude` (the chef-lieu, e.g. Bordeaux for
Nouvelle-Aquitaine) still sits alongside the new `label_lat`/`label_lng` (the
region's actual visual centre). `label_source` records how each was derived.

## Assigning points to regions

`admin1.parquet` is GeoParquet, so DuckDB's spatial extension reads the geometry
column directly. Filtering on the bounding box first makes the join roughly an
order of magnitude cheaper:

```sql
INSTALL spatial; LOAD spatial;

SELECT p.id, a.iso_3166_2, a.name, a.name_fr, a.country_code
FROM   points p
JOIN   'world/admin1.parquet' a
  ON   p.lon BETWEEN a.bbox_min_lng AND a.bbox_max_lng
 AND   p.lat BETWEEN a.bbox_min_lat AND a.bbox_max_lat
 AND   ST_Within(ST_Point(p.lon, p.lat), a.geometry);
```

Measured at ~188k points/second single-threaded, so ~5 minutes for 51M points.

## Rebuilding

```bash
uv run scripts/build_geo.py
```

Downloads Natural Earth into `.cache/` (gitignored, ~54 MB) and regenerates
`world/admin1.*`, the `world/countries` enrichment and both France datasets.

The build is idempotent: it reads its own output, preserves every existing
column and never drops a row, so re-running produces byte-identical files.

## Data sources

See [PROVENANCE.md](./PROVENANCE.md) for the source and licence of every file.
In short: boundaries, names, label points and areas are **Natural Earth (public
domain)**; French administrative codes are **data.gouv.fr (Licence Ouverte
2.0)**; the two city files have **unresolved provenance and should be treated as
ODbL**.

## Contributing

If you find an error, have a suggestion, or want to add a dataset, please open
an issue or a pull request.
