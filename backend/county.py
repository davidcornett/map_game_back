from db import get_db_cursor

class County:
    def __init__(self, id: str):
        self._id = id

    def get_id(self) -> str:
        return self._id

    def get_area(self) -> float:
        area_query = """ SELECT size from counties WHERE countyID =%s;"""
        with get_db_cursor() as cur:
            cur.execute(area_query, [self._id])
            return cur.fetchone()[0]
    
    def get_pop(self) -> int:
        pop_query = """ SELECT total_pop from countyid_year WHERE year = 2021 AND countyID = %s;"""
        with get_db_cursor() as cur:
            cur.execute(pop_query, [self._id])
            return cur.fetchone()[0]