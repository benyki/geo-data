# Project Structure

```
.
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   ├── db-suggestion.md
│   └── tree.md
├── scripts/
│   ├── add_slugs.py
│   ├── add_world_slugs.py
│   ├── align_country_names.py
│   ├── check_duplicates.py
│   ├── convert_csv_to_json.py
│   ├── convert_json_to_csv.py
│   ├── enrich_code_postaux.py
│   ├── enrich_communes.py
│   ├── enrich_google_countries.py
│   ├── enrich_regions.py
│   ├── get_lat_long.py
│   ├── load_france_db.py
│   ├── load_world_db.py
│   ├── process_departements.py
│   ├── process_google_countries.py
│   └── sort_az.py
├── france-csv/
│   ├── codes-postaux.csv
│   ├── communes.csv
│   ├── departements.csv
│   └── regions.csv
├── france-json/
│   ├── codes-postaux.json
│   ├── communes.json
│   ├── departements.json
│   └── regions.json
├── world-csv/
│   ├── bucket-list.csv
│   ├── cities.csv
│   ├── countries-by-google.csv
│   ├── countries.csv
│   ├── major_cities.csv
│   └── states.csv
├── world-json/
│   ├── cities.json
│   ├── countries-by-google.json
│   ├── countries.json
│   ├── major_cities.json
│   └── states.json
├── data-not-enriched/
├── migrations/
├── yard/
└── venv/
```

## Directory Descriptions

- **docs/**: Project documentation and specifications
- **scripts/**: Data processing and enrichment scripts
- **france-csv/**: French geographic data in CSV format
- **france-json/**: French geographic data in JSON format  
- **world-csv/**: World geographic data in CSV format
- **world-json/**: World geographic data in JSON format
- **data-not-enriched/**: Raw data files before processing
- **migrations/**: Database migration files
- **yard/**: Additional documentation and resources
- **venv/**: Python virtual environment 