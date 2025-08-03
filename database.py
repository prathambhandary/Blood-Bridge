import sqlite3

DATABASE = "blood_bridge.db"

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            dob TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            address_line TEXT,
            city TEXT,
            state TEXT,
            pincode TEXT,
            latitude REAL,
            longitude REAL,
            notify INTEGER DEFAULT 1,
            last_donated TEXT,
            health_problems TEXT
        );
    ''')
    c.execute( """    
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            certified INTEGER DEFAULT 0
    );""")

    conn.commit()
    conn.close()

def add_donor(data):
    if get_donor_by_email(data['email']):
        return False  # already exists

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO donors (
            name, email, phone, dob, blood_group,
            address_line, city, state, pincode,
            latitude, longitude, notify,
            last_donated, health_problems
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['email'],
        data['phone'],
        data['dob'],
        data['blood_group'],
        data.get('address_line'),
        data.get('city'),
        data.get('state'),
        data.get('pincode'),
        float(data['latitude']) if data.get('latitude') not in [None, ''] else None,
        float(data['longitude']) if data.get('longitude') not in [None, ''] else None,
        int(data.get('notify', 1)) if str(data.get('notify')).isdigit() else 1,
        data.get('last_donated'),
        data.get('health_problems')
    ))
    conn.commit()
    conn.close()
    return True

def get_donor_by_email(email):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM donors WHERE email = ?", (email,))
    donor = c.fetchone()
    conn.close()
    return dict(donor) if donor else None

def update_donor(data):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        UPDATE donors SET
            name = ?, phone = ?, dob = ?, blood_group = ?,
            address_line = ?, city = ?, state = ?, pincode = ?,
            latitude = ?, longitude = ?, notify = ?,
            last_donated = ?, health_problems = ?
        WHERE email = ?
    ''', (
        data['name'],
        data['phone'],
        data['dob'],
        data['blood_group'],
        data.get('address_line'),
        data.get('city'),
        data.get('state'),
        data.get('pincode'),
        float(data['latitude']) if data.get('latitude') not in [None, ''] else None,
        float(data['longitude']) if data.get('longitude') not in [None, ''] else None,
        int(data.get('notify', 1)) if str(data.get('notify')).isdigit() else 1,
        data.get('last_donated'),
        data.get('health_problems'),
        data['email']
    ))
    conn.commit()
    conn.close()

def get_all_donors():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM donors')
    donors = c.fetchall()
    conn.close()
    return [dict(row) for row in donors]

import sqlite3

def get_hospital_by_email(email):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM hospitals WHERE email = ?", (email,))
    hospital = cur.fetchone()
    conn.close()
    return dict(hospital) if hospital else None

def verify_hospital_password(email, password):
    hospital = get_hospital_by_email(email)
    if hospital and hospital['password'] == password and hospital['certified'] == 1:
        return hospital
    return None

def add_hospital(name, email, password, lat, log, address, phone):
    if get_hospital_by_email(email):
        return False
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO hospitals (name, email, password, latitude, longitude, address, phone, certified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, password, float(lat), float(log), address, phone, 0))
    conn.commit()
    conn.close()
    return True

from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 1)

def days_since(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return (datetime.now() - date).days
    except:
        return "N/A"

def is_eligible_to_donate(last_donated_date_str):
    if not last_donated_date_str:
        return True  # No record means never donated — eligible
    try:
        last_donated = datetime.strptime(last_donated_date_str, "%Y-%m-%d")
        return (datetime.now() - last_donated).days >= 90
    except:
        return False  # Invalid date format


# Run once to set up the DB
if __name__ == "__main__":
    create_table()
    print("Database initialized.")
    print(get_all_donors())
    