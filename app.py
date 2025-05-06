from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from firebase_config import firebase_auth, firebase_db
from openai_handler import generate_kannada_translation

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Admin mobile number (your number)
ADMIN_MOBILE = "8830720742"

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        user_ref = firebase_db.reference(f"users/{mobile}")
        user = user_ref.get()

        if user and user.get("password") == password:
            session["mobile"] = mobile
            session["name"] = user.get("name", "User")
            session["credits"] = user.get("credits", 0)
            if mobile == ADMIN_MOBILE:
                return redirect(url_for("admin_panel"))
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "mobile" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("name"), credits=session.get("credits"))

@app.route("/translate", methods=["POST"])
def translate():
    if "mobile" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question or not question[0].isalpha():
        return jsonify({"error": "Please enter a valid English question."})

    # Check if user is admin (skip credit deduction)
    if session["mobile"] != ADMIN_MOBILE:
        if session["credits"] <= 0:
            return jsonify({"error": "You have no credits left."})
        # Deduct credit
        session["credits"] -= 1
        firebase_db.reference(f"users/{session['mobile']}/credits").set(session["credits"])

    # Call OpenAI
    answer = generate_kannada_translation(question)
    return jsonify({"answer": answer, "credits": session.get("credits", 0)})

@app.route("/admin")
def admin_panel():
    if session.get("mobile") != ADMIN_MOBILE:
        return redirect(url_for("dashboard"))

    users_ref = firebase_db.reference("users")
    users = users_ref.get() or {}
    return render_template("admin.html", users=users)

@app.route("/update_user", methods=["POST"])
def update_user():
    if session.get("mobile") != ADMIN_MOBILE:
        return "Unauthorized", 403

    mobile = request.form.get("mobile")
    name = request.form.get("name")
    password = request.form.get("password")
    credits = int(request.form.get("credits", 0))

    user_ref = firebase_db.reference(f"users/{mobile}")
    user_ref.set({
        "name": name,
        "password": password,
        "credits": credits
    })
    return redirect(url_for("admin_panel"))

@app.route("/delete_user/<mobile>")
def delete_user(mobile):
    if session.get("mobile") != ADMIN_MOBILE:
        return "Unauthorized", 403

    firebase_db.reference(f"users/{mobile}").delete()
    return redirect(url_for("admin_panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
