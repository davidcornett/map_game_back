import requests
import csv
import os
import time
from dotenv import load_dotenv

"""
NPS boundaries geojson come from: https://catalog.data.gov/dataset/national-park-boundaries
Problem - a few park codes don't match the NPS API
This script outputs match failures to a CSV file
Dependencies:
    NPS api key in .env
    unit_codes.csv in database folder
        to generate (from shell):
        psql -d dbname -U username -c "\COPY (SELECT unit_code FROM national_parks WHERE unit_type 
        IN ('National Monument', 'National Park')) TO 'database/unit_codes.csv' WITH CSV HEADER"
Adjust unit_codes script if you want more NPS categories (e.g. National Historic Site, Park, National Memorial, etc.)

"""

def fetch_parks(unit_codes):
    load_dotenv()
    api_key = os.getenv('NPS_API_KEY')
    discrepancies = []
    for code in unit_codes:
        url = f'https://developer.nps.gov/api/v1/parks?parkCode={code}&api_key={api_key}'
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for park code {code}: {response.status_code}")
            continue
        
        parks_response = response.json()
        print(f'code: {code} total: {parks_response["total"]}')
        #print(f'code: {code}, name: {data["fullName"]} total: {data["total"]}')
        # Check if the 'total' key is present and act accordingly
        if 'total' in parks_response and parks_response['total'] == '0':
            discrepancies.append(code)
            print(f"Park code {code} not found in the NPS API")
        elif 'total' not in parks_response:
            print(f"'total' key not found in response for {code}: {parks_response}")

        #time.sleep(1)  # Sleep to respect the API rate limit

    return discrepancies


def log_discrepancies(discrepancies):
    with open('database/discrepancies.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['unit_code'])
        for code in discrepancies:
            writer.writerow([code])

def read_unit_codes():
    unit_codes = []
    with open('database/unit_codes.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row:  # Ensure the row is not empty
                unit_codes.append(row[0])
    return unit_codes


def main():
    unit_codes = read_unit_codes()

    # Depending on the total, you may choose to only pass part of them:
    first_half = unit_codes[:len(unit_codes)//2]
    second_half = unit_codes[len(unit_codes)//2:]
    discrepancies = fetch_parks(unit_codes)  # for first half

    log_discrepancies(discrepancies)

    print("Park code validation completed.")

if __name__ == "__main__":
    main()
