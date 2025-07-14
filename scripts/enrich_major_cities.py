import csv
import os
import requests
import time

def get_coords_from_api(city_name, country_name):
    """
    Uses the OpenStreetMap Nominatim API to get coordinates for a city.
    """
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&country={country_name}&format=json"
    headers = {'User-Agent': 'GeoData-Enrichment-Script/1.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f"    API Success for '{city_name}, {country_name}': Found lat={lat}, lon={lon}")
            return {"latitude": lat, "longitude": lon}
    except requests.exceptions.RequestException as e:
        print(f"    API Error for '{city_name}, {country_name}': {e}")
    except (IndexError, KeyError) as e:
        print(f"    API Warning for '{city_name}, {country_name}': Could not parse response. {e}")
    
    time.sleep(1) # Be polite to the API
    return None

def enrich_major_cities():
    """
    Enriches the major_cities.csv file with latitude and longitude data
    from the Nominatim API and cleans up column names.
    """
    input_path = 'major_cities.csv'
    output_path = 'major_cities_enriched.csv'

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return

    enriched_cities = []
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            city_name = row.get('City')
            country_name = row.get('Country')

            if not city_name or not country_name:
                continue

            print(f"-> Processing '{city_name}, {country_name}'...")
            coords = get_coords_from_api(city_name, country_name)

            # Clean up the row and add new data
            new_row = {
                'city': city_name,
                'country': country_name,
                'population_2024': row.get('Population (2024)'),
                'population_2023': row.get('Population (2023)'),
                'growth_rate': row.get('Growth Rate')
            }
            
            if coords:
                new_row['latitude'] = coords['latitude']
                new_row['longitude'] = coords['longitude']
            else:
                new_row['latitude'] = None
                new_row['longitude'] = None
                print(f"   - Failed to find coordinates for '{city_name}, {country_name}'.")

            enriched_cities.append(new_row)

    # Save the enriched data
    if not enriched_cities:
        print("No cities were processed. Exiting.")
        return

    print(f"\nSaving {len(enriched_cities)} enriched cities to {output_path}...")
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = enriched_cities[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_cities)

    print("Major cities enrichment complete! New file created.")


if __name__ == '__main__':
    enrich_major_cities() 