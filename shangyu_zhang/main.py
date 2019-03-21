import csv
import os
import sqlite3


PATRON = 0
CARD_BARCODE = 1
YEAR_JOINED = 2
PATRON_PHONE = 3
BOOK_BARCODE = 4
TITLE = 5
BOOK_YEAR = 6
AUTHOR = 7
AUTHOR_YEAR = 8
PUBLISHER = 9
PUBLISHER_PHONE = 10
CHECKOUT = 11
DUE = 12
RETURNED = 13


def load_sql_commands():
    # Read the schema sql and return list of sqls
    fd = open('schema.sql', 'r')
    sql = fd.read()
    fd.close()
    return sql.split(';')


def print_section_header(info):
    # Print header
    print('\n')
    print('-' * 30, info, '-' * 30)


def print_section_footer(info):
    # Print footer 
    print('-' * 30, info, '-' * 30)
    print('\n')


def get_db_connection():
    # Return db connection and cursor
    conn = sqlite3.connect("library.db")
    curr = conn.cursor()
    return conn, curr


# in Python, we specify functions using "def" -- this would be equiv to Java
# `public void load_data()`. Note that Python doesn't specify return types.
def load_data():
    # This function should:
    # 1) create a new database file called "library.db"
    # 2) create appropiate tables
    # 3) read the data.csv file and insert data into your database

    if os.path.exists("library.db"):
        os.remove("library.db")

    conn, curr = get_db_connection()
    curr.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables
    commands = load_sql_commands()
    for command in commands:
        curr.execute(command)
    conn.commit()

    with open("data.csv") as f:
        reader = csv.reader(f)
        next(reader) # throw out the header row
        for row in reader:
            # Why don't I use 'INSERT OR IGNORE'? Because I do not like that 'INSERT OR IGNORE' also increases the AUTO INCREMENT id in the table.
            try:
                curr.execute('INSERT INTO patron VALUES(null, ?, ?, ?, ?)', (row[PATRON], row[CARD_BARCODE], row[PATRON_PHONE], row[YEAR_JOINED]))
            except Exception as err:
                pass
            try:    
                curr.execute('INSERT INTO author VALUES(null, ?, ?)', (row[AUTHOR], row[AUTHOR_YEAR]))
            except Exception as err:
                pass
            try:    
                curr.execute('INSERT INTO publisher VALUES(null, ?, ?)', (row[PUBLISHER], row[PUBLISHER_PHONE]))
            except Exception as err:
                pass
            try:
                author_id = curr.execute("SELECT id FROM author WHERE name = ?", (row[AUTHOR],)).fetchone()[0]
                curr.execute('INSERT INTO book VALUES(null, ?, ?)', (row[TITLE], author_id))
            except Exception as err:
                pass
            try:
                book_id = curr.execute("SELECT id FROM book WHERE title = ?", (row[TITLE],)).fetchone()[0]
                publisher_id = curr.execute("SELECT id FROM publisher WHERE name = ?", (row[PUBLISHER],)).fetchone()[0]
                curr.execute('INSERT INTO book_version VALUES(null, ?, ?, ?, ?)', (row[BOOK_BARCODE], book_id, publisher_id, row[BOOK_YEAR]))
            except Exception as err:
                pass
            try:
                book_version_id = curr.execute("SELECT id FROM book_version WHERE barcode = ?", (row[BOOK_BARCODE],)).fetchone()[0]
                patron_id = curr.execute("SELECT id FROM patron WHERE name = ?", (row[PATRON],)).fetchone()[0]
                curr.execute('INSERT INTO borrowed_by VALUES(null, ?, ?)', (book_version_id, patron_id))
            except Exception as err:
                pass
            try:
                book_version_id = curr.execute("SELECT id FROM book_version WHERE barcode = ?", (row[BOOK_BARCODE],)).fetchone()[0]
                patron_id = curr.execute("SELECT id FROM patron WHERE name = ?", (row[PATRON],)).fetchone()[0]
                borrowed_by_id = curr.execute("SELECT id FROM borrowed_by WHERE patron_id = ? AND book_version_id = ?", (patron_id, book_version_id,)).fetchone()[0]
                curr.execute('INSERT INTO borrow VALUES(null, ?, ?, ?, ?)', (borrowed_by_id, row[CHECKOUT], row[DUE], row[RETURNED]))
            except Exception as err:
                pass

    conn.commit()
    conn.close() # close the DB connection when we are done


