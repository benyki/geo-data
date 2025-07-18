# Open Geo Datasets

A collection of curated and enriched geographical datasets for France and the World, ready for your next project.

This repository provides clean, easy-to-use geographical data in both CSV and JSON formats. The datasets have been sourced from official government platforms and reputable open-data providers, then cleaned and enriched with useful information like coordinates and URL-friendly slugs.

## 🚀 Getting Started

All data is located in the `world-csv/`, `world-json/`, `france-csv/`, and `france-json/` directories. You can clone this repository or download the files directly.

```bash
git clone https://github.com/benyki/geo-data.git
```

## 📂 File Descriptions

### World Data

Located in `world-csv/` and `world-json/`.

| File Name          | Description                                                                 | Format      |
| ------------------ | --------------------------------------------------------------------------- | ----------- |
| `countries.csv`    | A list of all countries with their ISO2 codes, names, and emojis.           | CSV         |
| `states.csv`       | States and provinces for all countries, linked by `country_code`.           | CSV         |
| `cities.csv`       | A large list of cities, linked to states and countries.                     | CSV         |
| `major_cities.csv` | A curated list of major world cities with recent population data.           | CSV         |
| `countries.json`   | JSON version of the countries dataset.                                      | JSON        |
| ...                | (and so on for all world files in JSON format)                              | JSON        |

### France Data

Official geographical data for France, located in `france-csv/` and `france-json/`.

| File Name              | Description                                                               | Format      |
| ---------------------- | ------------------------------------------------------------------------- | ----------- |
| `regions.json`         | A list of all French regions, including overseas territories.             | JSON        |
| `departements.json`    | All French departments, linked to their respective regions.               | JSON        |
| `communes.json`        | A detailed list of all French communes (municipalities).                  | JSON        |
| `codes-postaux.json`   | French postal codes linked to communes.                                   | JSON        |
| `regions.csv`          | CSV version of the regions dataset.                                       | CSV         |
| ...                    | (and so on for all France files in CSV format)                            | CSV         |

## Data Sources

*   **French Geographical Data:** [data.gouv.fr](https://www.data.gouv.fr/), the official French open data platform.
*   **World Cities, States, and Countries:** Sourced from multiple open datasets, including one from mexwell on Kaggle.
*   **Countries:** Sourced from Google's public repositories.

Some datasets have been enriched using the [OpenStreetMap Nominatim API](https://nominatim.openstreetmap.org/).

## Contributing

 If you find an error, have a suggestion, or want to add a new dataset, please open an issue or submit a pull request.
