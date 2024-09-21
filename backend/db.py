import os
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
db_password = os.getenv('DB_PASSWORD')
environment = os.getenv('ENVIRONMENT')

if environment == 'development':
    db_name = os.getenv('LOCAL_DB_NAME')
    db_user = os.getenv('LOCAL_DB_USER')
    db_host = os.getenv('LOCAL_DB_HOST')
    db_sslmode = os.getenv('LOCAL_DB_SSLMODE')
else:  # Assume production environment
    db_name = os.getenv('NEON_DB_NAME')
    db_user = os.getenv('NEON_DB_USER')
    db_password = os.getenv('NEON_DB_PASSWORD')
    db_host = os.getenv('NEON_DB_HOST')
    db_sslmode = os.getenv('NEON_DB_SSLMODE')

# Initialize your connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1, 
    maxconn=10, 
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    sslmode=db_sslmode
    )


# Database connection parameters
db_config = {
    'dbname': db_name,
    'user': db_user,
    'password': db_password,
    'host': db_host,
    'sslmode': db_sslmode
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
    # return all active unique challenge types, ignoring max size
    with get_db_cursor() as cur:
        challenge_query = """
            SELECT DISTINCT name, description, criteria
            FROM challenges
            WHERE active = TRUE;
        """
        cur.execute(challenge_query)
        rows = cur.fetchall()  # Get all rows as a list of tuples
        column_names = [desc[0] for desc in cur.description]  # Extract column names
        challenges_dicts = [dict(zip(column_names, row)) for row in rows]  # Create a list of dictionaries

        return challenges_dicts  # This could be returned to a Flask route for JSON serialization

