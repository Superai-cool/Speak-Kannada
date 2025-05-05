from flask import Flask, render_template, request, session, redirect, url_for
from firebase_config import db
from openai_handler import generate_kannada_translation
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

ADMIN_NUMBER = '8830720742'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        user_ref = db.child("users").child(mobile).get()
        if user_ref.val() and user_ref.val().get("password") == password:
            session['mobile'] = mobile
            session['name'] = user_ref.val().get("name", "User")
            session['credits'] = user_ref.val().get("credits", 0)

            if mobile == ADMIN_NUMBER:
                return redirect('/admin')

            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'mobile' not in session:
        return redirect('/login')

    return render_template('dashboard.html', name=session.get("name"), credits=session.get("credits"))

@app.route('/translate', methods=['POST'])
def translate():
    if 'mobile' not in session:
        return redirect('/login')

    user_input = request.form['user_input']

    if not user_input.strip() or not user_input.replace(' ', '').isascii():
        return {"error": "Please ask your question in English only."}

    credits = int(session.get("credits", 0))
    if credits <= 0:
        return {"error": "No credits left."}

    result = generate_kannada_translation(user_input)

    # Deduct credit
    mobile = session['mobile']
    credits -= 1
    session['credits'] = credits
    db.child("users").child(mobile).update({"credits": credits})

    return result

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'mobile' not in session or session['mobile'] != ADMIN_NUMBER:
        return redirect('/login')

    users = db.child("users").get()
    user_list = []
    if users.each():
        for user in users.each():
            user_data = user.val()
            user_list.append({
                "mobile": user.key(),
                "name": user_data.get("name", ""),
                "credits": user_data.get("credits", 0),
                "password": user_data.get("password", "")
            })

    return render_template("admin.html", users=user_list)

@app.route('/update_user', methods=['POST'])
def update_user():
    if session.get('mobile') != ADMIN_NUMBER:
        return redirect('/login')

    mobile = request.form['mobile']
    name = request.form['name']
    password = request.form['password']
    credits = request.form['credits']

    db.child("users").child(mobile).update({
        "name": name,
        "password": password,
        "credits": int(credits)
    })
    return redirect('/admin')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if session.get('mobile') != ADMIN_NUMBER:
        return redirect('/login')

    mobile = request.form['mobile']
    db.child("users").child(mobile).remove()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
