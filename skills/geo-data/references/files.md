# Files, columns and keys

Paths are relative to the repo, `~/code/+assets/geo-data`. Row counts as of
2026-11-14. The repo's `README.md` has the long explanation of the region
model; this is the lookup sheet.

## world/countries (.csv, .json), 250 rows

Key: `iso2` (also `iso3`, `numeric_code`, `id`).

| Columns | Notes |
|---|---|
| `name`, `native`, `name_fr`, `name_es`, `slug` | English name, name in its own language, French, Spanish |
| `iso2`, `iso3`, `numeric_code`, `tld`, `phone_code` | |
| `capital`, `currency`, `currency_name`, `currency_symbol` | |
| `region`, `subregion` | Continent-level grouping ("Asia", "Southern Asia") |
| `timezones` | A JSON-like string, not clean JSON: parse with care |
| `latitude`, `longitude` | Rough country centre |
| `label_lat`, `label_lng` | Label point inside the country's polygon: use this for a pin |
| `population`, `labelrank` | From Natural Earth; `labelrank` lower is more prominent |
| `emoji`, `emojiU` | Flag emoji and its code points. Plain text only; in a UI use `flags/1x1/<lower(iso2)>.png` |

## world/admin1 (.csv, .json, .geojson, .parquet), 3,493 rows

Each country's own top-tier division. Key: `adm1_code` (`USA-3521` for a
source unit, `FR-nouvelle-aquitaine` for one we dissolved).

`adm1_code, iso_3166_2, iso_3166_2_is_official, country_code, country_name,
name, name_en, name_fr, name_es, name_local, type, child_count, admin_level,
label_lat, label_lng, label_source, area_km2, bbox_min_lng, bbox_min_lat,
bbox_max_lng, bbox_max_lat, labelrank, wikidata_id, geonames_id, slug`

- `country_code` joins onto `countries.iso2`.
- `iso_3166_2` is not unique; `iso_3166_2_is_official` is `False` on
  synthesised codes.
- `child_count` is the number of `admin2` rows under a dissolved parent, `0`
  otherwise.
- `wikidata_id` and `geonames_id` are the keys for joining external data.
- The CSV and JSON have no geometry. Polygons are in the GeoJSON (about
  30 MB) and the GeoParquet (about 15 MB).

## world/admin2 (.csv, .json, .geojson, .parquet), 1,237 rows

Second tier for 12 countries only: GB, IT, FR, ES, SI, PH, LV, UG, MT, AZ, HU,
BE. Same columns as `admin1`, plus `parent_code`, a foreign key onto
`admin1.adm1_code`.

## world/cities (.csv, .json), 150,454 rows. ODbL

`id, name, state_id, state_code, state_name, country_id, country_code,
country_name, latitude, longitude, wikiDataId, slug`

- `country_code` joins onto `countries.iso2`.
- `state_id` and `state_code` come from the upstream database, not from our
  `admin1`: they do **not** join onto `adm1_code`. To put a city in one of our
  regions, do a spatial join on its coordinates.
- No population. The JSON is about 47 MB: read the CSV.

## world/major_cities (.csv, .json), 801 rows. ODbL

`City, Country, Population (2024), Population (2023), Growth Rate, slug`
(plus an unnamed index column). `Country` is a name, not a code. No
coordinates in the committed file.

## world/bucket-list.csv, 177 rows

`Destination, Description, DestinationCountries, TouristsCountries,
YearlyVisitors`. Hand-curated travel destinations with a paragraph each.

## world/countries-by-google (.csv, .json), world/countries-emoji.json, 243 rows

`iso2, name, slug, emoji, emojiU`. An older, smaller country table kept for
the flag emoji. `world/countries` has the same columns and more; prefer it.

## france/regions (.csv, .json, .geojson), 18 rows

Key: `code` (INSEE région code).

`code, chefLieu, nom, typeLiaison, zone, latitude, longitude, slug, name_fr,
departement_count, label_lat, label_lng, label_source, area_km2, bbox_*`

- `zone`: `metro` for the 13 mainland régions, otherwise overseas.
- `latitude`/`longitude` is the chef-lieu (Bordeaux for Nouvelle-Aquitaine);
  `label_lat`/`label_lng` is the région's visual centre.
- Polygons are dissolved from the départements.

## france/departements (.csv, .json, .geojson), 101 rows

Key: `code` (`01` to `95`, `2A`, `2B`, `971` to `976`). `region` is a foreign
key onto `regions.code`.

`code, region, chefLieu, nom, typeLiaison, zone, latitude, longitude, slug,
region_nom, name_fr, iso_3166_2, label_lat, label_lng, label_source, area_km2,
bbox_*`

## france/collectivites (.csv, .json, .geojson), 8 rows

Nouvelle-Calédonie, Polynésie française, Wallis-et-Futuna,
Saint-Pierre-et-Miquelon, Saint-Barthélemy, Saint-Martin, TAAF, Clipperton.
Most have their own country code in `iso_3166_1`.

## france/communes (.csv, .json), 37,642 rows. Attribution required

Key: `code` (INSEE commune code, not the postal code).

`code, nom, typeLiaison, zone, arrondissement, departement, region, type,
rangChefLieu, siren, codesPostaux, population, longitude, latitude, slug,
anciensCodes, chefLieu, commune`

- `departement` and `region` join onto the files above.
- `codesPostaux` holds several postal codes for one commune.
- `type` separates current communes from delegated and associated ones.

## france/codes-postaux (.csv, .json), 6,141 rows. Attribution required

`codePostal, libelleAcheminement, latitude, longitude, communesCount`. One row
per postal code, with a centre point. A postal code can cover several
communes and a commune several postal codes: there is no one-to-one key.

## flags/1x1/<cc>.png, 250 files. MIT

Square country flags, 192x192, named by lowercase ISO alpha-2 code: one for
every row of `world/countries.csv` (`lower(iso2)`). Made to crop to a circle
or a rounded square. `flags/README.md` has the usage rules, and the
`icons-flags` skill has the CSS and native notes for the selected and barred
states.

## Scripts

| Script | What it does |
|---|---|
| `scripts/build_geo.py` | Rebuilds `world/admin1.*`, `world/admin2.*`, the enrichment of `world/countries.*` and the French région, département and collectivité files from Natural Earth. Run with `uv run scripts/build_geo.py`. Idempotent: re-running gives byte-identical files |
| `scripts/check_duplicates.py <csv>` | Lists duplicate names in a CSV's first column |
| `scripts/sort_az.py <csv>` | Sorts a CSV by its first column |
| `scripts/get_lat_long.py` | Old Nominatim enrichment for the major cities file; its paths are stale |
