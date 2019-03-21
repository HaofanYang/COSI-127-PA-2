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
    author INTEGER REFERENCES author(name),
    publisher INTEGER REFERENCES publisher(name)
);

CREATE TABLE author (
    name TEXT PRIMARY KEY,
    birth_year INTEGER
);

CREATE TABLE publisher (
    name TEXT PRIMARY KEY,
    phone TEXT
);

CREATE TABLE checkout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT REFERENCES book(barcode),
    patron_id TEXT REFERENCES patron(card_number),
    checkout_date REAL,
    due_date REAL,
    returned INTEGER CHECK (returned = 1 OR returned = 0)
);