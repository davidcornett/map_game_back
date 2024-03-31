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


# Add more functions as necessary for your database operations
