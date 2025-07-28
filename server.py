from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from database import insert_user, generate_qr_id, get_user_by_email, update_user, get_user_by_qr_id  # ➕ You'll define get_user_by_email

app = Flask(__name__)
app.secret_key = "secretkey"

# Setup login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_email(user_id)  # This can be get_user_by_id if you store by ID
    if user_data:
        return User(user_data['id'], user_data['name'], user_data['email'])
    return None


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone_no = request.form['phone']
        session['name']  = name     
        session['email']  = email
        session['phone']  = phone_no
        #save to database here
        return redirect(url_for("user_edit"))
    return render_template("register.html")

@app.route("/user_edit",    methods=["POST", "GET"])
def user_edit():
    if request.method == "POST":
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
        
        if insert_user(user_data) == False:
            return render_template("user-edit-card.html", user=user_data, errmsg="User already exists with this email and name!")

        return render_template("qr.html", id=qr)
    
    user = {
        'name': session.get('name'),
        'email': session.get('email'),
        'phone': session.get('phone'),
    }
    return render_template("user-edit-card.html", user=user)

@app.route("/save", methods=["POST", "GET"])
def save():
    if request.method == "POST":
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
            "diabetes": int('diabetes' in request.form),
            "hypertension": int('hypertension' in request.form),
            "asthma": int('asthma' in request.form),
            "epilepsy": int('epilepsy' in request.form),
            "heart_disease": int('heart_disease' in request.form),
            "kidney_disease": int('kidney_disease' in request.form),
            "bleeding_disorder": int('bleeding_disorder' in request.form),
            "organ_transplant": int('organ_transplant' in request.form),
            "mental_disorder": int('mental_disorder' in request.form),
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
            "qr_code_id": request.form['qr_code_id']
        }
        update_user(user_data)
        return render_template("qr.html", id=request.form['qr_code_id'])
    return redirect(url_for("user_edit"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form['name']
        email = request.form["email"]
        user = get_user_by_email(email)
        if user and user.get('name') == name:
            user_obj = User(user["id"], user["name"], user["email"])
            login_user(user_obj)
            return render_template("user-edit-card2.html", user=user)
        return "Invalid login"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/qr-id=<qr_id>')
def get_patient_by_qr(qr_id):

    user = get_user_by_qr_id(qr_id)

    if user:
        return render_template('patient-details.html', user=user)
    else:
        return "No patient found with this QR ID.", 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)