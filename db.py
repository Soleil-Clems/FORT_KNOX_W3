from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()


def connect_db():
  conn= None
  try:
      conn = psycopg2.connect(
      dbname=os.getenv("POSTGRES_DB"),
      user=os.getenv("POSTGRES_USER"),
      password=os.getenv("POSTGRES_PASSWORD"),
      host=os.getenv("POSTGRES_HOST"),
      port=os.getenv("POSTGRES_PORT")
      )

      cursor = conn.cursor()

      print('PostgreSQL database version:')
      cursor.execute('SELECT version()')

      db_version = cursor.fetchone()
      print(db_version)
  except (Exception, psycopg2.DatabaseError) as error:
        print(error)
  finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        else:
            print("connection is none")

connect_db()