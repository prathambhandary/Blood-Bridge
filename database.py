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
    c.execute( """
    CREATE TABLE IF NOT EXISTS qr_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        address_line TEXT NOT NULL,
        city TEXT,
        state TEXT,
        pincode TEXT,
        diabetes BOOLEAN DEFAULT 0,
        hypertension BOOLEAN DEFAULT 0,
        asthma BOOLEAN DEFAULT 0,
        epilepsy BOOLEAN DEFAULT 0,
        heart_disease BOOLEAN DEFAULT 0,
        kidney_disease BOOLEAN DEFAULT 0,
        bleeding_disorder BOOLEAN DEFAULT 0,
        organ_transplant BOOLEAN DEFAULT 0,
        mental_disorder BOOLEAN DEFAULT 0,
        additional_conditions TEXT,
        first_aid TEXT,
        emergency_contact_name TEXT,
        emergency_contact_number TEXT,
        emergency_contact_relation TEXT,
        family_contact_name TEXT,
        family_contact_number TEXT,
        family_contact_relation TEXT,
        doctor_name TEXT,
        doctor_specialization TEXT,
        doctor_contact_number TEXT,
        doctor_email TEXT,
        qr_code_id TEXT UNIQUE,
        age INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

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

def get_donor_by_id(id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM donors WHERE id = ?", (id,))
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
    
import qrcode
import uuid
import os
from PIL import Image, ImageDraw, ImageFont

def generate_qr(data, qr_id):
    # --- QR Generation ---
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,  # Higher resolution
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # --- Load Fonts ---
    try:
        font_big = ImageFont.truetype("fonts/Inter-Bold.ttf", 40)
        font_small = ImageFont.truetype("fonts/Inter-Bold.ttf", 24)
        font_tiny = ImageFont.truetype("fonts/Inter-Regular.ttf", 16)
    except:
        font_big = font_small = font_tiny = ImageFont.load_default()

    # --- Text Content ---
    title = "Blood Bridge Health ID"
    subtitle = "Emergency QR Access"
    qr_code_id_text = f"QR ID: {qr_id}"

    # --- Measure Texts ---
    dummy_draw = ImageDraw.Draw(img_qr)
    def get_size(text, font):  # helper
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    title_w, title_h = get_size(title, font_big)
    subtitle_w, subtitle_h = get_size(subtitle, font_small)
    id_w, id_h = get_size(qr_code_id_text, font_tiny)

    # --- Final Canvas ---
    spacing = 20
    new_width = max(img_qr.size[0], title_w, subtitle_w, id_w) + 40
    new_height = title_h + subtitle_h + spacing * 3 + img_qr.size[1] + id_h + spacing * 3

    final_img = Image.new("RGB", (new_width, new_height), "white")
    draw = ImageDraw.Draw(final_img)

    # --- Drawing ---
    y = spacing
    draw.text(((new_width - title_w) // 2, y), title, fill="#aa001e", font=font_big)
    y += title_h + spacing // 2
    draw.text(((new_width - subtitle_w) // 2, y), subtitle, fill="#ff5722", font=font_small)
    y += subtitle_h + spacing

    qr_x = (new_width - img_qr.size[0]) // 2
    final_img.paste(img_qr, (qr_x, y))
    y += img_qr.size[1] + spacing

    draw.text(((new_width - id_w) // 2, y), qr_code_id_text, fill="#888888", font=font_tiny)

    # --- Save Final ---
    final_img.save(f"static/qrcodes/{qr_id}.png")

def generate_qr_id(output_dir="static/qrcodes"):
    import sqlite3

    def is_qr_unique(qr_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM qr_users WHERE qr_code_id = ?", (qr_id,))
        result = cursor.fetchone()
        conn.close()
        return result is None  # True if ID is unique

    while True:
        # Generate a unique ID
        unique_id = str(uuid.uuid4())
        if is_qr_unique(unique_id):
            break  # Exit loop if the ID is unique
    
    generate_qr(f"https://eazyfencer.pythonanywhere.com/qr-id={unique_id}", unique_id)
    return unique_id

def add_qr_user(user_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check for duplicate email + name
    cursor.execute("SELECT * FROM qr_users WHERE email=? AND name=?", (user_data["email"], user_data["name"]))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False  # User already exists

    cursor.execute("""
        INSERT INTO qr_users (
            name, email, phone, age, blood_group,
            address_line, city, state, pincode,
            diabetes, hypertension, asthma, epilepsy,
            heart_disease, kidney_disease, bleeding_disorder,
            organ_transplant, mental_disorder, additional_conditions,
            first_aid, emergency_contact_name, emergency_contact_number,
            emergency_contact_relation, family_contact_name, family_contact_number,
            family_contact_relation, doctor_name, doctor_specialization,
            doctor_contact_number, doctor_email, qr_code_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data["name"], user_data["email"], user_data["phone"], user_data["age"], user_data["blood_group"],
        user_data["address_line"], user_data["city"], user_data["state"], user_data["pincode"],
        int(user_data["diabetes"]), int(user_data["hypertension"]), int(user_data["asthma"]), int(user_data["epilepsy"]),
        int(user_data["heart_disease"]), int(user_data["kidney_disease"]), int(user_data["bleeding_disorder"]),
        int(user_data["organ_transplant"]), int(user_data["mental_disorder"]), user_data["additional_conditions"],
        user_data["first_aid"], user_data["emergency_contact_name"], user_data["emergency_contact_number"],
        user_data["emergency_contact_relation"], user_data["family_contact_name"], user_data["family_contact_number"],
        user_data["family_contact_relation"], user_data["doctor_name"], user_data["doctor_specialization"],
        user_data["doctor_contact_number"], user_data["doctor_email"], user_data["qr_code_id"]
    ))

    conn.commit()
    conn.close()
    return True

