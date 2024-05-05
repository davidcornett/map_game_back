import pandas as pd

# Define the data types for each column explicitly to avoid unwanted type inference
dtype_spec = {
    'county_id': str,
    'land_cover_code': str,  # Ensuring leading zeros are preserved by treating as string
    'squareMiles': str       # Initially load as string to handle the commas
}

# Load the CSV with specific data types
df = pd.read_csv('land_cover_db.csv', dtype=str)

# Remove commas from the 'squareMiles' column and convert to float
df['squareMiles'] = df['squareMiles'].apply(lambda x: float(x.replace(',', '')) if isinstance(x, str) else x)

# Save the cleaned CSV file
df.to_csv('land_cover_db_clean.csv', index=False)

