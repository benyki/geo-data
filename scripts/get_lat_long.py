#!/usr/bin/env python3
"""
Simple script to enrich CSV files with coordinates using OpenStreetMap API.
"""

import csv
import requests
import time

# ===== CONFIGURATION =====
INPUT_FILE = 'world-csv/major_cities.csv'  # Change this to your input CSV
OUTPUT_FILE = 'world-csv/major_cities_enriched.csv'  # Change this to your output CSV
API_DELAY = 1  # Delay between API calls (seconds)
CITY_COLUMN = 'City'  # Don't touch if your CSV has a column named 'City'
COUNTRY_COLUMN = 'Country'  # Don't touch if your CSV has a column named 'Coutnry'
# ========================

def get_coordinates(city, country):
    """Get coordinates for a city using OpenStreetMap API."""
    url = f"https://nominatim.openstreetmap.org/search?city={city}&country={country}&format=json"
    headers = {'User-Agent': 'GeoData-Enrichment-Script/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
    except Exception as e:
        print(f"Error getting coordinates for {city}, {country}: {e}")
    
    time.sleep(API_DELAY)
    return None

def enrich_csv():
    """Enrich CSV file with coordinates."""
    try:
        # Read input file
        with open(INPUT_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        print(f"Processing {len(rows)} rows from {INPUT_FILE}...")
        
        # Process each row
        for i, row in enumerate(rows, 1):
            city = row.get(CITY_COLUMN, '').strip()
            country = row.get(COUNTRY_COLUMN, '').strip()
            
            if not city or not country:
                print(f"Row {i}: Missing city or country data")
                continue
            
            print(f"Row {i}/{len(rows)}: {city}, {country}")
            coords = get_coordinates(city, country)
            
            if coords:
                row['latitude'] = coords['latitude']
                row['longitude'] = coords['longitude']
                print(f"  ✓ Found coordinates: {coords['latitude']}, {coords['longitude']}")
            else:
                row['latitude'] = ''
                row['longitude'] = ''
                print(f"  ✗ No coordinates found")
        
        # Write output file
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as file:
            if rows:
                writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"\n✓ Enrichment complete! Output saved to {OUTPUT_FILE}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    enrich_csv() 