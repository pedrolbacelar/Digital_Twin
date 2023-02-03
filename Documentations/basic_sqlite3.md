# SQLite3 Introdcution
SQLite is a free and open-source software library that provides a relational database management system. It is a popular choice for embedded systems and mobile devices, due to its small footprint, fast performance, and ease of use. SQLite uses dynamic typing, which means that data can be stored in a variety of formats, including integers, floats, strings, and blobs. It also supports SQL, the standard language used to manage relational databases. Unlike other databases, SQLite does not run as a separate server process, but instead, it is embedded into the applications that use it, making it easy to distribute and deploy. SQLite also has a proven track record of reliability and stability, with a rich history of use in a wide range of applications.

## "Instalation" (not necessary for python3)
To install SQLite on your system, you can download the precompiled binaries from the official website, sqlite.org. For Windows, Mac, and Linux systems, there are precompiled packages available for download.

If you're using Python, you can use the sqlite3 library, which provides a convenient interface for working with SQLite databases. You don't need to install any additional software to use SQLite with Python. The sqlite3 library is included in the standard Python distribution, so you can start using it right away.

## First Example

```python3
import sqlite3

# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect("example.db")

# Create a table
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
)
""")

# Insert data into the table
conn.execute("""
INSERT INTO users (name, age)
VALUES ('John Doe', 35)
""")

# Commit the changes
conn.commit()

# Query the data
cursor = conn.execute("SELECT * FROM users")
for row in cursor:
    print(row)

# Close the connection
conn.close()

```

In this example, the connect function is used to create a connection to the database file. The execute method is used to run SQL statements, such as creating a table or inserting data. The commit method is used to save the changes to the database. Finally, the execute method is used again to run a query and retrieve data from the database. The results of the query are returned as a cursor, which can be iterated over to access the rows of data.

## Nomenclature and Limitations

There are a few limitations to keep in mind when creating tables in a SQLite database:

- Column names: Column names must be unique within a table and cannot be the same as any SQLite keywords.
- Data types: SQLite supports a limited set of data types, including INTEGER, TEXT, REAL, BLOB, and NULL.
- Column constraints: SQLite supports several constraints, such as NOT NULL, UNIQUE, and PRIMARY KEY, which can be used to enforce rules on the data in a table.
- Maximum number of columns: The maximum number of columns in a SQLite table is limited to 32767.
- Maximum size of a row: The maximum size of a single row in a SQLite table is limited to approximately 1 MB.
- Maximum database size: The maximum size of a single SQLite database is limited to 140 terabytes.

In general, SQLite is designed to be a lightweight, file-based database that is well-suited for simple, small-scale applications. If you're working with a large-scale application that requires complex data structures and high performance, you may want to consider using a different database system, such as MySQL or PostgreSQL.


## Closing Database Conections
Closing a connection to a database is important because it releases the resources that the connection was using, such as memory and file handles. Failing to close a connection can lead to resource leaks and potential stability issues, especially in long-running applications.

In addition, some databases limit the number of concurrent connections that can be made at the same time. By properly closing connections when they're no longer needed, you ensure that you don't exceed this limit and prevent other parts of your application from being able to connect to the database.

Finally, it's good practice to close a connection as soon as you're done using it. This helps ensure that you don't accidentally reuse a connection that has been closed, or attempt to perform operations on a connection after it has been closed, which can result in errors.

In Python, it's recommended to use the with statement when working with databases. The with statement automatically closes the connection when the block of code within the with statement is finished. Here's an example:
```python
import sqlite3

with sqlite3.connect("example.db") as conn:
    # Query the data
    cursor = conn.execute("SELECT * FROM users WHERE name = 'John Doe'")
    for row in cursor:
        print(row)

```
In this example, the connection is automatically closed when the block of code within the with statement is finished, even if an exception is raised. This makes it easier to ensure that connections are properly closed, and reduces the risk of resource leaks and stability issues.


## Difference Between INTEGER and INTEGER PRIMARY KEY
In SQLite, INTEGER and INTEGER PRIMARY KEY are both data types for storing integers, but INTEGER PRIMARY KEY has an additional constraint.

The INTEGER data type is used to store integer values, such as 1, 2, 3, etc.

