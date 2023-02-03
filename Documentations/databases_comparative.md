# Comparing different Database Options

## General Overview

There are several database libraries for Python that are considered easy to use, including:

- SQLite: This is a built-in, file-based database that doesn't require any setup or configuration. It's great for small to medium-sized projects and is often used as the default database in many web frameworks.
- SQLAlchemy: This is a popular SQL toolkit that provides a high-level and flexible API for interacting with a variety of databases, including SQLite, MySQL, and PostgreSQL. It's known for its ease of use and great documentation.
- Peewee: This is a simple, expressive, and easy-to-use ORM that supports SQLite, MySQL, and PostgreSQL. It's a great option for those looking for a lightweight and straightforward ORM.

These are just a few of the most popular options, and the best one for you will depend on your specific needs and the complexity of your project.


## Difference between SQLite and MySQL
MySQL and SQLite are both relational database management systems (RDBMS), but they have several key differences:

- Scalability: MySQL is designed to handle large amounts of data and can be used for mission-critical applications, while SQLite is better suited for small to medium-sized projects and is not as scalable as MySQL.
- Concurrent Access: MySQL provides better support for concurrent access, with features such as transactions and row-level locking, while SQLite does not handle concurrent access as well and is prone to database corruption if multiple users try to write to the same database simultaneously.
- User Management: MySQL has built-in user management features, allowing you to control who can access the database and what they can do with it, while SQLite does not have any user management features.
- Server vs. Embedded: MySQL is a server-based RDBMS that runs on a separate server, while SQLite is an embedded RDBMS that is included as a library in the application and does not require a separate server.
- Performance: MySQL is typically faster than SQLite for large datasets, but SQLite can be faster for small datasets and simple queries.
- Cost: MySQL is typically more expensive to use than SQLite, as it requires more hardware and maintenance, while SQLite is free and open source.

In general, MySQL is a better choice for large-scale, mission-critical applications that require high performance, scalability, and robust user management features, while SQLite is a good choice for smaller projects that do not require these features.

MySQL is available under both open source and commercial licenses. The open source version of MySQL is called MySQL Community Edition and is released under the GPL (GNU General Public License). It provides access to the core features of MySQL and is suitable for many small to medium-sized applications.

For commercial applications, there is also a paid version of MySQL called MySQL Enterprise Edition, which provides additional features, such as technical support, management tools, and performance enhancements.

## InfluxDB Overview
InfluxDB is an open source time series database, designed to handle large amounts of time-stamped data, such as performance metrics, sensor data, and application logs.

Good points:

- Time-Series Optimized: InfluxDB is specifically designed for time-series data, making it well suited for applications that require real-time data analysis and visualization.
- Scalability: InfluxDB can handle large amounts of data and is scalable to meet the needs of growing applications.
- Performance: InfluxDB is known for its high performance and can handle large amounts of incoming data with low latency.
- Integrations: InfluxDB integrates well with other tools and technologies, such as Grafana, Telegraf, and Kapacitor, providing a comprehensive solution for data storage, analysis, and visualization.

Bad points:

- **Limited SQL Support: InfluxDB does not support SQL as a query language and requires learning a new query language, InfluxQL, which may be a learning curve for some users.**
- Limited Transactions: InfluxDB does not provide the same level of transactional support as some other relational databases, making it less suitable for applications that require ACID transactions.
- Limited Joining and Aggregation: InfluxDB does not support traditional SQL-style joins and aggregations, making it less suitable for some analytical workloads.

Overall, InfluxDB is a powerful time series database, designed for real-time data analysis and visualization, and is a good choice for applications that generate large amounts of time-stamped data. However, it may not be the best choice for applications that require traditional SQL support, transactional guarantees, or complex data analysis.

InfluxDB is open source software, released under the MIT license. It is free to use and can be modified to meet the needs of your application. The source code is available on Github, allowing developers to contribute to the project and build custom extensions.

InfluxDB also provides a commercial version, called InfluxDB Enterprise, which includes additional features and support for enterprise-level use cases.

