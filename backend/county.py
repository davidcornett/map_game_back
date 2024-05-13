import psycopg2
from psycopg2 import sql
from db import get_db_cursor

class County:
    def __init__(self, id: str):
        self._id = id
        #self._name = self.set_name()
        self._name = "flanders"
        self._land_cover = {}

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def set_name(self) -> str:
        name_query = """ SELECT countyName FROM counties WHERE countyID =%s;"""
        with get_db_cursor() as cur:
            cur.execute(name_query, (self._id,))
            return cur.fetchone()[0]

    def get_area(self) -> float:
        area_query = """ SELECT size from counties WHERE countyID =%s;"""
        with get_db_cursor() as cur:
            cur.execute(area_query, [self._id])
            return cur.fetchone()[0]
    
    def set_land_cover(self) -> None:
        lc_query = """
                SELECT square_miles, land_cover_code
                FROM county_land_cover
                WHERE county_id = %s;
                """
        
        description_query = """
                SELECT land_cover_code, category
                FROM land_cover_codes;
                """


        with get_db_cursor() as cur:
            # Fetch square miles and land cover codes
            cur.execute(lc_query, [self._id])
            county_data = cur.fetchall()
            
            # Fetch land cover descriptions
            cur.execute(description_query)
            categories = cur.fetchall()
            
            # Convert descriptions to a dictionary
            category_dict = {code: cat for code, cat in categories}
            
            # Create the final dictionary mapping square miles to descriptions
            for square_miles, land_cover_code in county_data:
                if land_cover_code in category_dict:
                    category = category_dict[land_cover_code]
                if category in self._land_cover:
                    self._land_cover[category] += square_miles  # Add to existing square miles
                else:
                    self._land_cover[category] = square_miles 
