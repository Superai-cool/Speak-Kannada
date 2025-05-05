from flask import Flask, render_template, request, session, redirect, url_for
import os
from firebase_admin import credentials, db, initialize_app
from openai_handler import generate_kannada_translation
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Firebase setup
cred = credentials.Certificate(eval(os.getenv("FIREBASE_JSON")))
initialize_app(cred, {"databaseURL": os.getenv("FIREBASE_DB_URL")})
ref = db.reference("/users")

# Admin mobile number
ADMIN_MOBILE = "8830720742"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    mobile = request.form.get("mobile")
    password = request.form.get("password")

    user_data = ref.child(mobile).get()
    if user_data and user_data.get("password") == password:
        session["mobile"] = mobile
        session["name"] = user_data.get("name")
        session["credits"] = user_data.get("credits", 0)
        if mobile == ADMIN_MOBILE:
            return redirect("/admin")
        return redirect("/dashboard")
    return "Invalid login", 403

@app.route("/dashboard")
def dashboard():
    if "mobile" not in session:
        return redirect("/")
    return render_template("dashboard.html", name=session["name"], credits=session["credits"])

@app.route("/get_kannada", methods=["POST"])
def get_kannada():
    if "mobile" not in session:
        return "Session expired. Please login again.", 401

    query = request.json.get("query")
    mobile = session["mobile"]

    if mobile != ADMIN_MOBILE:
        if not query.strip().replace(" ", "").isascii():
            return {"error": "Please ask your question in English only."}

        current_credits = session.get("credits", 0)
        if current_credits <= 0:
            return {"error": "No credits left. Please contact support."}

    result = generate_kannada_translation(query)

    if "error" not in result and mobile != ADMIN_MOBILE:
        new_credits = session["credits"] - 1
        ref.child(mobile).update({"credits": new_credits})
        session["credits"] = new_credits

    return result

@app.route("/admin")
def admin():
    if session.get("mobile") != ADMIN_MOBILE:
        return redirect("/")
    users = ref.get() or {}
    return render_template("admin.html", users=users)

@app.route("/update_user", methods=["POST"])
def update_user():
    if session.get("mobile") != ADMIN_MOBILE:
        return redirect("/")
    mobile = request.form.get("mobile")
    field = request.form.get("field")
    value = request.form.get("value")
    ref.child(mobile).update({field: value})
    return redirect("/admin")

@app.route("/delete_user", methods=["POST"])
def delete_user():
    if session.get("mobile") != ADMIN_MOBILE:
        return redirect("/")
    mobile = request.form.get("mobile")
    ref.child(mobile).delete()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
