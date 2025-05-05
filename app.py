# app.py

from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db
from openai_handler import generate_kannada_translation
import os
from dotenv import load_dotenv

load_dotenv()

# Firebase init
cred = credentials.Certificate(eval(os.getenv("FIREBASE_JSON")))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]
        user_ref = db.reference(f"users/{mobile}")
        user_data = user_ref.get()
        if user_data and user_data["password"] == password:
            session["user"] = user_data["name"]
            session["mobile"] = mobile
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    mobile = session.get("mobile")
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    if request.method == "POST":
        user_input = request.form["message"]
        if credit > 0 and user_input.strip():
            response = generate_kannada_translation(user_input)
            user_ref.update({"credit": credit - 1})
            credit -= 1
            return render_template("dashboard.html", name=session["user"], credit=credit, user_input=user_input, response=response)
        else:
            error = "No credits left. Please contact admin."
            return render_template("dashboard.html", name=session["user"], credit=credit, error=error)

    return render_template("dashboard.html", name=session["user"], credit=credit)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
