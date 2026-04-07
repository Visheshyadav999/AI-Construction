import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv


load_dotenv()

SUPABASE_URI = os.getenv("SUPABASE_URI")


def get_db_connection():
    try:
        # Connect to the cloud database
        conn = psycopg2.connect(SUPABASE_URI)
        return conn
    except Exception as e:
        print(f"🚨 CLOUD DATABASE CONNECTION ERROR: {e}")
        return None

def get_cursor(conn):
    # RealDictCursor ensures our database rows are returned as JSON-like dictionaries, 
    # exactly how your frontend expects them!
    return conn.cursor(cursor_factory=RealDictCursor)