CREATE TABLE patron (
    card_number TEXT PRIMARY KEY,
    name TEXT,
    join_year INTEGER,
    phone_number TEXT
);

CREATE TABLE book (
    barcode TEXT PRIMARY KEY,
    title TEXT,
    year INTEGER,
    author_id INTEGER REFERENCES author(id)
    publisher_id INTEGER REFERENCES publisher(id)
);

CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    birth_year INTEGER
);

CREATE TABLE publisher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
);

CREATE TABLE checkout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT REFERENCES publisher(barcode),
    patron_id TEXT REFERENCES patron(card_number),
    checkout_date REAL,
    due_date REAL,
    returned INTEGER CHECK (returned = 1 OR returned = 0)
);