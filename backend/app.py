from array import array
from ast import Str
from flask import Flask, render_template, request, flash, jsonify
from flask_cors import CORS
import os
from county import County
from country import Country
import csv
import geojson
import uuid
from dotenv import load_dotenv
import requests
from db import get_all_challenges 
from db import get_db_cursor

#from svg.path import parse_path
#from svg.path.path import Line
from xml.dom import minidom


county_adjacencies = [] # array of linked lists

# global var: TBD replace with DB calls
player_country = None

# Configuration
load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

def main():
    adjacency()
    
    """
    for e in county_adjacencies:
        print(e)
    """
    #print(int(county_adjacencies[0][0]) + 5)

# Routes 
@app.route('/')
def root():
    return "not implemented"


@app.route('/svg')
def svg():
    print("SVG")
    path_dict = {}
    doc = minidom.parse('static/usa-all-counties.svg')
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    paths = [path for path in doc.getElementsByTagName('path')]
    
    for p in paths:
        for county in player_country.get_counties():
            if p.getAttribute('id') == county.get_id():
                #print(p.getAttribute('id'))
                path_dict[p.getAttribute('id')] = {"d":p.getAttribute('d')}

    doc.unlink()

    """
    paths["id"] = "01069"
    paths["d"] = "M 409.67498,255.323 L 413.28898,254.994 L 413.17198,255.336 L 413.09598,255.67 L 413.24898,256.585 L 413.36098,256.846 L 413.45598,256.9 L 413.55098,256.9 L 413.63298,256.923 L 414.15398,257.496 L 414.23598,257.643 L 414.35498,257.9 L 414.67798,258.834 L 409.35098,259.482 L 409.26498,258.46 L 409.08798,256.882 L 408.00198,257.067 L 406.63198,257.211 L 407.02098,256.233 L 407.08298,256.179 L 407.33998,256.094 L 407.52498,256.085 L 407.69998,256.094 L 408.07398,256.183 L 408.35898,256.26 L 408.85498,256.306 L 409.02198,256.291 L 409.71998,255.692 L 409.67498,255.323"
    paths["inkscape:label"] = "Houston, AL"
    """

    return jsonify(path_dict)

    return "44"

@app.route('/get_ids')
def get_ids() -> array:
    return jsonify([x.get_id() for x in player_country.get_counties()])

@app.route('/get_area/<id>')
def get_area(id) -> str:
    c = County(str(id))
    return jsonify(c.get_area())


def create_new_map(county_ids: list, name: str) -> None:
    new_file = open("static/template.svg")
    content = new_file.read()
    print(content[0:40])
    """
    for x in county_ids:
        print("new map: %s", x)
    """
    old_file = open("static/usa-all-counties.svg.svg")
    #new_file.write("ffff") 
    new_file.close()
    old_file.close()



def process_countyID(id: str) -> list:
    output = []
    elem = ''

    for char in id:
        # character groups terminating with comma should be appended to list
        if char == ',':
            output.append(elem)
            elem = ''
        else:
            elem += char
    
    output.append(elem)  # add last character group, not terminating with comma
    return output

def createCountry(county_ids: list) -> object:
    # returns Country, comprised of Counties
    county_list = [County(id) for id in county_ids] # create list of County objects from list of county IDs
    return Country(county_list)


def build_new_map(county_ids: list) -> str:
    county_ids = ['25025', '31007', '06075']


def adjacency():
    county_counter = 0;
    with open('county_neighbors.csv') as file:
        data = list(csv.reader(file, delimiter=','))
        county_adjacencies.append(data[1])
        length = len(data)
        for i in range(2, length):
            if county_adjacencies[-1][0] == data[i][0]:
                county_adjacencies[-1].append(data[i][1])
            else:
                county_adjacencies.append(data[i])


def check_validity(country: object, max_area) -> tuple[bool, str]:
    # CHECK 1: AREA
    print(f"max_area: {max_area}")
    if country.get_area() not in range(0, max_area):
        return False, "Country area is not within allowed size range."

    # CHECK 2: ADJACENCY
    def remove_leading_zero(id):
        return id[1:] if id.startswith('0') else id

    county_ids = [remove_leading_zero(county.get_id()) for county in country.get_counties()]

    starting_node = county_ids[0]  # get a county ID from country
    
    # BFS traversal of graph - if not all counties selected are visited, country is invalid
    visited = [starting_node]
    queue = [starting_node]
    counter = 0

    while queue:
        current_node = queue.pop(0)
        counter += 1

        # get adjacent nodes of current node
        adjacent_nodes = adj_binary_search(int(current_node))

        for node in adjacent_nodes:
            if node not in visited and node in county_ids:
                visited.append(node)
                queue.append(node)

    return (True, None) if counter == len(county_ids) else (False, "The country is not contiguous.")


def adj_binary_search(id: int) -> bool:
    
    # get lowest and highest county id from global array of arrays 
    low = 0
    high = len(county_adjacencies)
    
    while True:

        mid = (low + high)//2
        mid_item = int(county_adjacencies[mid][0])
        
        if id == mid_item:
            #print("returning adjacencies: " + str(county_adjacencies[mid][1:]))
            return county_adjacencies[mid][1:]

        elif (low == high):
            break       
        elif id > mid_item:
            low = mid + 1
        else:
            high = mid - 1

    return False