## Comparing InfluxDB and SQLite
SQLite is a relational database management system and can be used to store time-series data, but it is not specifically designed for time-series data. Time-series data is a sequence of data points collected at regular intervals, often over a long period of time.

InfluxDB is a time-series database that is specifically designed to handle large amounts of time-stamped data and provides optimized storage and querying capabilities for time-series data.

While SQLite can store time-series data, it does not provide the same level of performance, scalability, and ease of use for time-series data as InfluxDB. SQLite is better suited for small to medium-sized projects, whereas InfluxDB is designed for large-scale time-series data.

#### Code Implementation

- InfluxDB

```python
# Import the InfluxDB-Python library
from influxdb import InfluxDBClient

# Connect to the database
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('mydb')

# Write data to the database
data = [
    {
        "measurement": "temperature",
        "time": "2022-01-01T00:00:00Z",
        "fields": {
            "value": 25.0
        }
    },
    {
        "measurement": "temperature",
        "time": "2022-01-02T00:00:00Z",
        "fields": {
            "value": 26.0
        }
    }
]
client.write_points(data)

# Query data from the database
result = client.query('SELECT "value" FROM "temperature"')
print(result)
```
- SQLite

```python
# Import the SQLite library
import sqlite3

# Connect to the database
conn = sqlite3.connect('mydb.db')

# Create a table
conn.execute('''CREATE TABLE temperature (time TEXT, value REAL)''')

# Insert data into the table
conn.execute("INSERT INTO temperature (time, value) VALUES ('2022-01-01T00:00:00Z', 25.0)")
conn.execute("INSERT INTO temperature (time, value) VALUES ('2022-01-02T00:00:00Z', 26.0)")
conn.commit()

# Query data from the table
cursor = conn.execute("SELECT time, value from temperature")
for row in cursor:
    print(row)

# Close the connection
conn.close()

```
In the above example, we connect to an InfluxDB database and write and query data from a measurement called temperature. For SQLite, we connect to a database file, create a table, insert data, and query data from the table. Note that this is just a simple example and more advanced operations, such as indexing, transactions, and data aggregation, are also possible in both InfluxDB and SQLite.

> If you're looking for a simple and straightforward database for storing around 100 MB of data, you might consider using SQLite. SQLite is a lightweight, file-based database that does not require any setup or configuration. It is a good choice for small projects like yours where you don't need advanced features such as user management, server-side processing, or concurrent access.

> To use SQLite with Python, you can use the sqlite3 library, which provides a convenient interface for working with SQLite databases. You can create tables, insert data, and run queries with a few lines of code. The data is stored in a single file, which makes it easy to manage and backup.

> SQLite has good documentation. The official website, sqlite.org, provides detailed documentation on the SQLite syntax, API, and features. The documentation includes examples and tutorials that cover a wide range of topics, from basic database operations to advanced techniques for working with SQLite. Additionally, there is a large community of SQLite users and developers who contribute to the documentation and provide support on forums and other online resources.

# Final Balance

## InfluxDB

##### Gain Points

- It's a build-in Time Series database
- The lab already worked with it
- Already have the code written with this database

##### Pain Points

- The version used in the previous codes it's not supported anymore (need to re-write it anyway if you go for making something up to date)
- Installing the old version of the library is complexity
    - We didn't manage to fin that version online (just have a zip folder)
    - You need to first run it in the terminal and after run it in the python codes
    - It's tricky to know what library to install
- InfluxDB is moving in the direction of a more comercial software (user management, fancy website), so there is not too much support for the old version
- Not using the SQL language 
- Projected for more scalable applications

## SQLite

##### Gain Points

- It's a build-in library in python3 (just need to import it, no instalations required)
- Use the SQL language (learning that can be applied in future projects)
- Opensource and stable ([full documentation](https://www.sqlite.org/docs.html) and high community activity)
- Easy to use it and straight forward.
- Projected for more small and medium-sized applications (limited to 150 TB)

##### Pain Points

- Not a time-series database (the time need to be add manually)
- New (but similar) development


