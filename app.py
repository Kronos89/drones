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



if __name__ == "__main__":
    tl.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
    


 
