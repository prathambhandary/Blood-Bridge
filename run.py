from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from database import add_donor, get_donor_by_email, update_donor, verify_hospital_password, calculate_distance, days_since, get_all_donors, is_eligible_to_donate
from mail import send_email

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
    return render_template("post-regs.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        donor = get_donor_by_email(email)
        if donor and donor.get('name') == name:
            donor_obj = Donor(donor['id'], donor['name'], donor['email'])
            login_user(donor_obj)
            return render_template("user-edit-card2.html", user=donor)
        return "Invalid login"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
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
            session['hospital_id'] = hospital['id']
            print(hospital['id'])
            session['hospital_name'] = hospital['name']
            print("here")
            return redirect(url_for('hospital_dashboard'))
        print("there")

        return render_template("hospital-login.html", error="Invalid credentials")

    return render_template("hospital-login.html")

@app.route("/hospital-dashboard")
def hospital_dashboard():
    print(session.get('hospital_id'))
    if session.get('hospital_id'):
        hospital_lat = 13.3521
        hospital_lon = 74.7917

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

        return render_template("hospital-dashboard.html", donors=final_donors, selected_group=selected_group)

    return redirect(url_for("hospital_login"))

@app.route("/sos", methods=['GET', 'POST'])
def sos():
    if session.get('hospital_id'):
        return render_template("get_bg.html")
    return redirect(url_for('hospital_login'))

@app.route("/sos-send", methods=['GET', 'POST'])
def sos_send():
    print(not session.get('hospital_id'))
    if not session.get('hospital_id'):
        return redirect(url_for('hospital_login'))

    if request.method == "POST":
        selected_group = request.form['blood_group']

        # Define hospital coordinates and message details
        hospital_lat = 13.3521
        hospital_lon = 74.7917
        hospital_address = "KMC Hospital, Manipal"
        hospital_phone = "1234567890"
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
        return redirect(url_for('hospital_dashboard'))

    return redirect(url_for("hospital_dashboard"))


@app.route("/hospital-logout")
def hospital_logout():
    session.pop('hospital_id', None)
    session.get('hospital_id')
    return redirect(url_for('hospital_login'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
