import psycopg2
from psycopg2 import sql

# Configuration
con = psycopg2.connect(dbname='mapgame', user='davidcornett', host='localhost')
cur = con.cursor()

class County:
    def __init__(self, id: str):
        self._id = id
        self._pop = self.set_pop()
        self._name = self.set_name()
        self._racial_breakdown = None
        self._unemployment_rate = None
        #self._poverty_rate = None
        self._per_capita_income = None
        self._gdp = None
        con.commit()

    def get_id(self) -> str:
        return self._id

    def get_pop(self) -> int:
        return self._pop

    def get_name(self) -> str:
        return self._name

    def set_name(self) -> str:
        name_query = """ SELECT countyName FROM counties WHERE countyID =%s;"""
        cur.execute(name_query, [self._id])
        return cur.fetchone()[0]

    def set_pop(self) -> int:
        pop_query = """
                SELECT total_pop FROM countyid_year
                WHERE year=2021 AND countyID=%s;
                """
        
        cur.execute(pop_query, [self._id])
        return cur.fetchone()[0]

    def set_unemployment_rate(self) -> float:
        unemployment_query = """
                SELECT unemployment_rate FROM countyid_year
                WHERE year=2019 AND countyID=%s;
                """
        
        cur.execute(unemployment_query, [self._id])
        self._unemployment_rate = cur.fetchone()[0]
        #return cur.fetchone()[0]
    
    def get_unemployment_rate(self) -> float:
        return self._unemployment_rate

    def set_poverty_rate(self) -> float:
        poverty_query = """
                SELECT poverty_rate FROM countyid_year
                WHERE year=2019 AND countyID=%s;
                """
        
        cur.execute(poverty_query, [self._id])
        return cur.fetchone()[0]
    
    def set_per_capita_income(self) -> int:
        income_query = """
                SELECT per_capita_income FROM countyid_year
                WHERE year=2019 AND countyID=%s;
                """
        
        cur.execute(income_query, [self._id])
        self._per_capita_income = cur.fetchone()[0]

    def get_per_capita_income(self) -> int:
        return self._per_capita_income
    

    def set_gdp(self) -> int:
        gdp_query = """
                SELECT gdp FROM countyid_year
                WHERE year=2022 AND countyID=%s;
                """
        
        cur.execute(gdp_query, [self._id])
        self._gdp = cur.fetchone()[0] * 1000 # convert SQL data, stored in in 1000s

    def get_gdp(self) -> int:
        return self._gdp

    def set_races(self) -> None:
        races = ['black', 'native', 'asian', 'pac_isl', 'two_plus_races', 'hispanic', 'white_not_hispanic']
        
        query_syntax = """
                SELECT {} FROM countyid_year
                WHERE year=2021 AND countyID=%s;
                """
        
        query = sql.SQL(query_syntax).format(sql.SQL(", ").join(map(sql.Identifier, races)))
        cur.execute(query, [self._id])
        query_result = cur.fetchall()[0]
        d = {}
        for i in range(len(races)):
            d[races[i]] = query_result[i]

        self._racial_breakdown = d

    def get_area(self) -> float:
        area_query = """ SELECT size from counties WHERE countyID =%s;"""
        cur.execute(area_query, [self._id])
        return cur.fetchone()[0]
    
    
