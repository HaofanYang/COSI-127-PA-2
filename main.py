# You should write your Python program in this file. Currently, it contains
# a skeleton of the methods you will need to write.

import csv
import os
import sqlite3

def load_data():
    # This function should:
    # 1) create a new database file called "library.db"
    # 2) create appropiate tables
    # 3) read the data.csv file and insert data into your database

    # first, we will check to see if library.db already exists.
    # if it does, we will delete it.
    if os.path.exists("library.db"):
        os.remove("library.db")

    # next, we will create a new SQLite database.

    # create a database connection.
    conn = sqlite3.connect("library.db")

    # create a cursor (this is like a single session)
    curr = conn.cursor()

    # send a pragma command to tell SQLite to check foreign key
    # constraints (it does not by default :( )
    curr.execute("PRAGMA foreign_keys = ON;")

    # here's an example for how to create a table and insert 2 rows into it
    # (note the `?` syntax to put values into the query)
    curr.execute("CREATE TABLE t ( val1 INTEGER, val2 TEXT )")
    curr.execute("INSERT INTO t VALUES(?, ?)",
                 (8, "this is a test"))
    curr.execute("INSERT INTO t VALUES(?, ?)",
                 (64, "this is another test"))


    # commit is like save -- if you don't do it, nothing is written.
    conn.commit()

    # here's an example of how to read data from the database
    curr.execute("SELECT * FROM t")
    for row in curr:
        # each time through the loop, row[0] will be the first column
        # of the result, and row[1] will be the second.
        print(row[0], row[1])

    conn.close() # close the DB connection when we are done

    # here's how to read a CSV file.
    with open("data.csv") as f:
        reader = csv.reader(f)
        next(reader) # throw out the header row

        for row in reader:
            # row[0] is the first column of the first row
            # row[1] is the second column of the first row
            print(row)



def overdue_books(date_str):
    # This function should take in a string like YYYY-MM-DD and print out
    # a report of all books that are overdue as of that date, and the
    # patrons who still have them.

    pass # delete this when you write your code

def most_popular_books():
    # This function should print out a report of which books are the
    # most popular (checked out most frequently). The library cares about
    # the books themselves, not who published them.

    pass # delete this when you write your code

def note_return(patron_card, book_barcode):
    # This function should update the database to indicate that the patron
    # with the passed card number has returned the book with the given
    # barcode. This function should print out an error if that patron didn't
    # have the book currently checked out.

    pass # delete this when you write your code

def note_checkout(patron_card, book_barcode, checkout_date):
    # This function should update the database to indicate that a patron
    # has checked out a book on the passed date. The due date of the book
    # should be 7 days after the checkout date. This function should print
    # out an error if the book is currently checked out.

    pass # delete this when you write your code

def replacement_report(book_barcode):
    # This function will be used by the library when a book has been lost
    # by a patron. It should print out: the publisher and publisher's contact
    # information, the patron who had checked out the book, and that patron's
    # phone number. 
    
    pass # delete this when you write your code


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
            
            