@app.route('/get_new_country', methods=['POST'])
def get_new_country():
    data = request.get_json()
    selected_county_ids = data.get('selected_county_ids', [])
    print(data)
    max_area = data.get('maxArea', 100000)
    global player_country
    player_country = createCountry(selected_county_ids)
    get_parks(selected_county_ids)

    # check that country is contigious and within allowed area range
    is_valid_country, error_message = check_validity(player_country, max_area)
    #print(player_country.get_pop())

    if not is_valid_country:
        return jsonify({"error": error_message}), 400
    else:
        player_country.set_races()
        player_country.set_unemployment_rate()
        player_country.set_per_capita_income()
        player_country.set_gdp()

        if data['challenge']:
            player_country.set_challenge_score(data['statKey'])
            submit_score(data, player_country.get_challenge_score())

        filtered_geojson = filter_geojson_by_counties(selected_county_ids)
    
        response_data = {
            "geojson": filtered_geojson, 
            "stats": {
                "total_population": player_country.get_pop(), 
                "pop_black": player_country.get_racial_percentage('black'),
                "pop_native": player_country.get_racial_percentage('native'),
                "pop_asian": player_country.get_racial_percentage('asian'),
                "pop_pac_isl": player_country.get_racial_percentage('pac_isl'),
                "pop_two_plus": player_country.get_racial_percentage('two_plus_races'),
                "pop_hispanic": player_country.get_racial_percentage('hispanic'),
                "pop_white": player_country.get_racial_percentage('white_not_hispanic'),
                "perCapIncome": player_country.get_per_capita_income(),
                "unemploymentRate": player_country.get_unemployment_rate(),
                "gdp": player_country.get_gdp(),
                "challengeScore": player_country.get_challenge_score() or "N/A"
            }
        }
        return response_data, 200


def filter_geojson_by_counties(selected_county_ids):
    with open('static/counties.geojson', 'r') as file:
        data = geojson.load(file)
    
    filtered_features = [feature for feature in data['features']
                         if feature['properties']['GEOID'] in selected_county_ids]

    filtered_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    return filtered_geojson

@app.route('/challenges', methods=['GET'])
def get_challenges():
    try:
        challenges = get_all_challenges()  # Fetch challenges from the database
        return jsonify(challenges), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    challenge_name = request.args.get('name', default=None, type=str)
    max_area = request.args.get('maxArea', default=None, type=int)

    if not challenge_name or max_area is None:
        # Early return if required parameters are missing
        return jsonify({'error': 'Missing required parameters: name and maxArea'}), 400

    # Prepare the query with JOIN and WHERE clauses for filtering
    query = """
        SELECT s.display_name, s.score, s.completion_date FROM scores s
        JOIN challenges c ON s.challenge_id = c.challenge_id
        WHERE c.name = %s AND c.max_area = %s
        ORDER BY s.score DESC
    """
    params = (challenge_name, max_area,)

    with get_db_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

        # Construct a list of dictionaries for each row in the query result
        leaderboard_entries = [
            dict(zip([desc[0] for desc in cur.description], row))
            for row in rows
        ]
    return jsonify(leaderboard_entries)

def submit_score(data: dict, score: int):
    displayName = data.get('displayName', 'Anonymous')  # Default to 'Anonymous' if not provided
    challenge_id = data['challenge']['challenge_id']
    
    # Generate a UUID for the session
    session_id = str(uuid.uuid4())

    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO scores (session_id, display_name, challenge_id, score)
                VALUES (%s, %s, %s, %s)
            """, (session_id, displayName, challenge_id, score))
    except Exception as e:
    # Handle any errors that occur during insert
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Score submitted successfully"}), 201


@app.route('/get_national_parks', methods=['GET'])
def get_national_parks():
    park_codes = 'cong,yose,lavo'
    api_key = os.getenv('NPS_API_KEY')  # Load API key from environment variables

    try:
        nps_url = f'https://developer.nps.gov/api/v1/parks?parkCode={park_codes}&api_key={api_key}'
        response = requests.get(nps_url)
        if response.status_code == 200:
            parks_data = response.json().get('data', [])
            print(jsonify(parks_data))
            return jsonify(parks_data)
        else:
            return jsonify({'error': 'Failed to fetch data from NPS API'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_parks(county_ids: list):
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                    SELECT DISTINCT np.name, np.unit_code
                    FROM national_parks np
                    JOIN county_coords cc ON ST_Intersects(np.geom, cc.geom)
                    WHERE cc.geoid = ANY(%s);
                """, (county_ids,))
                
            national_parks = cur.fetchall()
            # Format the results as a list of dictionaries or another suitable format
            parks = [{'name': row[0], 'unit_code': row[1]} for row in national_parks]
            print(parks)
            return jsonify(parks)
        
    except Exception as e:
        print(e)
        return jsonify({'error': 'Unable to process the request'}), 500


# Listener
if __name__ == "__main__":
    # bind to PORT if defined, otherwise use default
    main()
    port = int(os.environ.get('PORT', 6205))
    app.run(port=port) 
