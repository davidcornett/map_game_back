from array import array
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
from better_profanity import profanity

county_adjacencies = [] # array of linked lists

# global var: TBD replace with DB calls
player_country = None

# Configuration
load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

def init_app():
    adjacency() # load county adjacencies
    
# Routes 
@app.route('/')
def root():
    return "not implemented"

@app.route('/get_ids')
def get_ids() -> array:
    # serves list of all county IDs in user's country
    return jsonify([x.get_id() for x in player_country.get_counties()])

@app.route('/get_area/<id>')
def get_area(id) -> str:
    # serves area of county with given ID
    c = County(str(id))
    return jsonify(c.get_area())

@app.route('/get_pop/<id>')
def get_pop(id) -> str:
    # serves population of county with given ID
    c = County(str(id))
    return jsonify(c.get_pop())

def process_countyID(id: str) -> list:
    # returns list of character groups in county ID

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

def createCountry(county_ids: list, name: str, creator: str) -> object:
    # returns Country, comprised of Counties

    county_list = [County(id) for id in county_ids] # create list of County objects from list of county IDs
    return Country(county_list, name, creator)

def adjacency():

    # populate global 
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
    # returns tuple of validity status for new country and error message

    # CHECK 1: AREA
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


def adj_binary_search(id: int):
    # binary search for adjacent counties of a given county id, for ids in asencding order
    
    # get lowest and highest county id from global array of arrays 
    low = 0
    high = len(county_adjacencies)
    
    while True:

        mid = (low + high)//2
        mid_item = int(county_adjacencies[mid][0])
        
        if id == mid_item:
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
    # primary endpoint for creating a new country

    data = request.get_json()
    selected_county_ids = data.get('selected_county_ids', [])

    max_area = data.get('maxArea', 100000)
    global player_country
    name = data.get('countryName', 'Unknown') 
    creator = data.get('displayName', 'Anonymous')

    # profanity checks
    if profanity.contains_profanity(name):
        name = 'Unknown'
    if profanity.contains_profanity(creator):
        creator = 'Anonymous'

    player_country = createCountry(selected_county_ids, name, creator)

    # check that country is contigious and within allowed area range
    is_valid_country, error_message = check_validity(player_country, max_area)

    if not is_valid_country:
        return jsonify({"error": error_message}), 400
    else:

        # ALL MODES - set relevant items
        player_country.set_pop()
        player_country.set_races()
        player_country.set_unemployment_rate()
        player_country.set_per_capita_income()
        player_country.set_gdp()

        # CHALLENGE MODE - set items
        if data['challenge']:
            player_country.set_challenge_score(data['statKey'])
            submit_score(data, player_country.get_challenge_score())

        # SANDBOX MODE - set items
        else:
            player_country.set_land_cover()
            player_country.set_similar_countries()

        # enable map to only show user's counties
        filtered_geojson = filter_geojson_by_counties(selected_county_ids)
    
        # structure response to send 
        response_data = {
            "geojson": filtered_geojson, 
            "stats": {
                "name": player_country.get_name(),
                "creator": player_country.get_creator(),
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
                "challengeScore": player_country.get_challenge_score() or "N/A",
                "landCover": player_country.get_land_cover() or "N/A",
                "similarCountries": player_country.get_similar_countries() or "N/A"
            }
        }

        return response_data, 200


