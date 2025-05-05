import os
from flask import Flask, render_template, request, redirect, url_for, session
from firebase_config import db
from openai_handler import generate_kannada_translation
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        user_ref = db.reference(f"users/{mobile}")
        user = user_ref.get()

        if user and user.get("password") == password:
            session["user"] = user["name"]
            session["mobile"] = mobile
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid mobile or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    mobile = session.get("mobile")
    user_data = db.reference(f"users/{mobile}").get()
    credit = user_data.get("credit", 0)
    return render_template("dashboard.html", name=session["user"], credit=credit)

@app.route("/generate", methods=["POST"])
def generate():
    if "user" not in session:
        return redirect(url_for("login"))

    question = request.form["question"]
    mobile = session.get("mobile")
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    if credit <= 0:
        return {"response": "You are out of credits. Please contact support."}

    result = generate_kannada_translation(question)

    # deduct 1 credit
    user_ref.update({"credit": credit - 1})

    return {"response": result}

if __name__ == "__main__":
    app.run(debug=True)
