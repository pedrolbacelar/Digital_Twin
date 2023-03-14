## General data

- date: 14/03/2023
- time: from 16:41 until 14:48
- run time: 7min approx
- run on 5s model
- number of pallets: 5
- only 3 rfid reader on station 1, station 2, station 3.
- test attempt for verification of physical system and first test with broker_execute.py

## Results
- test stopped due to problem with station 1 pusher (pusher run out)
- 10 parts created
- rfid readings observed to working and matching with the real conditions.
- ev3 could grab the UID from rfid and attach it to finish trace.
- ev3s without rfid returned NULL value in database.
- eror message observed by broker_execute.py for not finding thr part 0 is ony present for second and third message from rfid (rfid sends the UID to database three times).