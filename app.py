from flask import Flask, render_template, request, redirect, url_for, session
from firebase_config import db
from openai_handler import get_kannada_response
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
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid mobile number or password.")
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
        return "Session expired. Please log in again."

    message = request.form["message"]
    mobile = session.get("mobile")
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    if credit <= 0:
        return "<strong>Insufficient credits.</strong> Please contact admin."

    # Get AI response
    response = get_kannada_response(message)

    # Deduct credit only if OpenAI response succeeded
    if not response.startswith("<strong>Error"):
        user_ref.update({"credit": credit - 1})

    return response

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
