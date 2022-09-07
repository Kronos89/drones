# imports
import flask
import json
import db
import re
import time
import logging
from timeloop import Timeloop
from datetime import timedelta
from db import db_connexion
from flask import Flask, jsonify, request


app = Flask(__name__)
tl = Timeloop()

models = "Lightweight", "Middleweight", "Cruiserweight", "Heavyweight"
states = "IDLE", "LOADING", "LOADED", "DELIVERING", "DELIVERED", "RETURNING"

def show_data(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
 

@app.route("/")
def prepare_database():
    dataset = json.load(open('data.json'))
    dataframe=list()
    
    for row in dataset:
        data = (str(row['serial_number']), str(row['model']), float(row['weight_limit']), float(row['battery_capacity']), str(row['state']))
        dataframe.append(data)

    try:
        db = db_connexion()
        cursor = db.cursor()
        cursor.executemany('insert into drone values(?,?,?,?,?)', dataframe)

    except Exception as E:
        print('Error : ', E)

    else:
        db.commit()
        db.close()
        print('Data inserted')

    drones()
    return '''<h1>Database created and ready</h1>
        <p>registering a drone ------> http://localhost:5000/drone</p>
        <p>loading a drone with medication items ------> http://localhost:5000/load</p>
        <p>checking loaded medication items for a given drone ------> http://localhost:5000/check_drone</p>
        <p>checking available drones for loading ------> http://localhost:5000/available</p>
        <p>check drone battery level for a given drone ------> http://localhost:5000/battery</p>
        '''

@app.route("/drone", methods=["POST"])
def insert_drone():
    drone = request.get_json()
    serial_number = drone["serial_number"]
    model = drone["model"]
    weight_limit = drone["weight_limit"]
    battery_capacity = drone["battery_capacity"]
    state = drone["state"]
    validation = validate_drone(serial_number, model, weight_limit, battery_capacity, state)
    
    if validation == "OK":
        result = db.insert_drone(serial_number, model, weight_limit, battery_capacity, state)
        return jsonify(result)
    else:
        return jsonify(validation)

def validate_drone(serial_number, model, weight_limit, battery_capacity, state):
    if len(serial_number) > 100:
        return "Serial number higher than 100 characters"
    if model not in models:
        return "Model must be: Lightweight, Middleweight, Cruiserweight, Heavyweight"
    if int(weight_limit) > 500:
        return "Weight must be lower than 500"
    if state not in states:
        return "State must be: IDLE, LOADING, LOADED, DELIVERING, DELIVERED, RETURNING"
    return "OK"

@app.route("/load_medication", methods=["POST"])
def load_medication():
    load = request.get_json()
    serial_number = load["serial_number"]
    medications = load["medications"]
    cargo_load = 0
    weight_limit = db.drone(serial_number)
    state = db.drone_state(serial_number)
    battery_capacity = battery(serial_number).get_json()["battery_capacity"]

    for medication in load["medications"]:
        cargo_load = cargo_load + medication['weight']
    
    if int(weight_limit) >= cargo_load:
        
        if battery_capacity < 25:
            return jsonify("Battery below 25% not loading"), 200

        if str(state) == "IDLE":
            for medication in load["medications"]:
                cargo_load = cargo_load + medication['weight']
                name = medication["name"]
                weight = medication["weight"]
                code = medication["code"]
                image = medication["image"]
                validation = validate_medication(name, code)

                if validation == "OK":
                    db.insert_medication(name, weight, code, image, serial_number)
                else:
                    return jsonify(validation)
            db.drone_state_update(serial_number)
            return jsonify("Loaded"), 200
        else:
            return jsonify("Drone not IDLE"), 200

    else:
        return jsonify("Weight limit of drone has been reach")

def validate_medication(name, code):
    if not re.match("^[A-Za-z0-9_-]*$", name):
        return "Allowed only letters, numbers, -, _ in medication name"
    if not re.match("^[A-Z0-9_]*$", code):
        return "Allowed only upper case letters, underscore and numbers in medication code"
    return "OK"

@app.route("/medication", methods=["POST"])
def insert_medication():
    medication = request.get_json()
    name = medication["name"]
    weight = medication["weight"]
    code = medication["code"]
    image = medication["image"]
    drone_serial = medication["drone_serial"]
    result = db.insert_medication(name, weight, code, image, drone_serial)
    return jsonify(result)


@app.route('/drones', methods=['GET'])
def drones():
    all_drones = db.drones()
    return jsonify(all_drones)


@app.route('/available', methods=['GET'])
def available():
    all_drones = db.available()
    return jsonify(all_drones)


@app.route('/check_drone/<serial_number>', methods=['GET'])
def check_drone(serial_number):
    all_medications = db.check_drone(serial_number)
    return jsonify(all_medications)


@app.route('/battery/<serial_number>', methods=['GET'])
def battery(serial_number):
    drone = db.battery(serial_number)
    return jsonify(drone)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Route not found</h1><p>The resource could not be found.</p>", 404


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*" # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response


@tl.job(interval=timedelta(minutes=1))
def log_job():
    drones = db.batterys()
    logging.basicConfig(filename="log_battery.txt", level=logging.DEBUG, format="%(asctime)s %(message)s")

    for drones in drones:
        logging.debug("     " + "Battery : " + str(drones["battery_capacity"]) + "     "+ "Serial number : " + str(drones["serial_number"]))



if __name__ == "__main__":
    tl.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
    


 
