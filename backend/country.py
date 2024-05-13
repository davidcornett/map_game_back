import csv
from collections import defaultdict
from psycopg2 import sql
from db import get_db_cursor

county_adjacencies = [] # array of linked lists

class Country:
    def __init__(self, counties: list, name: str, creator: str):
        self._counties = counties
        self._id_placeholder = ', '.join(['%s'] * len(self._counties))
        self._county_ids = [county.get_id() for county in self._counties]
        self._name = name
        self._creator = creator
        #self._area = sum(county.get_area() for county in self._counties)
        self._area = 24000
        #self._pop = sum(county.get_pop() for county in self._counties)
        self._pop = None
        self._racial_breakdown = None
        self._unemployment_rate = None
        self._per_capita_income = None
        self._gdp = None
        self._challenge = None
        self._challenge_score = None
        self._land_cover = {}
        self._similar_countries = [] # list of dict objects
    
    def get_counties(self):
        return self._counties
    
    def get_name(self) -> str:
        return self._name
    
    def get_creator(self) -> str:
        return self._creator
    
    def set_pop(self):
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
    
    def get_area(self) -> float:
        return self._area

    def check_validity(self):
        pass


    def set_races(self):
        races = ['black', 'native', 'asian', 'pac_isl', 'two_plus_races', 'hispanic', 'white_not_hispanic']
        racial_breakdown = defaultdict(int)
        for i in range(len(self._counties)):
            self._counties[i].set_races()
            for j in range(len(races)):
                racial_breakdown[races[j]] += self._counties[i]._racial_breakdown[races[j]]

        self._racial_breakdown = racial_breakdown
    
    def get_racial_percentage(self, race: str) -> float:
        return self._racial_breakdown[race]/self._pop
    
    def set_unemployment_rate(self):
        for i in range(len(self._counties)):
            self._counties[i].set_unemployment_rate()
        
        wt_unemployment_total = sum(county.get_unemployment_rate() * county.get_pop() for county in self.get_counties())
        self._unemployment_rate = round(wt_unemployment_total / self.get_pop(),2)
    
    def get_unemployment_rate(self) -> float:
        return self._unemployment_rate
    
    def set_per_capita_income(self):
        for i in range(len(self._counties)):
            self._counties[i].set_per_capita_income()
        
        wt_income_total = sum(county.get_per_capita_income() * county.get_pop() for county in self.get_counties())
        self._per_capita_income = round(wt_income_total / self.get_pop(),0)

    def get_per_capita_income(self) -> int:
        return self._per_capita_income
    
    def set_gdp(self):
        for i in range(len(self._counties)):
            self._counties[i].set_gdp()
        
        self._gdp = sum(county.get_gdp() for county in self.get_counties())

    def get_gdp(self) -> int:
        return self._gdp
    
    def set_challenge(self, challenge):
        self._challenge = challenge

    def set_challenge_score(self, key: str):
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
        for i in range(len(self._counties)):
            self._counties[i].set_land_cover()
            for key in self._counties[i]._land_cover.keys():
                
                if key in self._land_cover:
                    self._land_cover[key] += self._counties[i]._land_cover[key]
                else:
                    self._land_cover[key] = self._counties[i]._land_cover[key]
            #print(self._land_cover)

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
            print(result_dicts)
            self._similar_countries = result_dicts
    
    def get_similar_countries(self) -> list:
        return self._similar_countries


