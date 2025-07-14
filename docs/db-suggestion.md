# Database Schemas Suggestions

This document lists a suggested database schema and data structures available, presented in a clear and structured format to ensure they are easily understandable by both humans and AI systems. Each table and field is described to facilitate integration with AI-driven workflows.

---

## 🌍 World Database (`world_geo`)

This database will be built from the high-quality, relational dataset (`150k cities...`) and augmented with population data.

### `countries`
- **Description**: The primary table for world countries.
- **Columns**:
  - `id` (INTEGER, Primary Key)
  - `name` (TEXT, NOT NULL)
  - `iso2` (TEXT, UNIQUE)
  - `iso3` (TEXT, UNIQUE)
  - `phone_code` (TEXT)
  - `capital` (TEXT)
  - `currency` (TEXT)
  - `currency_name` (TEXT)
  - `region` (TEXT)
  - `subregion` (TEXT)
  - `timezones` (JSONB)
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)

### `states`
- **Description**: States, provinces, and other first-level administrative divisions.
- **Columns**:
  - `id` (INTEGER, Primary Key)
  - `name` (TEXT, NOT NULL)
  - `country_id` (INTEGER, NOT NULL, Foreign Key -> `countries.id`)
  - `state_code` (TEXT)
  - `type` (TEXT)
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)

### `cities`
- **Description**: A unified table of world cities.
- **Columns**:
  - `id` (INTEGER, Primary Key)
  - `name` (TEXT, NOT NULL)
  - `state_id` (INTEGER, NOT NULL, Foreign Key -> `states.id`)
  - `country_id` (INTEGER, NOT NULL, Foreign Key -> `countries.id`)
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)
  - `wikidata_id` (TEXT)
  - `population_2024` (BIGINT, nullable): Populated from the `major_cities_enriched.csv` file.
  - `population_2023` (BIGINT, nullable)
  - `growth_rate` (DOUBLE PRECISION, nullable)

---

## 🇫🇷 France Database (`france_geo`)

This database will use our detailed, enriched French datasets.

### `regions`
- **Description**: Stores French regions.
- **Columns**:
  - `code` (TEXT, Primary Key): INSEE region code.
  - `name` (TEXT)
  - `zone` (TEXT): e.g., "metro", "drom".
  - `chef_lieu_code` (TEXT): The INSEE code for the capital commune.
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)

### `departements`
- **Description**: Stores French departments.
- **Columns**:
  - `code` (TEXT, Primary Key): INSEE department code.
  - `name` (TEXT)
  - `region_code` (TEXT, Foreign Key -> `regions.code`)
  - `zone` (TEXT)
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)

### `communes`
- **Description**: Stores French communes (municipalities).
- **Columns**:
  - `code` (TEXT, Primary Key): INSEE commune code.
  - `name` (TEXT)
  - `departement_code` (TEXT, Foreign Key -> `departements.code`)
  - `region_code` (TEXT, Foreign Key -> `regions.code`)
  - `siren` (TEXT)
  - `population` (INTEGER)
  - `latitude` (DOUBLE PRECISION)
  - `longitude` (DOUBLE PRECISION)

### `postal_codes`
- **Description**: Stores unique postal codes and their average geographic center.
- **Columns**:
  - `code` (TEXT, Primary Key): The 5-digit postal code.
  - `routing_label` (TEXT)
  - `latitude` (DOUBLE PRECISION): *Average* latitude for the area.
  - `longitude` (DOUBLE PRECISION): *Average* longitude for the area.

### `postal_code_commune_map`
- **Description**: A mapping table for the many-to-many relationship between postal codes and communes.
- **Columns**:
  - `postal_code` (TEXT, Foreign Key -> `postal_codes.code`)
  - `commune_code` (TEXT, Foreign Key -> `communes.code`)
  - `PRIMARY KEY (postal_code, commune_code)`
