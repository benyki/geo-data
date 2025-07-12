import csv
import json

def calculate_average_coordinates(csv_file):
    """
    Reads a CSV file with department coordinates and calculates the average lat/lon.

    Args:
        csv_file (str): The path to the input CSV file.

    Returns:
        dict: A dictionary mapping department codes to their average coordinates.
    """
    coordinates = {}
    with open(csv_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                dept_code = row['Departement']
                lat_nord = float(row['Latitude la plus au nord'])
                lat_sud = float(row['Latitude la plus au sud'])
                lon_est = float(row['Longitude la plus à l’est'])
                lon_ouest = float(row['Longitude la plus à l’ouest'])

                avg_lat = (lat_nord + lat_sud) / 2
                avg_lon = (lon_est + lon_ouest) / 2
                
                # Standardize department codes (e.g., '01', '2A')
                if len(dept_code) == 1:
                    dept_code = f"0{dept_code}"

                coordinates[dept_code] = {
                    "latitude": round(avg_lat, 6),
                    "longitude": round(avg_lon, 6)
                }
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e} - Row: {row}")
    return coordinates

def add_coordinates_to_departements(json_file, coordinates):
    """
    Adds latitude and longitude to a JSON file of French departments.

    Args:
        json_file (str): The path to the departments JSON file.
        coordinates (dict): A dictionary with department codes and their coordinates.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        departements_data = json.load(f)

    for departement in departements_data:
        dept_code = departement.get('code')
        if dept_code in coordinates:
            departement['latitude'] = coordinates[dept_code]['latitude']
            departement['longitude'] = coordinates[dept_code]['longitude']

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(departements_data, f, indent=4, ensure_ascii=False)
    print(f"Successfully updated {json_file} with new coordinates.")


if __name__ == "__main__":
    CSV_COORDINATES_FILE = 'departements-coordinates.csv'
    DEPARTEMENTS_JSON_FILE = 'France-geo-officiel/departements.json'
    
    # Step 1: Calculate average coordinates from the CSV
    avg_coords = calculate_average_coordinates(CSV_COORDINATES_FILE)
    
    # Step 2: Add these coordinates to the main JSON file
    add_coordinates_to_departements(DEPARTEMENTS_JSON_FILE, avg_coords) 