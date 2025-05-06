from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from firebase_config import firebase_auth, firebase_db
from openai_handler import get_kannada_translation
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "defaultsecret")

ADMIN_NUMBER = "8830720742"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        ref = firebase_db.reference("/users")
        users = ref.get() or {}

        for uid, user in users.items():
            if user["mobile"] == mobile and user["password"] == password:
                session["name"] = user["name"]
                session["mobile"] = user["mobile"]
                session["credits"] = user["credits"]
                return redirect("/dashboard")

        return render_template("login.html", error="Invalid mobile or password")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "mobile" not in session:
        return redirect("/login")
    
    if session["mobile"] == ADMIN_NUMBER:
        return redirect("/admin")

    return render_template("dashboard.html", name=session["name"], credits=session["credits"])

@app.route("/admin")
def admin_panel():
    if "mobile" not in session or session["mobile"] != ADMIN_NUMBER:
        return redirect("/login")

    ref = firebase_db.reference("/users")
    users = ref.get() or {}
    return render_template("admin.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    if "mobile" not in session or session["mobile"] != ADMIN_NUMBER:
        return redirect("/login")

    data = request.form
    user_data = {
        "name": data["name"],
        "mobile": data["mobile"],
        "password": data["password"],
        "credits": int(data["credits"])
    }

    ref = firebase_db.reference("/users")
    ref.push(user_data)
    return redirect("/admin")

@app.route("/update_user/<uid>", methods=["POST"])
def update_user(uid):
    if "mobile" not in session or session["mobile"] != ADMIN_NUMBER:
        return redirect("/login")

    data = request.form
    updates = {
        "name": data["name"],
        "password": data["password"],
        "credits": int(data["credits"])
    }

    ref = firebase_db.reference(f"/users/{uid}")
    ref.update(updates)
    return redirect("/admin")

@app.route("/delete_user/<uid>")
def delete_user(uid):
    if "mobile" not in session or session["mobile"] != ADMIN_NUMBER:
        return redirect("/login")

    ref = firebase_db.reference(f"/users/{uid}")
    ref.delete()
    return redirect("/admin")

@app.route("/ask", methods=["POST"])
def ask():
    if "mobile" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_input = request.json.get("question", "").strip()
    if not user_input or not user_input[0].isascii():
        return jsonify({"error": "Please ask your question in English."}), 400

    ref = firebase_db.reference("/users")
    users = ref.get() or {}
    user = next((uid for uid, u in users.items() if u["mobile"] == session["mobile"]), None)

    if not user or users[user]["credits"] <= 0:
        return jsonify({"error": "No credits left"}), 403

    try:
        result = get_kannada_translation(user_input)
        firebase_db.reference(f"/users/{user}/credits").set(users[user]["credits"] - 1)
        session["credits"] -= 1
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": "Something went wrong: " + str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
