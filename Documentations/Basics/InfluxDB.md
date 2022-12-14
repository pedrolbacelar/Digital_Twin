# InfluxDB v1.7.7

## Introduction

InfluxDB is an open-source time series database developed by the company InfluxData. It is written in the Go programming language for storage and retrieval of time series data in fields such as operations monitoring, application metrics, Internet of Things sensor data, and real-time analytics.

Following documentation is related to installation and implementation of the InfluxDB v1.7.7. This is an older version of InfluxDB. This is being used without upgrading for retaining the consistency with existing codes and methodologies.

## Installation

- Since this is an older version of the database, the intallation file is not available in the InfluxDB website anymore. The setup files are currently available as a *.zip* folder. The required setup files will be made available in the lab computer for future.
- Extract the *.zip* folder to: **C:\Program Files\InfluxData\** as “influxdb-1.7.7-1”

## **Running InfluxDB server instance**

- To run the database, run following code in command prompt:

```powershell
cd C:\Program Files\InfluxData\influxdb-1.7.7-1
influxd
```

![image](https://user-images.githubusercontent.com/72768576/207633964-456b426f-b514-439f-8588-5978cf5a9f62.png)

- Note: This cmd window have to be kept open for the database to run in background.

## Running Influx shell

- To open Influx command line index, run following code in command prompt:
- 

```powershell
cd C:\Program Files\InfluxData\influxdb-1.7.7-1
influx
```

- Now you can start to read, write, create and drop (erase) data in the databases from the command prompt

## Some basic command lines

Following command line examples are run in the Influx shell. Read above section to know, how to initiate an Influx shell.

### Show databases

```powershell
SHOW DATABASES
```

### Create, drop (erase) and use a database

- to create

```powershell
CREATE DATABASE <database_name>	
```

- to drop

```powershell
DROP DATABASE <database_name>
```

- to use

```powershell
USE <database_name>
```

![image](https://user-images.githubusercontent.com/72768576/207634045-4c966504-7381-46ff-ab83-28a01c026558.png)


### Managing Measurements

![image](https://user-images.githubusercontent.com/72768576/207634125-cbf59893-415c-4c54-bb3b-63b33d18a214.png)


The measurements are created by adding the first data (Insert method). Tags are part of a measurement which tend to repeat often. Fields generally hold variable data. Using tags to specify data such as machine ID, event type are recommended as they increase database efficiency in relation to reduced computational power and time. Fields could hold data like temperature or throughput as they are highly variable data.

- to insert a measurement

```powershell
USE <database_name>
INSERT <measurement_name>,<tag>=<tag_value> <field>=<field_value>
```

![image](https://user-images.githubusercontent.com/72768576/207634187-e8d78557-ffee-4cc0-a6fb-a4f2fbcac0fb.png)

- delete all data from specific measurement

```powershell
DELETE FROM <measurement_name>
```

- delete the measurement

```powershell
DROP MEASUREMENT <measurement_name>
```

- to show *Measurements*
    - do not replace the keyword “MEASUREMENTS” with any user defined variables as this command is for showing all the measurements_ variable .

```powershell
SHOW MEASUREMENTS
```

![image](https://user-images.githubusercontent.com/72768576/207634269-6cef59e0-475f-473d-b3b3-99ea9116d190.png)

- to show all data from specific measurement

```powershell
SELECT * FROM <measurement_name>
```

![image](https://user-images.githubusercontent.com/72768576/207634353-53b4edde-04f6-4ce6-a980-714cb1451ae8.png)

## Installing python library

- For working with python, “influx-client” library has to be installed.

```python
python3 -m pipenv install influx-client
```

 

- Above given library is for Influx 1.x versions. This should not be confused with “influxdb-client” library which is meant for Influx 2.x versions.
- Use the following syntax to import the library

```python
from influx import InfluxDB
```

- While running, if following error occurs (i.e, … cannot be loaded because running scripts is disabled on this system),
    
    ![image](https://user-images.githubusercontent.com/72768576/207634431-7a6c07b2-096b-496a-b4cf-15a2bea97eff.png)
    
    follow the instructions in the website below to add the specific path given in the error message.
    https://learn.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)
