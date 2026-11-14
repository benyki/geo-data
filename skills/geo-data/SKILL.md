---
name: geo-data
description: Our geographic datasets and what is missing from them - the geo-data repo (countries, regions with boundary polygons, cities, French régions, départements, communes and postal codes, a travel bucket list, and 250 square country flags), the licence of each file, the join keys and traps, and where to get what the repo does not hold (Natural Earth, data.gouv.fr, GeoNames, OpenStreetMap, flag-icons). Use when a task needs a list of countries or regions, ISO codes, country names in French or Spanish, a country's capital, currency or phone code, a label point or a boundary polygon, "which region is this lat/lng in", French administrative data, a city list, a country flag, or when deciding whether geo data can be shipped inside an app.
---

# geo-data

One repo holds our geographic reference data: `~/code/+assets/geo-data`,
public on GitHub as `benyki/geo-data`. This skill says what is in it, what
each file may be used for, and where to go for what it does not have.

The skill holds no data. Read the files from the repo; if the folder is
missing, clone it:

```bash
git clone https://github.com/benyki/geo-data.git ~/code/+assets/geo-data
```

The repo keeps a copy of this skill in `skills/geo-data/`. Edit the skill in
`~/.agents/skills/geo-data/`, then copy it back into the repo (its `AGENTS.md`
says how).

## Start here

1. Find the file in the table below.
2. Check its licence column before shipping anything derived from it.
3. Open [`references/files.md`](references/files.md) for its columns and keys.
4. If the table does not have what you need, open
   [`references/external.md`](references/external.md) before searching the web.

## What is in the repo

Every tabular file exists as CSV and JSON. Files with polygons also exist as
GeoJSON, and the two world region files as GeoParquet.

| Data | File | Rows | Licence |
|---|---|---|---|
| Countries | `world/countries` | 250 | Public domain |
| Regions, top tier per country, with polygons | `world/admin1` | 3,493 | Public domain |
| Regions, second tier, 12 countries only | `world/admin2` | 1,237 | Public domain |
| Cities | `world/cities` | 150,454 | **Treat as ODbL** |
| Major cities with population | `world/major_cities` | 801 | **Treat as ODbL** |
| Travel destinations, hand-curated | `world/bucket-list.csv` | 177 | Public domain |
| Country flag emoji table | `world/countries-by-google`, `world/countries-emoji.json` | 243 | Unrecorded |
| French régions | `france/regions` | 18 | Public domain, INSEE codes |
| French départements | `france/departements` | 101 | Public domain, INSEE codes |
| French collectivités d'outre-mer | `france/collectivites` | 8 | Public domain, INSEE codes |
| French communes | `france/communes` | 37,642 | Licence Ouverte 2.0, **attribution required** |
| French postal codes | `france/codes-postaux` | 6,141 | Licence Ouverte 2.0, **attribution required** |
| Country flags, square PNG | `flags/1x1/<cc>.png` | 250 | MIT, **keep the notice** |

`PROVENANCE.md` in the repo is the authority on source and licence. Read it
before redistributing.

## Can I ship it in an app?

- **Yes, no attribution**: countries, admin1, admin2, the French régions,
  départements and collectivités, the bucket list. Natural Earth is public
  domain and our own work on it is CC0.
- **Yes, with a credit**: French communes and postal codes
  (`Source: data.gouv.fr`), and the flags (keep `flags/LICENSE-flag-icons`
  with them, or reproduce the MIT notice in the app's licences screen).
- **Careful**: `world/cities` and `world/major_cities`. Their origin was never
  recorded; the evidence points to the dr5hn countries-states-cities database
  and OpenStreetMap Nominatim, both ODbL. Shipping them means attribution and
  share-alike on the derived database. For a commercial offline app, prefer a
  city list you rebuild from GeoNames (see `references/external.md`).

## Rules that bite

- **Join regions on `adm1_code`, never on `iso_3166_2`.** 60 ISO codes map to
  more than one row, so grouping by ISO code double-counts.
- **`label_lat` / `label_lng` is not a centroid.** It is a point guaranteed to
  be inside the polygon, made for placing a label or a pin. The older
  `latitude` / `longitude` columns are something else (a rough country centre,
  or the chef-lieu in the French files).
- **Regions are not the same size across countries**, on purpose. Weight by
  `area_km2` or `labelrank` when comparing.
- **France has 18 régions, not 13.** The five overseas ones are both a région
  and a département. Filter `zone = 'metro'` for the 13.
- **The eight collectivités are neither régions nor départements.** They have
  their own file.
- **Names**: `name_fr` and `name_es` are filled on countries and on 99% of
  source regions, but empty on the 134 regions we dissolved from smaller
  units.
- **Flags are images, not emoji.** `world/countries.csv` has an `emoji`
  column; use it only in plain text you do not render yourself. In any UI use
  `flags/1x1/<lower(iso2)>.png` and the `icons-flags` skill, which has the
  crops and the selected and barred states.
- **Do not edit the generated files by hand.** `world/admin1.*`,
  `world/admin2.*`, the enrichment columns of `world/countries.*` and the
  French région, département and collectivité files come out of
  `uv run scripts/build_geo.py`. Change the script and rebuild.

## Which region is this point in?

`world/admin1.parquet` is GeoParquet; DuckDB's spatial extension reads it
directly. Filter on the bounding box first:

```sql
INSTALL spatial; LOAD spatial;

SELECT p.id, a.adm1_code, a.name, a.country_code
FROM   points p
JOIN   'world/admin1.parquet' a
  ON   p.lon BETWEEN a.bbox_min_lng AND a.bbox_max_lng
 AND   p.lat BETWEEN a.bbox_min_lat AND a.bbox_max_lat
 AND   ST_Within(ST_Point(p.lon, p.lat), a.geometry);
```

About 188,000 points a second on one thread.

## What the repo does not have

The short list; details and sources are in `references/external.md`.

- Natural Earth's source files: downloaded to `.cache/` (gitignored, about
  54 MB) by the build script, never committed.
- City boundaries, neighbourhoods, streets, points of interest.
- Postal codes outside France.
- Third-tier divisions, and second-tier ones outside 12 countries.
- Time zone polygons, elevation, coastlines, rivers, roads.
- Population for regions, and current population for most cities.
- Flags that are not countries (EU, UN, England, Scotland, Catalonia).
- Per-country destination lists and icons: a scheduled task
  (`geo-data-enrich`) is written to produce them, but its progress file,
  schema and output folders are not in the repo. Check where its output goes
  before relying on it.

## Loose ends in the repo

- `world/countries-by-google.*` and `world/countries-emoji.json` (243 rows of
  code, name, slug, flag emoji) are not described in the README or in
  `PROVENANCE.md`.
- `.gitignore` allowlists `scripts/enrich_major_cities.py` and
  `scripts/enrich_postaux.py`, which are not in `scripts/`.
- `docs/db-suggestion.md` describes a database schema based on the old
  `states` table, which `admin1` replaced.
- `scripts/get_lat_long.py` points at a `world-csv/` folder that no longer
  exists.
