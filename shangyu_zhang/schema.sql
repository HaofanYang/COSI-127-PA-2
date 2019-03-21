CREATE TABLE author (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT,
       year INTEGER,
       UNIQUE(name, year)
);

CREATE TABLE patron (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT,
       card TEXT UNIQUE,
       phone TEXT UNIQUE,
       year INTEGER
);

CREATE TABLE publisher (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT UNIQUE,
       phone TEXT UNIQUE
);

CREATE TABLE book (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT,
       author_id INTEGER REFERENCES author(id),
       UNIQUE(title, author_id)
);

CREATE TABLE book_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    book_id INTEGER REFERENCES book(id),
    publisher_id INTEGER REFERENCES publisher(id),
    year INTEGER
);

CREATE TABLE borrowed_by (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_version_id INTEGER REFERENCES book_version(id),
    patron_id INTEGER REFERENCES patron(id),
    UNIQUE(book_version_id, patron_id)
);

CREATE TABLE borrow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    borrowed_by_id INTEGER REFERENCES borrowed_by(id),
    check_out_date REAL,
    due_date REAL,
    returned INTEGER CHECK(returned = 0 OR returned = 1),
    UNIQUE(borrowed_by_id, check_out_date)
);