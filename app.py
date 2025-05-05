from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db
import os
from openai_handler import generate_kannada_translation

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Firebase initialization
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
        users_ref = db.reference("users")
        user = users_ref.child(mobile).get()
        if user and user.get("password") == password:
            session["user"] = user["name"]
            session["mobile"] = mobile
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

@app.route("/get_response", methods=["POST"])
def get_response():
    if "user" not in session:
        return redirect(url_for("login"))

    message = request.json.get("message", "")
    mobile = session.get("mobile")
    user_ref = db.reference(f"users/{mobile}")
    user_data = user_ref.get()
    credit = user_data.get("credit", 0)

    if credit <= 0:
        return {"error": "Insufficient credit. Please contact support."}

    # Call OpenAI function
    try:
        response = generate_kannada_translation(message)
    except Exception as e:
        return {"error": str(e)}

    # Deduct credit
    user_ref.update({"credit": credit - 1})
    return {"response": response, "remaining_credit": credit - 1}

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
