## General data

- date: 14/03/2023
- time: from 16:54 until 18:08
- run time: 1hr 14min approx
- run on 5s model
- number of pallets: 5
- only 3 rfid reader: on station 1, station 2, station 3.
- first test to run for more than one hour

## Results
- test stopped due to problem with station 1 pusher (pusher run out).
- 220 parts created.
- rfid readings observed to working and matching with the real conditions.
- ev3 could grab the UID from rfid and attach it to finish trace.
- ev3s without rfid returned NULL value in database.
- eror message observed by broker_execute.py for not finding thr part 0 is ony present for second and third message from rfid (rfid sends the UID to database three times).
- decided to add 0.5s delay between `finished` trace and next `started` trace to have different timestamps on the databse. This time difference error which might build towards end would be corrected now and then when the synchronisation happens.