The INTEGER PRIMARY KEY data type is used to store the primary key of a table. The primary key is a unique identifier for each row in the table, and it is used to enforce the relational integrity of the data in the table. When you define a column as INTEGER PRIMARY KEY, SQLite automatically generates a unique integer value for each row in the table, starting with 1 for the first row, 2 for the second row, and so on.

In addition to being a unique identifier for each row, the primary key is also used to enforce referential integrity when you create relationships between tables.

So, to summarize, the difference between INTEGER and INTEGER PRIMARY KEY is that INTEGER is a simple data type for storing integers, while INTEGER PRIMARY KEY is a special data type that is used to store the primary key of a table.

## Important Data Types
The most important data types in SQLite are:

- `NULL`: Represents the absence of a value.

- `INTEGER`: Stores whole numbers, such as 1, 2, 3, etc.

- `REAL`: Stores floating-point numbers, such as 3.14 or 1.2345.

- `TEXT`: Stores text values, such as "John Doe".

- `BLOB`: Stores binary data, such as images or binary files.

- `NUMERIC`: A flexible data type for storing decimal numbers, it is equivalent to REAL.

Note that the specific data types supported by SQLite may vary slightly depending on the implementation, but the above types are common across most implementations.

## Inserting Variables
You can insert variables into the SQL statement passed to .execute(). However, you need to use placeholders (?) in the SQL statement, and then pass the values for the placeholders as a separate argument to .execute(). This approach is known as parameter binding and helps to prevent SQL injection attacks.

Here's an example in Python using the sqlite3 library:
```python
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

name = 'John Doe'
age = 30

cursor.execute("""
INSERT INTO users (name, age)
VALUES (?, ?)
""", (name, age))

conn.commit()
conn.close()
```
In this example, the values for the name and age variables are passed as a tuple to the .execute() method, and the placeholders ? in the SQL statement are replaced with the actual values. This way, the values are safely separated from the SQL statement and can be easily changed without modifying the SQL code.

## When to use `commit`?
In SQLite, you need to call the commit method on the connection object every time you make a change to the database that you want to persist. The changes are not automatically saved to the database until you call the commit method.

For example, if you want to insert a single record into the database, you would use the following code:

```python
conn = sqlite3.connect('example.db')
conn.execute("INSERT INTO users (id, name, age) VALUES (1, 'John Doe', 30)")
conn.commit()
conn.close()
```

If you want to insert multiple records into the database, you can do so in a single commit call, like this:

```python
conn = sqlite3.connect('example.db')
conn.execute("INSERT INTO users (id, name, age) VALUES (1, 'John Doe', 30)")
conn.execute("INSERT INTO users (id, name, age) VALUES (2, 'Jane Doe', 25)")
conn.execute("INSERT INTO users (id, name, age) VALUES (3, 'Jim Smith', 35)")
conn.commit()
conn.close()

```

In general, you should call commit as soon as possible after making changes to the database, to ensure that the changes are saved in case of a crash or other unexpected error. However, you can also group multiple changes together and call commit once, if that makes sense for your use case.

## Cleaning the Database or Table
To clear the entire database in SQLite, you can delete all the rows in each table. Here is a sample code to do this:

```python
# Connect to the database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Get a list of all table names
cursor.execute("SELECT name from sqlite_master where type='table'")
table_names = cursor.fetchall()

# Loop through each table and delete all rows
for table_name in table_names:
    cursor.execute(f'DELETE from {table_name[0]}')

# Commit the changes
conn.commit()

# Close the connection
conn.close()

```
This code first retrieves a list of all table names in the database, then loops through each table and deletes all rows. Finally, it commits the changes and closes the connection.

To clear a specific table in SQLite, you can delete all the rows in that table. Here is a sample code to do this:

```python
# Connect to the database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Define the name of the table you want to clear
table_name = 'users'

# Delete all rows in the table
cursor.execute(f'DELETE from {table_name}')

# Commit the changes
conn.commit()

# Close the connection
conn.close()


```

This code defines the name of the table you want to clear, then deletes all the rows in that table. Finally, it commits the changes and closes the connection

**Another practical way: **

```python
def clear(self, table):
    #--- clear all the data written in {table}

    with sqlite3.connect(self.database_path) as digital_model_DB:
        digital_model_DB.execute(f"DROP TABLE IF EXISTS {table}")
        digital_model_DB.commit()
```





