import csv

input_file_path = 'counties_years_data.csv'  # Update to your problematic CSV file path
output_file_path = 'county_year.csv'  # Output file path

def format_county_id(county_id):
    """Ensure the countyID is 5 digits long, prepending zeros if necessary."""
    return county_id.zfill(5)

with open(input_file_path, mode='r', newline='', encoding='utf-8-sig') as infile, \
     open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        if 'countyID' in row:
            row['countyID'] = format_county_id(row['countyID'])
            writer.writerow(row)
        else:
            print("Warning: 'countyID' not found in row")

print(f"Updated CSV has been saved to {output_file_path}")
