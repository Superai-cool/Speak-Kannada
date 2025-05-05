from flask import Flask, render_template, request, redirect, session, url_for
from openai_handler import get_kannada_response
from firebase_config import db
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        user_data = db.reference(f"users/{mobile}").get()
        if user_data and user_data.get("password") == password:
            session["user"] = user_data["name"]
            session["mobile"] = mobile
            return redirect(url_for("dashboard"))
        else:
            return "Invalid mobile number or password"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["user"])

@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return redirect(url_for("login"))
    user_input = request.form["message"]
    response = get_kannada_response(user_input)
    return response

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
def admin_panel():
    users = db.reference("users").get() or {}
    return render_template("admin.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.form
    db.reference(f"users/{data['mobile']}").set({
        "name": data["name"],
        "password": data["password"],
        "credit": int(data["credit"])
    })
    return redirect("/admin")

@app.route("/update_user/<mobile>", methods=["POST"])
def update_user(mobile):
    data = request.form
    db.reference(f"users/{mobile}").update({
        "name": data["name"],
        "password": data["password"],
        "credit": int(data["credit"])
    })
    return redirect("/admin")

@app.route("/delete_user/<mobile>", methods=["POST"])
def delete_user(mobile):
    db.reference(f"users/{mobile}").delete()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
