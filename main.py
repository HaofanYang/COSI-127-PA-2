# You should write your Python program in this file. Currently, it contains
# a skeleton of the methods you will need to write.

import csv
import os
import sqlite3

# Index of corresponding information in each row in the CSV file
P_NAME = 0 # Patron name
P_CN = 1 # Patron card number
P_JY = 2 # Patron join year
P_PN = 3 # Patron phone number
B_BC = 4 # Book bar code
B_TITLE = 5 # Book title
B_YEAR = 6 # Book year
B_AUTHOR = 7 # Book Author
A_BIRTHY = 8 # Author birth year
P_NAME = 9 # Publisher name
P_PHONE = 10 # Publisher phone
CKO_DATE = 11 # Checkout date
DUE_DATE = 12 # Due date
RETURNED = 13 # Returned


def create_table_commands():
    # Create tables shown in the ER diagram
    fd = open('create_tables.sql', 'r')
    sql = fd.read()
    fd.close()
    return sql.split(';')

# TODO reload data before submit
def load_data():
    # This function should:
    # 1) create a new database file called "library.db"
    # 2) create appropriate tables
    # 3) read the data.csv file and insert data into your database
    if os.path.exists("library.db"):
        os.remove("library.db")
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()
    curr.execute("PRAGMA foreign_keys = ON;")

    # Create tables. Please refer to create_tables.sql for more details
    for command in create_table_commands():
        curr.execute(command)
    conn.commit()

    with open("data.csv") as f:
        reader = csv.reader(f)
        next(reader)  # throw out the header row
        for row in reader:
            # Check if a patron card number has been added
            not_exist = curr.execute("SELECT * FROM patron WHERE card_number = ?", (row[P_CN],)).fetchone() is None
            if not_exist:
                curr.execute("INSERT INTO patron VALUES(?,?,?,?)",
                             (row[P_CN], row[P_NAME], row[P_JY], row[P_PHONE]))

            # Check if an author name has been added
            not_exist = curr.execute("SELECT * FROM author WHERE name = ?", (row[B_AUTHOR],)).fetchone() is None
            if not_exist:
                curr.execute("INSERT INTO author VALUES(?,?)", (row[B_AUTHOR], row[A_BIRTHY]))

            # Check if a publisher name has been added
            not_exist = curr.execute("SELECT * FROM publisher WHERE name = ?", (row[P_NAME],)).fetchone() is None
            if not_exist:
                curr.execute("INSERT INTO publisher VALUES(?,?)", (row[P_NAME], row[P_PHONE]))

            # Check if a book barcode has been added
            not_exist = curr.execute("SELECT * FROM book WHERE barcode = ?", (row[B_BC],)).fetchone() is None
            if not_exist:
                curr.execute("INSERT INTO book VALUES(?,?,?,?,?)",
                             (row[B_BC], row[B_TITLE], row[B_YEAR], row[B_AUTHOR], row[P_NAME]))

            # When adding rental records, I assumed there is NO invalid rental record in the original .csv file
            # An invalid rental record can be, for example, a book was checked out when it wasn't returned back
            curr.execute("INSERT INTO checkout VALUES(null,?,?,?,?,?)",
                         (row[B_BC], row[P_CN], row[CKO_DATE], row[DUE_DATE], row[RETURNED]))

    conn.commit()
    curr.close()
    conn.close()


def overdue_books(date_str):
    # This function should take in a string like YYYY-MM-DD and print out
    # a report of all books that are overdue as of that date, and the
    # patrons who still have them.
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()
    match = curr.execute("""
                    SELECT B.name, C.title, date(A.due_date) 
                    FROM checkout AS A
                    JOIN patron AS B ON B.card_number = A.patron_id
                    JOIN book AS C ON C.barcode = A.book_id
                    WHERE A.due_date <= julianday(?) AND A.returned = 0
                """, (date_str,)).fetchall()
    if len(match) > 0:
        print("{} Overdue Books Found:".format(len(match)))
        for row in match:
            print("Patron: {}; Book: {}; Due_date: {}".format(row[0], row[1], row[2]))
    else:
        print("There is no book overdue.")
    curr.close()
    conn.close()


