from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from firebase_config import firebase_db
from openai_handler import generate_kannada_translation
import re
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

admin_numbers = ["9876543210", "8830720742"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]
        users_ref = firebase_db.reference("/users")
        users = users_ref.get()

        for uid, user in users.items():
            if user["mobile"] == mobile and user["password"] == password:
                session["name"] = user["name"]
                session["mobile"] = mobile
                session["credits"] = user["credits"]
                session["is_admin"] = mobile in admin_numbers
                return redirect(url_for("dashboard"))

        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["name"], credits=session["credits"])

@app.route("/process", methods=["POST"])
def process():
    if "mobile" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    question = request.json.get("question", "").strip()

    if not re.match(r'^[A-Za-z0-9 ,?!.]+$', question):
        return jsonify({"error": "Please ask your question in English only."}), 400

    credits = int(session["credits"])
    if credits <= 0 and not session.get("is_admin"):
        return jsonify({"error": "You have run out of credits!"}), 403

    result = generate_kannada_translation(question)

    if not session.get("is_admin"):
        session["credits"] -= 1
        user_ref = firebase_db.reference("/users").order_by_child("mobile").equal_to(session["mobile"]).get()
        for uid in user_ref:
            firebase_db.reference(f"/users/{uid}").update({"credits": session["credits"]})
            break

    return jsonify(result)

@app.route("/admin", methods=["GET"])
def admin():
    if not session.get("is_admin"):
        return "Unauthorized", 403

    users = firebase_db.reference("/users").get() or {}
    return render_template("admin.html", users=users)

@app.route("/admin/update", methods=["POST"])
def admin_update():
    if not session.get("is_admin"):
        return "Unauthorized", 403

    action = request.form["action"]
    uid = request.form["uid"]

    ref = firebase_db.reference(f"/users/{uid}")

    if action == "delete":
        ref.delete()
    elif action == "edit":
        updates = {
            "name": request.form["name"],
            "password": request.form["password"],
            "credits": int(request.form["credits"])
        }
        ref.update(updates)
    elif action == "add":
        users_ref = firebase_db.reference("/users")
        new_ref = users_ref.push()
        new_ref.set({
            "name": request.form["name"],
            "mobile": request.form["mobile"],
            "password": request.form["password"],
            "credits": int(request.form["credits"])
        })

    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
