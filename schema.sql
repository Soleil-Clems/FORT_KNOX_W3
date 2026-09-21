PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    birth_year INTEGER,
    death_year INTEGER
);

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    title TEXT,
    language TEXT,
    download_count INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY,
    subject_name TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS book_subjects (
    book_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    CONSTRAINT PK_book_subjects PRIMARY KEY(
        book_id,
        subject_id
    ),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);


CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    date_added TEXT,
    reviewer TEXT,
    recommend INTEGER,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE INDEX IF NOT EXISTS idx_books_author_id ON books(author_id);
CREATE INDEX IF NOT EXISTS idx_reviews_book_id ON reviews(book_id);