#!/usr/bin/env python3
"""
Simple script to check for duplicate names in the first column of a CSV file.
command: python3 check_duplicates.py <csv_file>
"""

import sys
import csv
from collections import Counter

def check_duplicates(csv_file):
    """Check for duplicate names in the first column of a CSV file."""
    try:
        names = []
        
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    names.append(row[0].strip())  # First column
        
        # Count occurrences of each name
        name_counts = Counter(names)
        
        # Find duplicates
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate name(s):")
            for name, count in duplicates.items():
                print(f"  '{name}' appears {count} times")
        else:
            print("No duplicate names found.")
            
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 check_duplicates.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    check_duplicates(csv_file) 