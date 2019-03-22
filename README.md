## PA2 REPORT 

Haofan Yang(haofanyang@brandeis.edu)

---
### 1. ER diagram
![ER Diagram](/images/ER.jpg)

_**Figure 1.** ER diagram_

---
The ER diagram for this project is shown in _**Figure 1**_. In the remaining part of the session,
a detailed explanation on the design of this ER diagram will be provided:
    
   * For each entity type, assumptions made on data will be validated, and based on it, 
   functional dependencies between attributes will be explained.
   
   * The meaning of each relationship and the choice of their cardinality will be explained.
   
#### 1.1 Entities
There are four entity types.
##### 1.1.1 Patron
* **Assumptions made on data:**
    
    Each person has one and only one `card number`, two people are considered different patrons 
    as long as they have different card numbers even if they have the exact same name.
    
    Each patron has only one `phone number`. Actually this is not a natural assumption to make, 
    as in reality a person can have multiple phone numbers. However, if one takes a closer look at the dataset, 
    there is only one field for patron phone number.
    
    And each patron has one and only one `join year`.
    
* **Functional dependencies:**
    
    `Card_Number` => `Phone_Number`, `Join_Year`, `Name`
    
    Given a card number, the name, phone number and join year of a patron can be unambiguously determined.

##### 1.1.2 Book
* **Assumption made on data:**
    
    Each book has a unique `barcode`. 
    
    A book must have one and only one `title` but a title may refer to different books. 
    
    A book must have one and only one `year` in which it was published 
    but there may be many books published in that given year. 
    
    Furthermore, the library can have many copies of a _same_ book (same title, publish year, publisher and author)
    but those copies are still considered as different books.
    
* **Functional dependencies:**
    
    `Barcode` => `Title`, `Year`
    
    Given a barcode, the title and publish year of a book can be unambiguously determined.
##### 1.1.3 Publisher
* **Assumption made on data:**
    
    Publishers are identified by their names. As long as two publishers have different names, 
    it is safe to consider them as different publishers.
    
* **Functional dependencies:**

    `Name` => `Phone_Number`
    
    Given a publisher name, the publisher phone can be unambiguously determined.
##### 1.1.4 Author
* **Assumption made on data:**
    
    An author can be uniquely identified by his or her name.
    
        Special notes for readers: 
        At this point I realize I have made a wrong assumption on authors. That is, two DIFFERENT authors 
        who were born in DIFFERENT YEARS can have the SAME name. Thus the primary key for `Author` should be 
        a compound key of year and name. However, at this point, I have only two hours till due time and I 
        have no choice but to continue this mistake in the remaining part, as I don't have time to modify code
* **Functional dependencies:**

    `Name` => `Birth_Year`
#### 1.2 Relationships
There are three relationship types
##### 1.2.1 Checkout

`Book` and `Patron` are participants of this binary relationship. As one book can be checked out by 
different patrons and a patron can check out different books, this is a **many to many** relationship 
and attributes of this relationship cannot migrate to either side. For this reason, a **physical** 
table in the database is required for this relationship. For more detail on schema, 
please refer to **session 1.3**

##### 1.2.2 Write

`Book` and `Author` are participants of this binary relationship. Each book must have an unique author 
but one author may write different books. As a result, this is a **One to Many** relationship. To represent this
relationship, foreign key referencing between `Book(author)` and `Author(name)` is sufficient.
##### 1.2.3 Publish

`Book` and `Publisher` are participants of this binary relationship. Each book must have an unique publisher 
but one publisher may have published different books. As a result, this is a **One to Many** relationship. 
To represent this relationship, foreign key referencing between `Book(publisher)` and `Publisher(name)` is sufficient.
#### 1.3 Schemas involved
As illustrated in previous sessions, the schema design corresponding to the ER diagram shown in _**Figure 1**_
is as follows:
```sqlite3
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
```

---
### 2 Normalization in 3NF
#### 2.1 First normal form
The original data has already complied with the first normal form:
*  There are **no multivalues** for each attribute
*  Each row of the same attributes are of the **same type**
![1NF](/images/1NF.jpeg)
_**Figure 2.** 1NF Normalization_
#### 2.2 Second normal form
It is difficult to identify a primary key from **Figure 2.** To satisfy the second normal form, the original 
table is split into three tables `Book`, `Patron` and `Checkout`, each of which complies with 
the second normal form, as every non-key attribute is dependent on the primary key.
![2NF](/images/2NF.jpeg)
_**Figure 3.** 2NF Normalization_
#### 2.3 Third normal form
However, not all non-key attributes in those three tables are **independent**.
For example, `Publisher` and `Publisher_Phone` are not independent, as `Publisher_Phone`
can be determined by `Publisher`. In order to comply with the third normal form, a new schema 
is proposed as shown in **Figure 4.**
![3NF](/images/3NF.jpeg)
_**Figure 4.** 3NF Normalization_

This was the actual schema implemented in `main.py`