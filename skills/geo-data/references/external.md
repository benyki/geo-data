# Data that is not in the repo

Where each thing comes from, what its licence means for us, and whether it is
worth bringing into the repo. Licences are stated as understood on
2026-11-14: open the source's own terms before shipping.

## Upstreams of what we already have

| Source | Feeds | Licence | Where |
|---|---|---|---|
| Natural Earth, 10m cultural vectors | `world/admin1`, `world/admin2`, `world/countries` enrichment, French polygons | Public domain | `github.com/nvkelso/natural-earth-vector`; the build script downloads `ne_10m_admin_1_states_provinces` and `ne_10m_admin_0_countries` into `.cache/` |
| data.gouv.fr (INSEE, La Poste) | French codes, communes, postal codes | Licence Ouverte 2.0, credit `Source: data.gouv.fr` | `data.gouv.fr`, `geo.api.gouv.fr` |
| flag-icons v7.5.0 | `flags/1x1` | MIT | `github.com/lipis/flag-icons`, npm `flag-icons` |
| dr5hn countries-states-cities database | Most likely `world/cities` | ODbL 1.0 | `github.com/dr5hn/countries-states-cities-database` |
| OpenStreetMap Nominatim | Some city coordinates | ODbL 1.0, and a usage policy of one request a second | `nominatim.org` |

`.cache/` is gitignored and can be deleted; `uv run scripts/build_geo.py`
fetches it again.

## Not in the repo, and where to get it

| Need | Source | Licence | Note |
|---|---|---|---|
| A licence-clean city list with population | GeoNames `cities500`, `cities15000`, `allCountries` | CC BY 4.0 (credit only, no share-alike) | The first choice to replace `world/cities`. Our `admin1.geonames_id` joins onto it |
| City and neighbourhood boundaries, streets, points of interest | OpenStreetMap (Geofabrik extracts, Overpass) | ODbL | Share-alike on derived databases |
| Finer administrative levels worldwide | geoBoundaries, GADM | geoBoundaries is open per country; GADM forbids commercial use | Check each country's licence in geoBoundaries |
| Postal codes outside France | GeoNames postal code dump | CC BY 4.0 | Coverage and precision vary a lot by country |
| Time zone polygons | timezone-boundary-builder | ODbL | For "what time zone is this point in" |
| Elevation, coastlines, rivers, roads, urban areas | Natural Earth physical and cultural themes | Public domain | The same download the build script already uses, other layers |
| Names in more languages, population, facts per place | Wikidata | CC0 | Join on `admin1.wikidata_id` or `cities.wikiDataId` |
| Live geocoding and reverse geocoding | Mapbox, Nominatim | Paid, or rate-limited | Not reference data: do not cache into the repo against the provider's terms |
| Flags that are not countries (EU, UN, England, Scotland, Wales, Catalonia) | flag-icons `1x1` | MIT | 21 exist upstream; render with the commands in `flags/README.md` |
| French IRIS, cadastre, addresses | data.gouv.fr (IGN, BAN) | Licence Ouverte 2.0 | Large; fetch per need |

## The scheduled destinations job

A scheduled task named `geo-data-enrich` is written to add, per country, a
ranked list of travel destinations with an icon each. Its instructions name
`world/countries-jobs-progress.json`, `schema/destination.schema.json`,
`source/world/destinations/<iso2>.json` and
`assets/destinations/icons/<iso2>/<slug>.svg`. None of these are in the repo
on GitHub. Before using or extending that data, find out where the job
actually writes (another machine, or nowhere yet).

## Before adding a dataset to the repo

1. Record its source, retrieval date and licence in `PROVENANCE.md` in the
   same commit. An unrecorded file is how the city files became a problem.
2. Prefer public domain or CC BY sources. Keep ODbL data in clearly named
   files, never merged into a public-domain one.
3. Use the existing keys: `iso2` for countries, `adm1_code` for regions.
4. Keep generated files reproducible: extend `scripts/build_geo.py` rather
   than hand-editing its output.
5. The repo is public. Nothing private, no API keys, no scraped data whose
   terms forbid redistribution.
