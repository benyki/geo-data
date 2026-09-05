# Provenance

Source and licence for every data file. Check this before redistributing.

## Summary

| Files | Source | Licence | Attribution |
| --- | --- | --- | --- |
| `world/admin1.*` | Natural Earth 10m admin-1 (dissolved for 12 countries) | Public domain | Not required |
| `world/admin2.*` | Natural Earth 10m admin-1 | Public domain | Not required |
| `world/countries.*` | Natural Earth 10m admin-0 + country reference data | Public domain | Not required |
| `france/regions.*` | Natural Earth (dissolved) + INSEE codes | Public domain / Licence Ouverte 2.0 | See note |
| `france/departements.*` | Natural Earth + INSEE codes | Public domain / Licence Ouverte 2.0 | See note |
| `france/collectivites.*` | Natural Earth + INSEE codes | Public domain / Licence Ouverte 2.0 | See note |
| `france/communes.*` | data.gouv.fr | Licence Ouverte 2.0 | **Required** |
| `france/codes-postaux.*` | data.gouv.fr | Licence Ouverte 2.0 | **Required** |
| `world/cities.*` | see "Known issue" below | **Unresolved** | **Assume ODbL** |
| `world/major_cities.*` | population aggregation, enriched via Nominatim | **Unresolved** | **Assume ODbL** |
| `world/bucket-list.csv` | hand-curated | Public domain | Not required |

*Note on France:* the geometry, label points and areas are Natural Earth (public
domain). The `code`, `chefLieu` and `zone` columns are INSEE identifiers from
data.gouv.fr. Identifiers are facts and generally not copyrightable, but if you
redistribute the French files wholesale, credit data.gouv.fr.

## Primary sources

### Natural Earth — 10m cultural vectors
- `ne_10m_admin_1_states_provinces.geojson` — 4,596 first-order subdivisions
- `ne_10m_admin_0_countries.geojson` — 258 countries
- Retrieved: 2026-09-04, from `github.com/nvkelso/natural-earth-vector` (`master`)
- Licence: **public domain**, <https://www.naturalearthdata.com/about/terms-of-use/>
- Rebuild: `uv run scripts/build_geo.py`

### data.gouv.fr — French administrative reference
- Regions, departements, communes, postal codes
- Licence: **Licence Ouverte / Open Licence 2.0** — attribution required
- Attribution string: `Source: data.gouv.fr`

## Known issue — the city files are not licence-clean

`world/cities.*` and `world/major_cities.*` predate this build and their
provenance was never recorded properly. The original README credited "mexwell on
Kaggle" and "Google's public repositories" without links.

Evidence strongly indicates the upstream is
**`dr5hn/countries-states-cities-database`**: byte-identical `id` values
(e.g. `3901` = Badakhshan), an identical column set, and a matching row-count
profile. That database is licensed **ODbL v1.0** — attribution required,
share-alike attaches to derivatives.

Some coordinates were additionally enriched via the **OpenStreetMap Nominatim**
API, which is also ODbL.

**Until this is resolved, treat the city files as ODbL.** If you ship them, you
must attribute and share alike:

    Data by Countries States Cities Database
    https://github.com/dr5hn/countries-states-cities-database | ODbL v1.0

This does **not** affect `world/admin1.*`, `world/countries.*` or the France
region/departement files, which were rebuilt from Natural Earth and carry no
ODbL lineage.

### Why admin-1 was rebuilt rather than restored

An earlier `world/states.csv` (4,223 rows, since replaced by `world/admin1.*`)
was a filtered subset of the dr5hn data. The filter had dropped 854 rows and
taken Spain, the United Kingdom and Belgium to zero coverage.

Natural Earth supplies all of those units *with polygons*, and is public domain,
so the rebuild fixed the coverage gap and the licence problem in one move rather
than restoring ODbL rows.
