from influx import InfluxDB

#-- connect to database
db = InfluxDB('http://127.0.0.1:8086',precision='ms')

NOME_DATABASE = "lego"
# db.write(NOME_DATABASE,'machine_state', fields={"event": "h", "th": 100})
db.write(NOME_DATABASE,'machine_state', fields={"th": 10}, tags={"activity":6})
db.write(NOME_DATABASE,'machine_state', fields={"th": 10, "event": "evento"}, tags={"activity":6})

temp = db.select_recent(NOME_DATABASE, 'machine_state')
print(temp)
