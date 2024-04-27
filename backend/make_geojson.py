import psycopg2
import json

# Database connection parameters
dbname = "mapgame"
user = "davidcornett"
host = "localhost"

# Connect to your PostgreSQL database
conn = psycopg2.connect(dbname=dbname, user=user, host=host)

# Open a cursor to perform database operations
cur = conn.cursor()

# SQL query from above
sql_query = """
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(shape)::json,
            'properties', json_build_object(
                'id', objectid,
                'fips', state_cnty_fips,
                'county_name', cnty_name,
                'forest_land', foresland_acres,
                'timber_land', timberland_acres

                -- Add other properties from columns as needed
            )
        )
    )
) AS geojson
FROM forest_cover;
"""

# Execute the query
cur.execute(sql_query)

# Fetch the result
result = cur.fetchone()[0]

# Save the result to a GeoJSON file
with open('forest_cover.geojson', 'w') as outfile:
    json.dump(result, outfile, indent=2)

# Close communication with the database
cur.close()
conn.close()

print("GeoJSON file has been created: output.geojson")
