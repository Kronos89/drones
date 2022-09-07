import sqlite3
DATABASE_NAME = "drone.db"
JSON_NAME = "data.json"

def show_data(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def db_connexion():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def db_connexion_select():
    db = db_connexion()
    db.row_factory = show_data
    cur = db.cursor()
    return cur

def drones():
    cur = db_connexion_select()
    return cur.execute('SELECT * FROM drone;').fetchall()

def available():
    cur = db_connexion_select()
    return cur.execute('SELECT * FROM drone WHERE state == "IDLE";').fetchall()

def check_drone(serial_number):
    cur = db_connexion_select()
    return cur.execute('SELECT * FROM medication WHERE drone_serial == ?;', [serial_number]).fetchall()

def battery(serial_number):
    cur = db_connexion_select()
    return cur.execute('SELECT battery_capacity FROM drone WHERE serial_number == ?;', [serial_number]).fetchone()

def insert_drone(serial_number, model, weight_limit, battery_capacity, state):
    db = db_connexion()
    cursor = db.cursor()
    statement = "INSERT INTO drone(serial_number, model, weight_limit, battery_capacity, state) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(statement, [serial_number, model, weight_limit, battery_capacity, state])
    db.commit()
    return True

def insert_medication(name, weight, code, image, drone_serial):
    db = db_connexion()
    cursor = db.cursor()
    statement = "INSERT INTO medication(name, weight, code, image, drone_serial) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(statement, [name, weight, code, image, drone_serial])
    db.commit()
    return True

def drone(serial_number):
    db = db_connexion()
    cursor = db.cursor()
    drone = cursor.execute('SELECT weight_limit FROM drone WHERE serial_number == ?;', [serial_number]).fetchone()[0]
    return drone

def drone_state(serial_number):
    db = db_connexion()
    cursor = db.cursor()
    drone = cursor.execute('SELECT state FROM drone WHERE serial_number == ?;', [serial_number]).fetchone()[0]
    return drone

def drone_state_update(serial_number):
    db = db_connexion()
    cursor = db.cursor()
    statement = 'UPDATE drone SET state = "LOADING" WHERE serial_number == ?;'
    cursor.execute(statement, [serial_number])
    db.commit()
    return drone

def batterys():
    cur = db_connexion_select()
    drone = cur.execute('SELECT battery_capacity, serial_number FROM drone;').fetchall()
    return drone