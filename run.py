from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from database import add_donor, get_donor_by_email, update_donor, verify_hospital_password, calculate_distance, days_since, get_all_donors, is_eligible_to_donate, add_hospital, verify_hospital_password, get_donor_by_id, generate_qr_id, add_qr_user, get_qr_donor_by_qr_id, get_qr_donor_by_email, generate_qr, get_qr_donor_by_name_email, insert_emergency_need, get_all_emergency
from mail import send_email, happy_mail, happy_mail_2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secretkey"

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class Donor(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_data = get_donor_by_email(user_id)
    if user_data:
        return Donor(user_data['id'], user_data['name'], user_data['email'])
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        session['name'] = name
        session['email'] = email
        session['phone'] = phone
        return redirect(url_for("user_donor"))
    return render_template("register.html")

@app.route("/user_edit", methods=["GET", "POST"])
def user_donor():
    if request.method == "POST":
        donor_data = {
            "name": request.form['name'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "dob": request.form['dob'],
            "blood_group": request.form['blood_group'],
            "address_line": request.form['address_line'],
            "city": request.form['city'],
            "state": request.form['state'],
            "pincode": request.form['pincode'],
            "latitude": request.form['latitude'],
            "longitude": request.form['longitude'],
            "notify":int( 'notify' in request.form),
            "last_donated": request.form['last_donated'],
            "health_problems": request.form['health_problems']
        }

        print(donor_data)

        if not add_donor(donor_data):
            return render_template("user-edit-card.html", user=donor_data, errmsg="Donor already exists!")
        happy_mail(donor_data)
        happy_mail_2(donor_data)
        return render_template("post-regs.html")

    user = {
        'name': session.get('name'),
        'email': session.get('email'),
        'phone': session.get('phone'),
    }
    return render_template("user-edit-card.html", user=user)

@app.route("/save", methods=["POST"])
def save():
    donor_data = {
        "name": request.form['name'],
        "email": request.form['email'],
        "phone": request.form['phone'],
        "dob": request.form['dob'],
        "blood_group": request.form['blood_group'],
        "address_line": request.form['address_line'],
        "city": request.form['city'],
        "state": request.form['state'],
        "pincode": request.form['pincode'],
        "latitude": request.form['latitude'],
        "longitude": request.form['longitude'],
        "notify": int('notify' in request.form),
        "last_donated": request.form['last_donated'],
        "health_problems": request.form['health_problems']
    }
    update_donor(donor_data)

    print(not(get_qr_donor_by_email(donor_data['email'])))

    if not get_qr_donor_by_email(donor_data['email']):
        return render_template("post-login.html")
    return render_template("post-login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        donor = get_donor_by_email(email)
        if donor and donor.get('name') == name:
            donor_obj = Donor(donor['id'], donor['name'], donor['email'])
            print(login_user(donor_obj))
            print(donor)
            session['donor_id'] = donor['id']
            # login success
            # return render_template("user-edit-card2.html", user=donor)
            return render_template("user-dashboard.html", user=donor)
        return "Invalid login"
    return render_template("login.html")

@app.route("/redirect-to-edit-user", methods=["GET", "POST"])
def redirect_to_edit_user():
    donor_id = session.get('donor_id')
    if donor_id:
        donor = get_donor_by_id(donor_id)
        return render_template("user-edit-card2.html", user=donor)
    return render_template("login.html")

@app.route("/back-home", methods=["GET", "POST"])
def back_home():
    donor_id = session.get('donor_id')
    if donor_id:
        donor = get_donor_by_id(donor_id)
        return render_template("user-dashboard.html", user=donor)
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    session.pop('donor_id', None)
    session['donor_id'] = None
    session.clear()
    print(session.get('donor_id'))
    return redirect(url_for("home"))

##################################################################################

@app.route("/hospital", methods=["GET", "POST"]) 
def hospital_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        hospital = verify_hospital_password(email, password)
        print(hospital)
        if hospital:
            session["hospital_data"] = hospital
            print("here")
            return redirect(url_for('hospital_dashboard'))
        print("there")

        return render_template("hospital-login.html", error="Invalid credentials")

    return render_template("hospital-login.html")

@app.route("/hospital-dashboard")
def hospital_dashboard():
    print(session.get('hospital_data'))
    
    if session.get('hospital_data'):
        hospital = session.get('hospital_data')
        hospital_lat = hospital['latitude']
        hospital_lon = hospital['longitude']

        selected_group = request.args.get("blood_group")
        raw_donors = get_all_donors()
        processed_donors = []

        for donor in raw_donors:
            dist = (
                calculate_distance(hospital_lat, hospital_lon, donor['latitude'], donor['longitude'])
                if donor['latitude'] and donor['longitude'] else float('inf')
            )
            last_donated_days = days_since(donor.get('last_donated'))
            eligible = is_eligible_to_donate(donor.get('last_donated'))

            if not selected_group or donor['blood_group'] == selected_group:
                processed_donors.append({
                    "blood_group": donor["blood_group"],
                    "contact": donor["phone"],
                    "distance": dist,
                    "last_donated_days": last_donated_days,
                    "diseases": donor.get("health_problems", "None"),
                    "eligible": eligible
                })

        # Separate and sort
        eligible_donors = sorted([d for d in processed_donors if d['eligible']], key=lambda d: d['distance'])
        ineligible_donors = [d for d in processed_donors if not d['eligible']]

        # Take top 20 eligible donors
        top_eligible = eligible_donors[:20]

        if top_eligible:
            max_distance = top_eligible[-1]['distance']
        else:
            max_distance = float('inf')  # fallback if no eligible donors

        # Filter ineligible donors within that same radius
        nearby_ineligible = [d for d in ineligible_donors if d['distance'] <= max_distance]

        # Final list: eligible first, then ineligible — both within same radius
        final_donors = top_eligible + sorted(nearby_ineligible, key=lambda d: d['distance'])

        return render_template("hospital-dashboard.html", donors=final_donors)

    return redirect(url_for("hospital_login"))

@app.route("/sos", methods=['GET', 'POST'])
def sos():
    if session.get('hospital_data'):
        return render_template("get_bg.html")
    return redirect(url_for('hospital_login'))

@app.route("/sos-send", methods=['GET', 'POST'])
def sos_send():
    print(not session.get('hospital_data'))
    if not session.get('hospital_data'):
        return redirect(url_for('hospital_login'))

    if request.method == "POST":
        selected_group = request.form['blood_group']

        hospital = session.get('hospital_data')

        # Define hospital coordinates and message details
        hospital_lat = hospital['latitude']
        hospital_lon = hospital['longitude']
        hospital_address = hospital['address']
        hospital_phone = hospital['phone']
        location_url = f"https://www.google.com/maps?q={hospital_lat},{hospital_lon}"

        # Get all donors and filter by blood group, eligibility, notify=1
        all_donors = get_all_donors()
        filtered = []

        for donor in all_donors:
            if donor['blood_group'] != selected_group:
                continue
            if not is_eligible_to_donate(donor.get('last_donated')):
                continue
            if int(donor.get('notify', 1)) != 1:
                continue
            if not donor.get('latitude') or not donor.get('longitude'):
                continue

            distance = calculate_distance(hospital_lat, hospital_lon, donor['latitude'], donor['longitude'])
            donor['distance'] = distance
            filtered.append(donor)

        # Sort by distance and take top 20
        nearest_20 = sorted(filtered, key=lambda d: d['distance'])[:20]

        # Send WhatsApp to each
        for donor in nearest_20:
            send_email(
                to_email=donor['email'],
                blood_group=donor['blood_group'],
                location_url=location_url,
                address=hospital_address,
                call_number=hospital_phone
            )
        return render_template("hospital-post-sos.html")

    return redirect(url_for("hospital_dashboard"))

@app.route("/hospital-register", methods=['POST', 'GET'])
def hospital_register():
    if request.method == "POST":
        name = request.form['name']
        if not add_hospital(
                request.form['name'],
                request.form['email'],
                request.form['password'],
                request.form['latitude'],
                request.form['longitude'],
                request.form['address_line'] + ', ' + request.form['city'] + ', ' + request.form['state'] + ', ' + request.form['pincode'],
                request.form['phone']
            ):
            return render_template("hospital-register.html", user=[], errmsg="Hospital with that mail already exsist")
        return render_template("hospital-post-regs.html")
    return render_template("hospital-register.html", user=[])

@app.route("/hospital-logout")
def hospital_logout():
    session.pop('hospital_data', None)
    session.get('hospital_data')
    return redirect(url_for('hospital_login'))

############################################################################

@app.route('/qr-register', methods=["POST", "GET"])
def qr_register():
    if session.get("donor_id"):
        user = get_donor_by_id(session.get("donor_id"))
        donor = get_qr_donor_by_name_email(user['name'], user['email'])
        if not donor:
            donor1 = user
        user = {}
        if request.method == "POST":
            if donor:
                qr = donor['qr_code_id']
            else:
                qr = generate_qr_id()
            user_data = {
                "name": request.form['name'],
                "email": request.form['email'],
                "phone": request.form['phone'],
                "age": request.form['age'],
                "blood_group": request.form['blood_group'],
                "address_line": request.form['address_line'],
                "city": request.form['city'],
                "state": request.form['state'],
                "pincode": request.form['pincode'],
                "diabetes": 'diabetes' in request.form,
                "hypertension": 'hypertension' in request.form,
                "asthma": 'asthma' in request.form,
                "epilepsy": 'epilepsy' in request.form,
                "heart_disease": 'heart_disease' in request.form,
                "kidney_disease": 'kidney_disease' in request.form,
                "bleeding_disorder": 'bleeding_disorder' in request.form,
                "organ_transplant": 'organ_transplant' in request.form,
                "mental_disorder": 'mental_disorder' in request.form,
                "additional_conditions": request.form['additional_conditions'],
                "first_aid": request.form['first_aid'],
                "emergency_contact_name": request.form['emergency_contact_name'],
                "emergency_contact_number": request.form['emergency_contact_number'],
                "emergency_contact_relation": request.form['emergency_contact_relation'],
                "family_contact_name": request.form['family_contact_name'],
                "family_contact_number": request.form['family_contact_number'],
                "family_contact_relation": request.form['family_contact_relation'],
                "doctor_name": request.form['doctor_name'],
                "doctor_specialization": request.form['doctor_specialization'],
                "doctor_contact_number": request.form['doctor_contact_number'],
                "doctor_email": request.form['doctor_email'],
                "qr_code_id": qr
            }

            static_folder = os.path.join(os.path.dirname(__file__), 'static/qrcodes')
            file_path = os.path.join(static_folder, f"{qr}.png")
            if donor:
                if os.path.isfile(file_path):
                    return render_template("qr-display.html", id=qr)
                else:
                    generate_qr(f"https://eazyfencer.pythonanywhere.com/qr-id={qr}", qr)
                    return render_template("qr-display.html", id=qr)
            
            if add_qr_user(user_data) == False:
                return render_template("qr-register.html", user=user_data, errmsg="User already exists with this email and name!")

            return render_template("qr-display.html", id=qr)
        if not donor:
            return render_template("qr-register.html", user=donor1)
        else:
            return render_template("qr-register.html", user = donor)
    return render_template('login.html')


@app.route('/qr-id=<qr_id>')
def get_patient_by_qr(qr_id):

    user = get_qr_donor_by_qr_id(qr_id)

    if user:
        return render_template('patient-details.html', user=user)
    else:
        return "No patient found with this QR ID.", 404
    
@app.route('/status')
def status():
    if current_user.is_authenticated:
        if session.get('hospital_data'):
            return f"""Logged in as: {current_user.email}\n
            Logged in as: {session.get('hospital_data')['name']}"""
        return f"Logged in as: {current_user.email}"
    if session.get('donor_id'):
        if session.get('hospital_data'):
            return f""""Logged in as: {session.get('donor_id')}\n   
            Logged in as: {session.get('hospital_data')['name']}"""
        return f"Logged in as: {session.get('donor_id')} with id"
    if session.get('hospital_data'):
        return f"Logged in as: {session.get('hospital_data')['name']}"
    return "Not logged in"

@app.route('/view-qr')
def view_qr():
    if session.get('donor_id'):
        donor = get_donor_by_id(session.get('donor_id'))
        email = donor['email']
        qr_donor = get_qr_donor_by_email(email)
        qr = qr_donor['qr_code_id']
        qr_path = os.path.join('static/qrcodes', f"{qr}.png")
        print('here')
        if os.path.exists(qr_path):
            return render_template('qr-display.html', id=qr)
        else:
            generate_qr(f"https://eazyfencer.pythonanywhere.com/qr-id={qr}", qr)
            return "refresh again to get qr"
    return "Not logged in"

##########################################

@app.route("/manage-emergency", methods=["POST", "GET"])
def manage_emergency():
    if not session.get('hospital_data'):
        return redirect(url_for('hospital_login'))
    if request.method == "POST":
        return render_template("manage-emergency.html")

@app.route("/add-emergency", methods=["POST", "GET"])
def add_emergency():
    if not session.get('hospital_data'):
        return redirect(url_for('hospital_login'))
    if request.method == "POST":
        return render_template("add-emergency.html")
    
@app.route("/add-emergency-need", methods=["POST", "GET"])
def add_emergency_need():
    if not session.get('hospital_data'):
        return redirect(url_for('hospital_login'))
    if request.method == "POST":
        data = session.get('hospital_data')
        blood_group = request.form['blood_group']
        status = request.form['status']
        date = request.form['date']
        time = request.form['time']
        phone = data['phone']
        lat = data['latitude']
        log = data['longitude']
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        hospital_id = data['id']
        insert_emergency_need(blood_group, status, dt, phone, lat, log, hospital_id)

        return render_template("message.html", message="Emergency Request Added")
    
@app.route("/view-emergency", methods=["POST", "GET"])
def view_emergency():
    if not session.get('hospital_data'):
        return redirect(url_for('hospital_login'))
    if request.method == "POST":
        data = get_all_emergency(session.get('hospital_data')['id'])

        print(data)

        return render_template("view-emergency.html", emergencies=data)

@app.route('/ss')
def ss():
    return render_template('ss.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
