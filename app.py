from flask import Flask, render_template, request, redirect, url_for, session
from firebase_config import firebase_auth, firebase_db
from openai_handler import generate_kannada_translation
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

admin_number = "8830720742"

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]
        users = firebase_db.child("users").get().val()
        if users and mobile in users and users[mobile]["password"] == password:
            session["mobile"] = mobile
            session["name"] = users[mobile]["name"]
            session["credits"] = users[mobile]["credits"]
            if mobile == admin_number:
                return redirect("/admin")
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid mobile or password")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "mobile" not in session:
        return redirect("/login")

    if request.method == "POST":
        question = request.form["question"]
        if not question.replace(" ", "").isalpha():
            return render_template("dashboard.html", name=session["name"], credits=session["credits"],
                                   error="Please ask your question in English only.")

        if session["credits"] <= 0:
            return render_template("dashboard.html", name=session["name"], credits=session["credits"],
                                   error="No credits left.")

        response = generate_kannada_translation(question)
        session["credits"] -= 1
        firebase_db.child("users").child(session["mobile"]).update({"credits": session["credits"]})
        return render_template("dashboard.html", name=session["name"], credits=session["credits"],
                               question=question, response=response)

    return render_template("dashboard.html", name=session["name"], credits=session["credits"])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "mobile" not in session or session["mobile"] != admin_number:
        return redirect("/login")

    users = firebase_db.child("users").get().val()
    return render_template("admin.html", users=users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
