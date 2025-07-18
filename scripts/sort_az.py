#!/usr/bin/env python3
"""
Simple script to sort a CSV file alphabetically by the first column.
command: python3 sort_csv.py <csv_file>
"""

import sys
import csv

def sort_csv(csv_file):
    """Sort a CSV file alphabetically by the first column."""
    try:
        rows = []
        
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    rows.append(row)
        
        if not rows:
            print("CSV file is empty.")
            return
        
        # Sort by first column (case-insensitive)
        header = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # Sort data rows alphabetically by first column
        sorted_data = sorted(data_rows, key=lambda row: row[0].lower() if row[0] else '')
        
        # Combine header with sorted data
        sorted_rows = [header] + sorted_data if header else sorted_data
        
        # Write back to the same file
        with open(csv_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(sorted_rows)
        
        print(f"Successfully sorted {len(data_rows)} rows alphabetically by first column.")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 sort_csv.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    sort_csv(csv_file) 