def filter_geojson_by_counties(selected_county_ids):
    # returns geojson with only selected counties

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
    # serves json of all challenges

    try:
        challenges = get_all_challenges()  # Fetch challenges from the database
        return jsonify(challenges), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # serves leaderboard specific to user's challenge

    challenge_name = request.args.get('name', default=None, type=str)
    max_area = request.args.get('maxArea', default=None, type=int)

    if not challenge_name or max_area is None:
        # Early return if required parameters are missing
        return jsonify({'error': 'Missing required parameters: name and maxArea'}), 400

    # Prepare the query with JOIN and WHERE clauses for filtering
    query = """
        SELECT s.display_name, s.score, s.country_name, s.completion_date FROM scores s
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
    # submit challenge score to DB

    display_name = data.get('displayName', 'Anonymous')  # Default to 'Anonymous' if not provided
    country_name = data.get('countryName', 'Unknown')  # Default to 'Unknown' if not provided
    challenge_id = get_challenge_id(data['challenge'], data['maxArea'])
    
    # Generate a UUID for the session
    session_id = str(uuid.uuid4())
    
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO scores (session_id, display_name, challenge_id, score, country_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, display_name, challenge_id, score, country_name))
    except Exception as e:
    # Handle any errors that occur during insert
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Score submitted successfully"}), 201

def get_challenge_id(challenge_data: dict, area: int) -> int:
    # looks up and returns challenge ID based on the selected challenge criteria and max area

    criteria_type = challenge_data['criteria']['criteria_type']
    goal_direction = challenge_data['criteria']['goal_direction']
    description = challenge_data['description']
    name = challenge_data['name']

    id_query = """
        SELECT challenge_id 
        FROM challenges
        WHERE criteria->>'criteria_type' = %s
            AND criteria->>'goal_direction' = %s
            AND description = %s
            AND name = %s
            AND max_area = %s;
        """
    
    with get_db_cursor() as cur:
        cur.execute(id_query, (criteria_type, goal_direction, description, name, area))
        challenge_id = cur.fetchone()[0]
    return challenge_id

@app.route('/wake_neon', methods=['GET'])
def wake_neon():    
    wake_query = """
        SELECT 1;
        """
    with get_db_cursor() as cur:
        cur.execute(wake_query)
        return jsonify({"message": "Neon database is awake"}), 200
    
@app.route('/wake_render', methods=['GET'])
def wake():
    return jsonify({"message": "Hello world!"})

@app.route('/get_national_parks', methods=['POST'])
def get_national_parks():
    data = request.get_json()
    selected_county_ids = data.get('selected_county_ids', [])

    # get list of park codes that intersect with selected counties
    park_codes = get_parks(selected_county_ids)
    
    # If no parks are found inside the country, return an empty list
    if not park_codes:
        return jsonify({'data': [], 'message': 'No matching national parks found'}), 200

    # Format list for use in API query
    park_codes_string = ','.join(set(park_codes))

    api_key = os.getenv('NPS_API_KEY')  # Load API key from environment variables
    try:
        nps_url = f'https://developer.nps.gov/api/v1/parks?parkCode={park_codes_string}&api_key={api_key}'
        response = requests.get(nps_url)
        if response.status_code == 200:
            parks_data = response.json().get('data', [])
            return jsonify({'data': parks_data, 'message': 'Parks data fetched successfully'})
        else:
            return jsonify({'data': [], 'message': 'Failed to fetch data from NPS API'}), response.status_code
    except Exception as e:
        return jsonify({'data': [], 'message': str(e)}), 500

def get_parks(county_ids: list) -> list:
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                    SELECT DISTINCT np.name, np.unit_code
                    FROM national_parks np
                    JOIN county_coords cc ON ST_Intersects(np.geom, cc.geom)
                    WHERE cc.geoid = ANY(%s)
                    AND np.unit_type IN ('National Monument', 'National Park');
                """, (county_ids,))
                
            national_parks = cur.fetchall()

            # account for Sequoia and Kings Canyon which are merged by NPS
            park_code_overrides = {
                'KICA': 'SEKI',
                'SEQU': 'SEKI'
            }

            # Get list of all matched park codes, accounting for any overrides
            park_codes = [park_code_overrides.get(code[1], code[1]) for code in national_parks]
  
            return park_codes
        
    except Exception as e:
        print(e)
        return jsonify({'error': 'Unable to process the request'}), 500

init_app() # set up county adjacencies data structure

# Listener
if __name__ == "__main__":
    # bind to PORT if defined, otherwise use default
    port = int(os.environ.get('PORT', 6205))
    app.run(port=port) 
