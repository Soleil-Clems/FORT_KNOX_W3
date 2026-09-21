import sys
import logging
import db
import yaml
import json
import sqlite3

with open("config.yaml") as f:
    config = yaml.safe_load(f)

def load_db():
  with sqlite3.connect(config["db_path"]) as connection:
    db.create_schema(connection)
    cursor = connection.cursor()
  return cursor, connection

def v_prolific_authors():
  db = load_db()
  cursor = db[0]
  connection = db[1]

  sql =''' 
    CREATE VIEW IF NOT EXISTS v_prolific_authors AS
    SELECT authors.author_id, authors.name, COUNT(*) AS total_books 
    FROM authors
    LEFT JOIN books ON authors.author_id = books.author_id
    GROUP BY authors.author_id, authors.name 
    ORDER BY total_books DESC;
  '''
  cursor.execute(sql)

  cursor.execute("SELECT * FROM v_prolific_authors;")
  row = cursor.fetchall()
  connection.close()
  return row


def v_book_full():
  db = load_db()
  cursor = db[0]
  connection = db[1]
  
  sql = '''
  CREATE VIEW IF NOT EXISTS v_book_full AS
  SELECT books.book_id, books.title, authors.author_id, authors.name, AVG(rating) AS avg_rating, GROUP_CONCAT(subjects.subject_name,", " ) AS subjects 
  FROM books LEFT JOIN authors ON books.author_id = authors.author_id
  LEFT JOIN reviews ON books.book_id= reviews.book_id 
  LEFT JOIN book_subjects ON books.book_id = book_subjects.book_id 
  LEFT JOIN subjects ON book_subjects.subject_id = subjects.subject_id 
  GROUP BY books.book_id, books.title;
  '''
  cursor.execute(sql)

  sql = "SELECT * FROM v_book_full;"
  cursor.execute(sql)
  row = cursor.fetchall()
  connection.close()
  return row


def v_subject_popularity():
  sql = """
  CREATE VIEW IF NOT EXISTS v_subject_popularity AS
  SELECT subjects.subject_id, subjects.subject_name, COUNT(books.book_id) AS total_books, AVG(reviews.rating) AS average_rating 
  FROM subjects LEFT JOIN book_subjects ON subjects.subject_id = book_subjects.subject_id 
  LEFT JOIN books ON book_subjects.book_id = books.book_id 
  LEFT JOIN reviews ON books.book_id= reviews.book_id 
  GROUP BY subjects.subject_id, subjects.subject_name 
  ORDER BY total_books DESC;
  """
  db = load_db()
  cursor = db[0]
  connection = db[1]

  cursor.execute(sql)

  sql = "SELECT * FROM v_subject_popularity;"
  cursor.execute(sql)
  row= cursor.fetchall()
  connection.close()
  return row

def get_or_create_id(cursor, table, id_column, unique_column, value):
    sql = f"SELECT {id_column} FROM {table} WHERE {unique_column} = ?"
    cursor.execute(sql, (value,))

    row = cursor.fetchone()

    if row is not None:
        return row[0]

    sql = f"INSERT INTO {table} ({unique_column}) VALUES (?)"
    cursor.execute(sql, (value,))

    return cursor.lastrowid


def build():
    with sqlite3.connect(config["db_path"]) as connection:
        db.create_schema(connection)
        cursor = connection.cursor()

        with open(config["clean_json_path"], "r") as f:
            clean_json = json.load(f)

        for data in clean_json:
            if not data["author"]:
              continue

            author_name = data["author"].replace(",", "")
            
            

            author_id = get_or_create_id(
                cursor,
                "authors",
                "author_id",
                "name",
                author_name
            )

            sql_books = """
                INSERT OR REPLACE INTO books
                (book_id, author_id, title, language, download_count)
                VALUES (?, ?, ?, ?, ?)
            """

            cursor.execute(sql_books, (
                data["book_id"],
                author_id,
                data["title"],
                data["language"],
                data["download_count"]
            ))

            if data["reviewer"]:
              sql_reviews = """
                  INSERT OR REPLACE INTO reviews
                  (book_id, rating, date_added, reviewer, recommend)
                  VALUES (?, ?, ?, ?, ?)
              """

              cursor.execute(sql_reviews, (
                  data["book_id"],
                  data["my_rating"],
                  data["date_added"],
                  data["reviewer"],
                  data["recommend"]
              ))

            # Subjects
            for subject in data["subjects"]:
                subject_id = get_or_create_id(
                    cursor,
                    "subjects",
                    "subject_id",
                    "subject_name",
                    subject
                )

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO book_subjects
                    (book_id, subject_id)
                    VALUES (?, ?)
                    """,
                    (data["book_id"], subject_id)
                )

        connection.commit()
    connection.close()
    print("build", len(clean_json))


def query(option3=""):
        
  match option3:
    case "v_prolific_authors":
      return v_prolific_authors()
    case "v_book_full":
      return v_book_full()
    case "v_subject_popularity":
      return v_subject_popularity()
    case _:
      raise ValueError("The option", option3, "does not exist")
  

def explain(option3):
  db = load_db()
  cursor = db[0]
  connection = db[1]
  sql = f"""
    EXPLAIN QUERY PLAN {option3}
  """
  cursor.execute(sql)
  row = cursor.fetchall()
  connection.close()
  return row



def stats():
  db = load_db()
  cursor = db[0]
  connection = db[1]
  sql_authors = "SELECT count(*) FROM authors"
  sql_books = "SELECT count(*) FROM books"
  sql_reviews = "SELECT count(*) FROM reviews "
  sql_subjects = "SELECT count(*) FROM subjects"
  sql_book_subjects = "SELECT count(*) FROM book_subjects"

  cursor.execute(sql_authors)
  stat_authors = cursor.fetchone()[0]
  cursor.execute(sql_books)
  stat_books = cursor.fetchone()[0]
  cursor.execute(sql_reviews)
  stat_reviews = cursor.fetchone()[0]
  cursor.execute(sql_subjects)
  stat_subjects = cursor.fetchone()[0]
  cursor.execute(sql_book_subjects)
  stat_book_subjects = cursor.fetchone()[0]

  stat = f"""
  authors: {stat_authors},
  books: {stat_books},
  reviews: {stat_reviews},
  subjects: {stat_subjects},
  book_subjects: {stat_book_subjects}
  """
  connection.close()
  return stat



def options(option1, option2="", option3=""):

    match option1:
      case "build":
        build()
      case "query":
        if not option2 == "--view":
            raise ValueError("The option", option2, "does not exist with", option1)
              
        print(query(option3))
      case "explain":
        if not option2 == "--sql":
          raise ValueError("The option", option2, "does not exist with", option1)


        return print(explain(option3))
      case "stats":
        print(stats())
      case _:
        logging.error("Option not found")


try:
  command = sys.argv[1]
  command2 =  sys.argv[2] if len(sys.argv) > 2 else ""
  command3 =  sys.argv[3] if len(sys.argv) > 3 else ""
  
  options(command, command2, command3)
except  IndexError:
  logging.error("Command not found")
except ValueError as error:
  print('Caught this error: ', " ".join(error.args))