# TODO efficiency
def most_popular_books():
    # This function should print out a report of which books are the
    # most popular (checked out most frequently). The library cares about
    # the books themselves, not who published them.
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()

    # I assume the requirement for this function is to
    # give a list of books that have the greatest number of checkouts
    match = curr.execute("""
                        SELECT DISTINCT title, count FROM
                            (SELECT B.title, COUNT(A.book_id) as count
                            FROM checkout AS A
                            JOIN book AS B ON A.book_id = B.barcode
                            GROUP BY A.book_id) AS MATCH
                        WHERE count = (
                                SELECT MAX(count) FROM 
                                    (SELECT B.title, COUNT(A.book_id) as count
                                    FROM checkout AS A
                                    JOIN book AS B ON A.book_id = B.barcode
                                    GROUP BY A.book_id)
                            )
                        ORDER BY title
                    """).fetchall()
    print("The most popular book(s) is:")
    for row in match:
        print("Book: {}; Number_of_checkout: {}".format(row[0], row[1]))
    curr.close()
    conn.close()


# TODO print error??
def note_return(patron_card, book_barcode):
    # This function should update the database to indicate that the patron
    # with the passed card number has returned the book with the given
    # barcode. This function should print out an error if that patron didn't
    # have the book currently checked out.
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()

    # Get the checkout id of unreturned book
    match = curr.execute("""
                            SELECT id FROM checkout
                            WHERE patron_id = ? AND book_id = ? AND returned = 0
                        """, (patron_card, book_barcode)).fetchall()
    if len(match) == 0:
        print("Error: this patron does not have the book currently checked out")
    else:
        curr.execute("""
                UPDATE checkout
                SET returned = 1
                WHERE book_id = ?
            """, (book_barcode, ))
        conn.commit()
    curr.close()
    conn.close()


# TODO Other bugs?
def note_checkout(patron_card, book_barcode, checkout_date):
    # This function should update the database to indicate that a patron
    # has checked out a book on the passed date. The due date of the book
    # should be 7 days after the checkout date. This function should print
    # out an error if the book is currently checked out.
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()

    # Check if the given book was returned
    match = curr.execute("""
                            SELECT id FROM checkout
                            WHERE book_id = ? AND returned = 0
                        """, (book_barcode, )).fetchall()

    # Check if exists such a patron
    patron = curr.execute("""
                            SELECT * FROM checkout
                            WHERE card_number = ?
                        """, (patron_card, )).fetchall()
    if len(match) > 0:
        print("Error: this book is currently checked out")
    elif len(patron) == 0:
        print("Error: patron doesn't exist")
    else:
        curr.execute("""
                INSERT INTO checkout VALUES(null, ?, ?, julianday(?), julianday(?, '+7 days'), 0)
            """, (book_barcode, patron_card, checkout_date, checkout_date))
        conn.commit()
    curr.close()
    conn.close()


# TODO unfinished
def replacement_report(book_barcode):
    # This function will be used by the library when a book has been lost
    # by a patron. It should print out: the publisher and publisher's contact
    # information, the patron who had checked out the book, and that patron's
    # phone number.
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()
    curr.close()
    conn.close()
    pass # delete this when you write your code


# TODO unfinished
def inventory():
    # This function should report the library's inventory, the books currently
    # available (not checked out).

    pass # delete this when you write your code


# this is the entry point to a Python program, like `public static void main`
# in Java.
if __name__ == "__main__":
    while True:
        print("Hello! Welcome to the library system. What can I help you with today?")
        print("\t1) Load data")
        print("\t2) Overdue books")
        print("\t3) Popular books")
        print("\t4) Book return")
        print("\t5) Book checkout")
        print("\t6) Book replacement")
        print("\t7) Inventory")
        print("\t8) Quit")

        user_response = int(input("Select an option: "))

        if user_response == 1:
            load_data()
        elif user_response == 2:
            date = input("Date (YYYY-MM-DD): ")
            overdue_books(date)
        elif user_response == 3:
            most_popular_books()
        elif user_response == 4:
            patron = input("Patron card: ")
            book = input("Book barcode: ")
            note_return(patron, book)
        elif user_response == 5:
            patron = input("Patron card: ")
            book = input("Book barcode: ")
            chd = input("Checkout date (YYYY-MM-DD): ")
            note_checkout(patron, book, chd)
        elif user_response == 6:
            book = input("Book barcode: ")
            replacement_report(book)
        elif user_response == 7:
            inventory()
        elif user_response == 8:
            break
        else:
            print("Unrecognized option. Please try again.")
