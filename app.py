import os
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db
from openai_handler import generate_kannada_translation

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Firebase setup
firebase_cert_json = os.environ.get("FIREBASE_JSON")
if not firebase_cert_json:
    raise Exception("FIREBASE_JSON not set in Railway variables.")

import json
cred = credentials.Certificate(json.loads(firebase_cert_json))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        user_ref = db.reference(f'users/{mobile}')
        user = user_ref.get()
        if user and user['password'] == password:
            session['user'] = user['name']
            session['mobile'] = mobile
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    name = session["user"]
    mobile = session["mobile"]
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    response = None
    if request.method == 'POST':
        question = request.form['question']
        if credit > 0:
            try:
                response = generate_kannada_translation(question)
                credit -= 1
                user_ref.update({"credit": credit})
            except Exception as e:
                response = f"Error: {str(e)}"
        else:
            response = "You don't have enough credits."

    return render_template("dashboard.html", name=name, credit=credit, response=response)

@app.route('/admin')
def admin():
    users = db.reference("users").get()
    return render_template("admin.html", users=users)

@app.route('/update_user', methods=["POST"])
def update_user():
    mobile = request.form["mobile"]
    name = request.form["name"]
    password = request.form["password"]
    credit = int(request.form["credit"])
    db.reference(f"users/{mobile}").update({
        "name": name,
        "password": password,
        "credit": credit
    })
    return redirect(url_for("admin"))

@app.route('/add_user', methods=["POST"])
def add_user():
    mobile = request.form["mobile"]
    name = request.form["name"]
    password = request.form["password"]
    credit = int(request.form["credit"])
    db.reference(f"users/{mobile}").set({
        "name": name,
        "password": password,
        "credit": credit
    })
    return redirect(url_for("admin"))

@app.route('/delete_user', methods=["POST"])
def delete_user():
    mobile = request.form["mobile"]
    db.reference(f"users/{mobile}").delete()
    return redirect(url_for("admin"))

if __name__ == '__main__':
    app.run(debug=True)
