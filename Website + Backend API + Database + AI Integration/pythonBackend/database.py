import psycopg2
from contextlib import contextmanager

@contextmanager
def connectPostgres():
    conn = None
    try:
        conn = psycopg2.connect(
            database="apt",
            user="postgres",
            password="root",
            host="127.0.0.1",
            port=5432,
        )
        yield conn 
    finally:
        if conn:
            conn.close()
            print("Connection closed.")