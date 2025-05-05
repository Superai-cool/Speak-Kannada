from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db
from openai_handler import generate_kannada_translation
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

cred = credentials.Certificate(eval(os.environ.get("FIREBASE_JSON")))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        ref = db.reference(f"users/{mobile}")
        user_data = ref.get()

        if user_data and user_data["password"] == password:
            session["user"] = user_data["name"]
            session["mobile"] = mobile

            if mobile == "8830720742":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    mobile = session.get("mobile")
    user_data = db.reference(f"users/{mobile}").get()
    credit = user_data.get("credit", 0)
    return render_template("dashboard.html", name=session["user"], credit=credit)


@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return "Unauthorized", 401

    user_input = request.json.get("user_input")
    mobile = session.get("mobile")
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    if credit <= 0:
        return {"error": "No credits left."}, 403

    response = generate_kannada_translation(user_input)

    # Deduct credit if not admin
    if mobile != "8830720742":
        user_ref.update({"credit": credit - 1})

    return {"response": response}


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    if "user" not in session or session.get("mobile") != "8830720742":
        return redirect(url_for("login"))
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
