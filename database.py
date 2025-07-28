import sqlite3
from datetime import datetime

DB_NAME = 'scan2save.db'

# SQL schema
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
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
"""

# Create DB and tables
def create_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
    except sqlite3.Error as e:
        "Failed"
    finally:
        conn.close()

# Insert a user
import sqlite3

def insert_user(user_data):
    conn = sqlite3.connect("scan2save.db")
    cursor = conn.cursor()

    # Check for duplicate email + name
    cursor.execute("SELECT * FROM users WHERE email=? AND name=?", (user_data["email"], user_data["name"]))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False  # User already exists

    cursor.execute("""
        INSERT INTO users (
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
    title = "Scan2Save Health ID"
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
    draw.text(((new_width - title_w) // 2, y), title, fill="#10349e", font=font_big)
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
        conn = sqlite3.connect("scan2save.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE qr_code_id = ?", (qr_id,))
        result = cursor.fetchone()
        conn.close()
        return result is None  # True if ID is unique

    while True:
        # Generate a unique ID
        unique_id = str(uuid.uuid4())
        if is_qr_unique(unique_id):
            break  # Exit loop if the ID is unique
    
    generate_qr(f"http://192.168.43.131:5000/qr-id={unique_id}", unique_id)
    return unique_id

def get_user_by_email(email):
    conn = sqlite3.connect("scan2save.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
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

def update_user(user_data):
    try:
        conn = sqlite3.connect("scan2save.db")
        cursor = conn.cursor()

        update_query = """
        UPDATE users SET
            name = ?,
            email = ?,
            phone = ?,
            age = ?,
            blood_group = ?,
            address_line = ?,
            city = ?,
            state = ?,
            pincode = ?,
            diabetes = ?,
            hypertension = ?,
            asthma = ?,
            epilepsy = ?,
            heart_disease = ?,
            kidney_disease = ?,
            bleeding_disorder = ?,
            organ_transplant = ?,
            mental_disorder = ?,
            additional_conditions = ?,
            first_aid = ?,
            emergency_contact_name = ?,
            emergency_contact_number = ?,
            emergency_contact_relation = ?,
            family_contact_name = ?,
            family_contact_number = ?,
            family_contact_relation = ?,
            doctor_name = ?,
            doctor_specialization = ?,
            doctor_contact_number = ?,
            doctor_email = ?
        WHERE qr_code_id = ?
        """
        values = (
            user_data["name"],
            user_data["email"],
            user_data["phone"],
            user_data["age"],
            user_data["blood_group"],
            user_data["address_line"],
            user_data["city"],
            user_data["state"],
            user_data["pincode"],
            user_data["diabetes"],
            user_data["hypertension"],
            int(user_data["asthma"]),
            user_data["epilepsy"],
            user_data["heart_disease"],
            user_data["kidney_disease"],
            user_data["bleeding_disorder"],
            user_data["organ_transplant"],
            user_data["mental_disorder"],
            user_data["additional_conditions"],
            user_data["first_aid"],
            user_data["emergency_contact_name"],
            user_data["emergency_contact_number"],
            user_data["emergency_contact_relation"],
            user_data["family_contact_name"],
            user_data["family_contact_number"],
            user_data["family_contact_relation"],
            user_data["doctor_name"],
            user_data["doctor_specialization"],
            user_data["doctor_contact_number"],
            user_data["doctor_email"],
            user_data["qr_code_id"]
        )

        cursor.execute("SELECT * FROM users WHERE qr_code_id = ?", (user_data["qr_code_id"],))
        result = cursor.fetchone()
        if not result:
            "failed"


        cursor.execute(update_query, values)
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        return False

def print_all_users():
    import sqlite3

    try:
        conn = sqlite3.connect("scan2save.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        # Get column names
        column_names = [desc[0] for desc in cursor.description]

        print(f"📦 Total records: {len(rows)}\n" + "=" * 60)

        for idx, row in enumerate(rows, 1):
            print(f"\n👤 User {idx}")
            print("-" * 40)
            for col, val in zip(column_names, row):
                print(f"{col:25}: {val}")
            print("-" * 40)

    except sqlite3.Error as e:
        "failed"
    finally:
        conn.close()

def get_user_by_qr_id(qr_id):
    conn = sqlite3.connect("scan2save.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE qr_code_id = ?", (qr_id,))
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

import os
import sqlite3

def sync_qr_images(qr_folder="static/qrcodes", db_path="scan2save.db"):
    # 1. Get all QR IDs from DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT qr_code_id FROM users")
    db_qr_ids = {row[0] for row in cursor.fetchall()}
    conn.close()

    # 2. Get all QR image filenames in the folder
    folder_qr_ids = {
        fname.replace(".png", "") for fname in os.listdir(qr_folder) if fname.endswith(".png")
    }

    # 3. Find missing QR codes (exist in DB, not in folder)
    missing_qr_ids = db_qr_ids - folder_qr_ids

    # 4. Find extra QR codes (exist in folder, not in DB)
    extra_qr_ids = folder_qr_ids - db_qr_ids

    print(f"Missing QR IDs (to generate): {missing_qr_ids}")
    print(f"Extra QR IDs (to delete): {extra_qr_ids}")

    # 5. Generate missing QR codes
    for qr_id in missing_qr_ids:
        url = f"http://192.168.43.131:5000/qr-id={qr_id}"
        generate_qr(url, qr_id)
        print(f"✅ Generated QR: {qr_id}")

    # 6. Delete extra QR codes
    for qr_id in extra_qr_ids:
        path = os.path.join(qr_folder, f"{qr_id}.png")
        try:
            os.remove(path)
            print(f"🗑️ Deleted extra QR: {qr_id}")
        except Exception as e:
            print(f"⚠️ Error deleting {qr_id}.png: {e}")

sync_qr_images()
print_all_users()