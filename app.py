from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import openai
import os
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Firebase setup
cred = credentials.Certificate(os.environ.get("FIREBASE_KEY_PATH"))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

# OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]
        ref = db.reference(f"users/{mobile}")
        user = ref.get()
        if user and user["password"] == password:
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


@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return redirect(url_for("login"))
    
    mobile = session.get("mobile")
    ref = db.reference(f"users/{mobile}")
    user_data = ref.get()
    credit = user_data.get("credit", 0)

    if credit <= 0:
        return jsonify({"reply": "❌ You have no remaining credits."})

    message = request.form["message"]

    # Custom GPT prompt
    prompt = f"""
You are "Speak Kannada" – a custom GPT designed to help users learn and speak local, conversational Kannada in a clear, friendly, and structured way.

Respond in this consistent four-part format:

👉 **Kannada Translation** – (modern Kannada only)
🧾 **Transliteration** – (Kannada sentence in English letters)
💬 **Meaning / Context** – (Explain the meaning)
✍️ **Example Sentence** – (Realistic Kannada sentence + transliteration + meaning)

If unrelated to Kannada learning, gently say:
“This app is only for learning Kannada. Please ask something Kannada-related.”

User Input: {message}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["choices"][0]["message"]["content"]

        # Deduct credit
        new_credit = max(0, credit - 1)
        ref.update({"credit": new_credit})

        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