def get_donor_by_qr_id(qr_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_users WHERE qr_code_id = ?", (qr_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "blood_group": row[4],
            "address_line": row[5],
            "city": row[6],
            "state": row[7],
            "pincode": row[8],
            "diabetes": row[9],
            "hypertension": row[10],
            "asthma": row[11],
            "epilepsy": row[12],
            "heart_disease": row[13],
            "kidney_disease": row[14],
            "bleeding_disorder": row[15],
            "organ_transplant": row[16],
            "mental_disorder": row[17],
            "additional_conditions": row[18],
            "first_aid": row[19],
            "emergency_contact_name": row[20],
            "emergency_contact_number": row[21],
            "emergency_contact_relation": row[22],
            "family_contact_name": row[23],
            "family_contact_number": row[24],
            "family_contact_relation": row[25],
            "doctor_name": row[26],
            "doctor_specialization": row[27],
            "doctor_contact_number": row[28],
            "doctor_email": row[29],
            "qr_code_id": row[30],
            "age": row[31],
            "last_updated": row[32],
        }
    return None

def get_qr_donor_by_email(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "blood_group": row[4],
            "address_line": row[5],
            "city": row[6],
            "state": row[7],
            "pincode": row[8],
            "diabetes": row[9],
            "hypertension": row[10],
            "asthma": row[11],
            "epilepsy": row[12],
            "heart_disease": row[13],
            "kidney_disease": row[14],
            "bleeding_disorder": row[15],
            "organ_transplant": row[16],
            "mental_disorder": row[17],
            "additional_conditions": row[18],
            "first_aid": row[19],
            "emergency_contact_name": row[20],
            "emergency_contact_number": row[21],
            "emergency_contact_relation": row[22],
            "family_contact_name": row[23],
            "family_contact_number": row[24],
            "family_contact_relation": row[25],
            "doctor_name": row[26],
            "doctor_specialization": row[27],
            "doctor_contact_number": row[28],
            "doctor_email": row[29],
            "qr_code_id": row[30],
            "age": row[31],
            "last_updated": row[32],
        }
    return None

# Run once to set up the DB
if __name__ == "__main__":
    create_table()
    print("Database initialized.")
    print(get_all_donors())