from db import get_db_cursor

class Country:
    # object to store data for a user-created country
    def __init__(self, counties: list, name: str, creator: str):
        self._counties = counties
        self._id_placeholder = ', '.join(['%s'] * len(self._counties))
        self._county_ids = [county.get_id() for county in self._counties]
        self._name = name
        self._creator = creator
        self._area = self.set_area()
        self._pop = None
        self._racial_breakdown = None
        self._unemployment_rate = None
        self._per_capita_income = None
        self._gdp = None
        self._challenge = None
        self._challenge_score = None
        self._land_cover = {} # dict holds square miles of land cover by category
        self._similar_countries = [] # list of dict objects
    
    def get_counties(self):
        return self._counties
    
    def get_name(self) -> str:
        return self._name
    
    def get_creator(self) -> str:
        return self._creator
    
    def set_pop(self):
        # setter for country population
        pop_query = f"""
            SELECT SUM(total_pop) AS total_population
            FROM countyid_year
            WHERE year = 2021 AND countyID IN ({self._id_placeholder});
        """

        with get_db_cursor() as cur:
            cur.execute(pop_query, self._county_ids)
            self._pop = cur.fetchone()[0]

    def get_pop(self) -> int:
        return self._pop
    
    def set_area(self):
        # setter for country area
        area_query = f"""
            SELECT SUM(size) AS total_area
            FROM counties
            WHERE countyID IN ({self._id_placeholder});
        """
        with get_db_cursor() as cur:
            cur.execute(area_query, self._county_ids)
            return cur.fetchone()[0]
    
    def get_area(self) -> float:
        return self._area

    def set_races(self):
        # setter for racial breakdown of country
        races = ['black', 'native', 'asian', 'pac_isl', 'two_plus_races', 'hispanic', 'white_not_hispanic']
        race_columns = ', '.join([f"SUM({race}) AS total_{race}" for race in races])
        
        race_query = f"""
            SELECT {race_columns}
            FROM countyid_year
            WHERE year = 2021 AND countyID IN ({self._id_placeholder});
        """
        with get_db_cursor() as cur:
            cur.execute(race_query, self._county_ids)  # Execute the query with the county IDs safely passed as parameters
            result = cur.fetchone()
        racial_breakdown = {f"{races[i]}": result[i] for i in range(len(races))}
        self._racial_breakdown = racial_breakdown
    
    def get_racial_percentage(self, race: str) -> float:
        return self._racial_breakdown[race]/self._pop
    
    def set_unemployment_rate(self):
        # setter for country unemployment rate

        # query joins due to different years for pop vs unemployment data
        unemployment_query = f"""
        SELECT SUM(b.unemployment_rate * a.total_pop) / SUM(a.total_pop) AS weighted_unemployment_rate
        FROM countyid_year AS a  -- Population data for 2021
        JOIN countyid_year AS b  -- Unemployment data for 2019
        ON a.countyID = b.countyID
        WHERE 
            a.year = 2021 AND 
            b.year = 2019 AND 
            a.countyID IN ({self._id_placeholder});    
        """

        with get_db_cursor() as cur:
            cur.execute(unemployment_query, self._county_ids)
            self._unemployment_rate = round(cur.fetchone()[0], 2)
    
    def get_unemployment_rate(self) -> float:
        return self._unemployment_rate
    
    def set_per_capita_income(self):
        # setter for country per capita income

        # query joins due to different years for pop vs per capita income data
        per_cap_query = f"""
        SELECT SUM(CAST(b.per_capita_income AS BIGINT) * CAST(a.total_pop AS BIGINT)) / SUM(a.total_pop) AS weighted_per_capita_income
        FROM countyid_year AS a  -- Population data for 2021
        JOIN countyid_year AS b  -- Unemployment data for 2019
        ON a.countyID = b.countyID
        WHERE 
            a.year = 2021 AND 
            b.year = 2019 AND 
            a.countyID IN ({self._id_placeholder});    
        """

        with get_db_cursor() as cur:
            cur.execute(per_cap_query, self._county_ids)
            self._per_capita_income = int(cur.fetchone()[0])


    def get_per_capita_income(self) -> int:
        return self._per_capita_income
    
    def set_gdp(self):
        # setter for country GDP

        gdp_query = f"""
            SELECT sum(gdp) as total_gdp
            FROM countyid_year
            WHERE year=2022 
            AND countyID IN ({self._id_placeholder});
            """

        with get_db_cursor() as cur:
            cur.execute(gdp_query, self._county_ids)
            self._gdp = cur.fetchone()[0] * 1000 # convert SQL data, stored in in 1000s
        
    def get_gdp(self) -> int:
        return self._gdp

    def set_challenge_score(self, key: str):
        # setter for challenge score

        # Match the provided key to the corresponding attribute
        if key == 'total_population':
            self._challenge_score = self.get_pop()
        elif key == 'gdp':
            self._challenge_score = self.get_gdp()
        else:
            return None

    def get_challenge_score(self) -> int:
        return self._challenge_score
    
    def set_land_cover(self):
        # setter for country land cover (forest, developed, etc)

        lc_query = f"""
            SELECT lcc.category, SUM(clc.square_miles) AS total_square_miles
            FROM county_land_cover clc
            JOIN land_cover_codes lcc ON clc.land_cover_code = lcc.land_cover_code
            WHERE clc.county_id IN ({self._id_placeholder})
            GROUP BY lcc.category;
        """

        with get_db_cursor() as cur:
            cur.execute(lc_query, self._county_ids)
            results = cur.fetchall()
        
        # Process results to aggregate land cover by category
        for category, total_square_miles in results:
            self._land_cover[category] = total_square_miles

    def get_land_cover(self) -> dict:
        return self._land_cover
    
    def set_similar_countries(self):
        # sets user country's global population rank and the immediate 2 larger and 2 smaller countries

        query = """
            WITH input_population AS (
            SELECT %s::BIGINT AS population, %s::VARCHAR AS country
            ),
            immediate_larger AS (
            SELECT rank, country, population
            FROM global_pop_ranks
            WHERE population > (SELECT population FROM input_population)
            ORDER BY population ASC
            LIMIT 2
            ),
            immediate_smaller AS (
            SELECT rank, country, population
            FROM global_pop_ranks
            WHERE population < (SELECT population FROM input_population)
            ORDER BY population DESC
            LIMIT 2
            )
            SELECT * FROM (
            SELECT rank, country, population FROM immediate_larger
            UNION ALL
            SELECT NULL AS rank, (SELECT country FROM input_population), (SELECT population FROM input_population)
            UNION ALL
            SELECT rank, country, population FROM immediate_smaller
            ) AS combined_results
            ORDER BY population DESC
        """

        with get_db_cursor() as cur:
            cur.execute(query, (self._pop, self._name))
            results = cur.fetchall()
            result_dicts = [
            {'rank': r, 'country': c, 'population': p}
            for r, c, p in results
            ]
            self._similar_countries = result_dicts
    
    def get_similar_countries(self) -> list:
        return self._similar_countries