def overdue_books(date_str):
    # This function should take in a string like YYYY-MM-DD and print out
    # a report of all books that are overdue as of that date, and the
    # patrons who still have them.
    conn, curr = get_db_connection()
    result = curr.execute("""
        SELECT BK.title, PA.name, date(BR.due_date)
        FROM borrowed_by AS BB 
        JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
        JOIN book_version AS BV ON BB.book_version_id = BV.id
        JOIN book AS BK ON BV.book_id = BK.id
        JOIN patron AS PA ON BB.patron_id = PA.id
        WHERE BR.due_date <= julianday(?)
        AND BR.returned = 0
        ORDER BY BR.due_date, BK.title, PA.name
    """, (date_str,)).fetchall()
    if result and len(result) > 0:
        print_section_header('{} Overdue Books found'.format(len(result)))
        for row in result: 
            print('Book: {}, Patron: {}, Due Date: {}'.format(row[0], row[1], row[2]))
        print_section_footer('All Overdue Books')
    else:
        print_section_header('No Overdue Books As of that Date')
        print_section_footer('No Overdue Books As of that Date')
    conn.close()


def most_popular_books():
    # This function should print out a report of which books are the
    # most popular (checked out most frequently). The library cares about
    # the books themselves, not who published them.
    conn, curr = get_db_connection()
    # In my table of `book`, the pair of book title and author id is unique. 
    result = curr.execute("""
        SELECT BK.title AS book, AU.name, COUNT(BR.id)
        FROM borrowed_by AS BB 
        JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
        JOIN book_version AS BV ON BB.book_version_id = BV.id
        JOIN book AS BK ON BV.book_id = BK.id
        JOIN author AS AU ON BK.author_id = AU.id
        GROUP BY BK.id
        ORDER BY COUNT(BR.id) DESC, BK.title, AU.name
        LIMIT 20
    """).fetchall()
    print_section_header('Top 20 Most Popular Books')
    for row in result:
        print('Book: {}; Author: {}; Checked Out Times: {}'.format(row[0], row[1], row[2]))
    print_section_footer('Top 20 Most Popular Books')
    conn.close()


def note_return(patron_card, book_barcode):
    # This function should update the database to indicate that the patron
    # with the passed card number has returned the book with the given
    # barcode. This function should print out an error if that patron didn't
    # have the book currently checked out.
    conn, curr = get_db_connection()
    result = curr.execute("""
        SELECT BR.id
        FROM borrowed_by AS BB 
        JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
        JOIN book_version AS BV ON BB.book_version_id = BV.id
        JOIN patron AS PA ON PA.id = BB.patron_id
        WHERE PA.card = ?
        AND BV.barcode = ?
        AND BR.returned = 0
    """, (patron_card, book_barcode)).fetchone()
    
    if result and len(result) > 0:
        print_section_header('Book Returned')
        borrow_id = result[0]
        curr.execute("""
            UPDATE borrow
            SET returned = 1
            WHERE id = ?
        """, (borrow_id,))
        print_section_footer('Book Returned')
    else:
        print_section_header('ERROR: Patron not found or the patron did not have the book checked out.')
        print_section_footer('ERROR: Patron not found or the patron did not have the book checked out.')
    conn.commit()
    conn.close()

