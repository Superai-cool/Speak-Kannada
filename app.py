from flask import Flask, render_template, request, redirect, session
import firebase_admin
from firebase_admin import credentials, db
from openai_handler import generate_kannada_translation
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate(eval(os.environ.get("FIREBASE_JSON")))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]
        ref = db.reference("users").child(mobile).get()

        if ref and ref["password"] == password:
            session["mobile"] = mobile
            session["name"] = ref["name"]
            session["credits"] = ref["credit"]
            session["messages"] = []

            if mobile == "8830720742":
                return redirect("/admin")
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")
    return redirect("/")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "mobile" not in session:
        return redirect("/")

    messages = session.get("messages", [])

    if request.method == "POST":
        user_input = request.form["user_input"].strip()
        if not user_input.replace(" ", "").isascii():
            return render_template("dashboard.html", name=session["name"], credits=session["credits"], messages=messages, error="Please ask your question in English only.")

        try:
            result = generate_kannada_translation(user_input)
            # Deduct 1 credit
            mobile = session["mobile"]
            session["credits"] -= 1
            db.reference("users").child(mobile).update({"credit": session["credits"]})

            messages.append({"user": user_input, "bot": result})
            session["messages"] = messages
        except Exception as e:
            return render_template("dashboard.html", name=session["name"], credits=session["credits"], messages=messages, error="Something went wrong. Try again!")

    return render_template("dashboard.html", name=session["name"], credits=session["credits"], messages=messages)


@app.route("/admin")
def admin():
    if session.get("mobile") == "8830720742":
        all_users = db.reference("users").get()
        return render_template("admin.html", users=all_users)
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
