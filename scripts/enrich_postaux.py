import json
import os
from collections import defaultdict

def enrich_postaux_with_coordinates():
    """
    Enriches postal code data with an average latitude and longitude, calculated
    from all the communes associated with each postal code.
    """
    communes_path = 'France-geo-officiel/communes_enriched.json'
    postaux_path = 'France-geo-officiel/codes-postaux.json'
    output_path = 'France-geo-officiel/codes-postaux_enriched.json'

    # Check for necessary files
    if not os.path.exists(communes_path):
        print(f"Error: Enriched communes file not found at {communes_path}")
        return
    if not os.path.exists(postaux_path):
        print(f"Error: Original postal codes file not found at {postaux_path}")
        return

    # 1. Load the enriched communes data and create a coordinate map
    print(f"Loading commune coordinates from {communes_path}...")
    with open(communes_path, 'r', encoding='utf-8') as f:
        communes_data = json.load(f)
    
    coord_map = {
        commune['code']: {
            'latitude': commune.get('latitude'),
            'longitude': commune.get('longitude')
        }
        for commune in communes_data if 'latitude' in commune and 'longitude' in commune
    }
    print(f"Created a coordinate map for {len(coord_map)} communes.")

    # 2. Load the postal code data
    print(f"Loading postal code data from {postaux_path}...")
    with open(postaux_path, 'r', encoding='utf-8') as f:
        postaux_data = json.load(f)

    # 3. Group communes by postal code
    print("Grouping communes by postal code...")
    postal_code_groups = defaultdict(list)
    for entry in postaux_data:
        commune_code = entry.get('codeCommune')
        postal_code = entry.get('codePostal')
        if postal_code and commune_code in coord_map:
            postal_code_groups[postal_code].append(coord_map[commune_code])
    
    print(f"Found {len(postal_code_groups)} unique postal codes with valid communes.")

    # 4. Calculate average coordinates for each postal code
    print("Calculating average coordinates for each postal code...")
    enriched_postaux_data = []
    for code, coords_list in postal_code_groups.items():
        if not coords_list:
            continue
        
        avg_lat = sum(c['latitude'] for c in coords_list) / len(coords_list)
        avg_lon = sum(c['longitude'] for c in coords_list) / len(coords_list)
        
        # We can take the routing label from the first commune, as it's generally consistent.
        # A more robust solution could verify this, but this is a good approximation.
        original_entry = next((p for p in postaux_data if p['codePostal'] == code), None)
        libelle = original_entry['libelleAcheminement'] if original_entry else ''

        enriched_postaux_data.append({
            "codePostal": code,
            "libelleAcheminement": libelle,
            "latitude": avg_lat,
            "longitude": avg_lon,
            "communesCount": len(coords_list)
        })

    # 5. Save the new enriched data
    print(f"Saving enriched postal code data to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_postaux_data, f, ensure_ascii=False, indent=2)

    print("Postal code enrichment complete! New file created.")

if __name__ == '__main__':
    enrich_postaux_with_coordinates() 