def note_checkout(patron_card, book_barcode, checkout_date):
    # This function should update the database to indicate that a patron
    # has checked out a book on the passed date. The due date of the book
    # should be 7 days after the checkout date. This function should print
    # out an error if the book is currently checked out.
    conn, curr = get_db_connection()
    result = curr.execute("""
        SELECT BR.id
        FROM borrowed_by AS BB 
        JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
        JOIN book_version AS BV ON BB.book_version_id = BV.id
        WHERE BV.barcode = ?
        AND BR.returned = 0
    """, (book_barcode,)).fetchone()
    
    if result and len(result) > 0:
        print_section_header('ERROR: The book is currently checked out.')
        print_section_footer('ERROR: The book is currently checked out.')
    else:
        patron_id, book_version_id = -1, -1
        try:
            patron_id = curr.execute("SELECT id FROM patron WHERE card = ?", (patron_card,)).fetchone()[0]
        except Exception as e:
            print_section_header('ERROR: Patron card not found.')
            print_section_footer('ERROR: Patron card not found.')
        try:
            book_version_id = curr.execute("SELECT id FROM book_version WHERE barcode = ?", (book_barcode,)).fetchone()[0]
        except Exception as e:
            print_section_header('ERROR: Book barcode not found.')
            print_section_footer('ERROR: Book barcode not found.')
        if patron_id != -1 and book_version_id != -1:
            print_section_header('Book Checked Out Successfully.')
            result = curr.execute('SELECT id FROM borrowed_by WHERE patron_id = ? AND book_version_id = ?', (patron_id, book_version_id)).fetchone()
            if result and len(result) > 0:
                borrowed_by_id = result[0]
            else:
                curr.execute('INSERT INTO borrowed_by VALUES(null, ?, ?) ', (book_version_id, patron_id))
                borrowed_by_id = curr.lastrowid
            curr.execute('INSERT INTO borrow VALUES(null, ?, julianday(?), julianday(?, "+7 days"), 0)', (borrowed_by_id, checkout_date, checkout_date))
            print_section_footer('Book Checked Out Successfully.')
    conn.commit()
    conn.close()


def replacement_report(book_barcode):
    # This function will be used by the library when a book has been lost
    # by a patron. It should print out: the publisher and publisher's contact
    # information, the patron who had checked out the book, and that patron's
    # phone number. 
    conn, curr = get_db_connection()
    result = curr.execute("""
        SELECT PB.name, PB.phone, PA.name, PA.phone
        FROM borrowed_by AS BB
        JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
        JOIN book_version AS BV ON BB.book_version_id = BV.id
        JOIN patron AS PA ON PA.id = BB.patron_id
        JOIN publisher AS PB ON BV.publisher_id = PB.id
        WHERE BV.barcode = ?
        AND BR.returned = 0
    """, (book_barcode,)).fetchone()
    if result and len(result) > 0:
        print_section_header('Replacement required.')
        print('This book has been lost by -> Name: {}; Phone: {}'.format(result[2], result[3]))
        print('Please contact the publisher for a replacement -> Publisher: {}; Phone: {}'.format(result[0], result[1]))
        print_section_footer('Replacement required.')
    else:
        print_section_header('ERROR: Book barcode not found or the book is not checked out.')
        print_section_footer('ERROR: Book barcode not found or the book is not checked out.')
    conn.close()
    

def inventory():
    # This function should report the library's inventory, the books currently
    # available (not checked out).
    conn, curr = get_db_connection()
    result = curr.execute("""
        SELECT BK.title, BV.barcode, PB.name, BV.year
        FROM book AS BK
        JOIN book_version AS BV ON BK.id = BV.book_id
        JOIN publisher AS PB ON BV.publisher_id = PB.id
        WHERE BV.id NOT IN (
            SELECT DISTINCT(BV.id)
            FROM borrowed_by AS BB
            JOIN borrow AS BR ON BB.id = BR.borrowed_by_id
            JOIN book_version AS BV ON BB.book_version_id = BV.id
            JOIN book AS BK ON BK.id = BV.book_id
            AND BR.returned = 0
        )
        ORDER BY BK.title, BV.year, PB.name
    """).fetchall()
    if result and len(result) > 0:
        print_section_header('All {} available books.'.format(len(result)))
        for row in result:
            print('Book: {}; Barcode: {}; Publisher: {}; Published Year: {}'.format(row[0], row[1], row[2], row[3]))
        print_section_footer('All {} available books.'.format(len(result)))
    else:
        print_section_header('All books have been checked out.')
        print_section_footer('All books have been checked out.')
    conn.close()


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
            
            
