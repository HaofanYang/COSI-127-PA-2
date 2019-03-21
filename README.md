## Student
Haofan Yang (haofanyang@brandeis.edu)
## ER Diagram 
![ER](/images/ER.jpg)
## Python sqlite3 APIs
### Conceptual workflow
`Connection` -> `Consor` -> `Execute SQL requests` -> `Close Consor` -> `Commit changes` -> `Close Connection` 
1. `conn = sqlite3.connect('*.db')` 
    
    This will load a `.db` file or create a new `.db` file if it doesn't exist
2. `cursor = conn.cursor()`

    This instantiates a cursor, which will be used to invoke SQL commands.

3. `curcor.execute("$(SQL request)", ($(Parameters)))`

    This will execute a given SQL request. Please refer to SQL request of type `String`, which is independent with python 
    or other programming languages. 
    
    The **second input** is a `tuple` of parameters.

4. `curcor.featchall()`

    Return a `list` of `tuple`, where each `tuple` corresponds to a raw of the table.

5. `cursor.close()`

    When finish editing, remember to close the cursor.

6. `conn.commit()`

    And then commit changes made to this database.
    
7. `conn.close()`

    And then close the connection.

## Code Design Doc
### Functionality
1. `load_data()`: 
    * **Description**: Load `.csv` file and produce a resulting `.db` file.
    * **Input type**: `Null`
    * **Output type**: `Null`
2. `overdue_book()`: 
    * **Description**: Given a date in the form of `MM-DD-YYYY`, print a `list` of overdue books that are still hold by patrons
    * **Input type**: `String`
    * **Output type**: `List`
3. `most_popular_books()`:
    * **Description**: Return a `List` of books that have been checked out most frequently.
    * **Input type**: `Null`
    * **Output type**: `Null`
4. ``