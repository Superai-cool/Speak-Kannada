from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from firebase_config import firebase_auth, firebase_db
from openai_handler import generate_kannada_translation
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
ADMIN_MOBILE = "8830720742"

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        user = firebase_db.reference(f"users/{mobile}").get()

        if user and user.get("password") == password:
            session["mobile"] = mobile
            session["name"] = user["name"]
            session["credits"] = user["credits"]
            return redirect("/admin" if mobile == ADMIN_MOBILE else "/dashboard")
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "mobile" not in session:
        return redirect("/login")

    if request.method == "POST":
        question = request.form["question"].strip()
        if not question.replace(" ", "").isascii():
            return render_template("dashboard.html", name=session["name"], credits=session["credits"],
                                   conversation=[], error="Please ask in English only.")

        if session["mobile"] != ADMIN_MOBILE and session["credits"] <= 0:
            return render_template("dashboard.html", name=session["name"], credits=0,
                                   conversation=[], error="No credits left.")

        response = generate_kannada_translation(question)

        if session["mobile"] != ADMIN_MOBILE:
            session["credits"] -= 1
            firebase_db.reference(f"users/{session['mobile']}").update({"credits": session["credits"]})

        conversation = [{"question": question, "response": response}]
        return render_template("dashboard.html", name=session["name"], credits=session["credits"],
                               conversation=conversation)

    return render_template("dashboard.html", name=session["name"], credits=session["credits"], conversation=[])

@app.route("/translate", methods=["POST"])
def translate():
    if "mobile" not in session:
        return jsonify({"error": "Not logged in"}), 401

    question = request.json.get("question", "").strip()
    if not question or not question.replace(" ", "").isascii():
        return jsonify({"error": "Ask in English only"}), 400

    mobile = session["mobile"]
    credits = session["credits"]
    if mobile != ADMIN_MOBILE and credits <= 0:
        return jsonify({"error": "No credits left"}), 402

    response = generate_kannada_translation(question)

    if mobile != ADMIN_MOBILE:
        credits -= 1
        session["credits"] = credits
        firebase_db.reference(f"users/{mobile}").update({"credits": credits})

    return jsonify({"answer": response, "credits": session["credits"]})

@app.route("/admin")
def admin_panel():
    if session.get("mobile") != ADMIN_MOBILE:
        return redirect("/dashboard")

    users = firebase_db.reference("users").get() or {}
    return render_template("admin.html", users=users)

@app.route("/update_user", methods=["POST"])
def update_user():
    if session.get("mobile") != ADMIN_MOBILE:
        return "Unauthorized", 403

    form = request.form
    firebase_db.reference(f"users/{form['mobile']}").set({
        "name": form["name"],
        "password": form["password"],
        "credits": int(form["credits"])
    })
    return redirect("/admin")

@app.route("/delete_user/<mobile>")
def delete_user(mobile):
    if session.get("mobile") != ADMIN_MOBILE:
        return "Unauthorized", 403

    firebase_db.reference(f"users/{mobile}").delete()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
