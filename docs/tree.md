# Project Structure

```
.
├── README.md
├── AGENTS.md                 # agent rules; says to install skills/geo-data
├── CLAUDE.md                 # points to AGENTS.md
├── LICENSE
├── PROVENANCE.md
├── .gitignore
├── docs/
│   ├── db-suggestion.md
│   └── tree.md
├── scripts/
│   ├── build_geo.py          # rebuilds admin1 + countries + France from Natural Earth
│   ├── check_duplicates.py
│   ├── get_lat_long.py
│   └── sort_az.py
├── skills/
│   └── geo-data/             # the agent skill for this repo (copy to ~/.agents/skills/)
├── flags/
│   ├── 1x1/<cc>.png          # 250 square country flags, 192x192 (flag-icons, MIT)
│   ├── LICENSE-flag-icons
│   └── README.md
├── france/
│   ├── regions.csv|.json|.geojson        # 18 - metropolitaines + DROM
│   ├── departements.csv|.json|.geojson   # 101
│   ├── collectivites.csv|.json|.geojson  # 8 - COM
│   ├── communes.csv|.json
│   └── codes-postaux.csv|.json
├── world/
│   ├── admin1.csv|.json|.geojson|.parquet   # 3,493 - top tier per country
│   ├── admin2.csv|.json|.geojson|.parquet   # 1,237 - 12 countries
│   ├── countries.csv|.json
│   ├── countries-by-google.csv|.json
│   ├── countries-emoji.json
│   ├── cities.csv|.json
│   ├── major_cities.csv|.json
│   └── bucket-list.csv
└── .cache/                   # Natural Earth downloads (gitignored)
```

## Directory descriptions

- **docs/** — documentation and schema notes
- **scripts/** — data processing and build scripts
- **flags/** — square country flag images to crop round or rounded-square,
  named by lowercase ISO alpha-2 code. MIT, not public domain.
- **france/** — French administrative data. Régions, départements and
  collectivités are three separate datasets, not views of one level.
- **world/** — global data. `admin1` is each country's top-tier division;
  `admin2` holds the second tier for the 12 countries that have one.
- **.cache/** — regenerable Natural Earth source files, never committed

Only the scripts listed above are committed; `.gitignore` allowlists them
individually.
