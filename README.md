API REST Python Sqlite3 Flask and Json
======================================

> Drone project

### Dependencies

> pip install flask timeloop or pip install -r requirements.txt 


### Run

> You can run the project by running python app.py


### Testing the API

> There are differents routes

/drone by POST with this json to registering a drone:
>{
>    "serial_number": "A0000011",
>    "model": "Lightweight",
>    "weight_limit": 500,
>    "battery_capacity": 80,
>    "state": "IDLE"
>}

/load_medication by POST with this json to loading a drone with medication items:
>{
>    "serial_number": "A000002",
>    "medications": [
>        { "weight": 100,"name": "Aspirina","code": "AS00003","image": ""},
>        { "weight": 20,"name": "Aspirina","code": "AS00004","image": ""},
>        { "weight": 30,"name": "Dipirona","code": "DI00002","image": ""}
>    ]
>}

/check_drone/<serial_number> by GET for checking loaded medication items for a given drone:
>http://localhost:5000/check_drone/A000002

/available by GET for checking available drones for loading
>http://localhost:5000/available

/battery/<serial_number> by GET for check drone battery level for a given drone:
>http://localhost:5000/battery/A000001