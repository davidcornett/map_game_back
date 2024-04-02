from psycopg2 import pool
from contextlib import contextmanager

# Initialize your connection pool
db_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, dbname='mapgame', user='davidcornett', host='localhost')


# Database connection parameters
db_config = {
    'dbname': 'mapgame',
    'user': 'davidcornett',
    'host': 'localhost'
}

@contextmanager
def get_db_connection():
    con = db_pool.getconn()
    try:
        # Optionally set session characteristics here, if needed
        yield con
    finally:
        db_pool.putconn(con)

@contextmanager
def get_db_cursor(commit=False):
    con = db_pool.getconn()
    try:
        cur = con.cursor()
        yield cur
        if commit:
            con.commit()
        else:
            con.rollback()
    finally:
        cur.close()
        db_pool.putconn(con)

def get_all_challenges():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM challenges WHERE active = TRUE;")
        rows = cur.fetchall()  # Get all rows as a list of tuples
        column_names = [desc[0] for desc in cur.description]  # Extract column names
        challenges_dicts = [dict(zip(column_names, row)) for row in rows]  # Create a list of dictionaries

        return challenges_dicts  # This could be returned to a Flask route for JSON serialization

