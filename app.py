from flask import Flask, render_template, request, redirect, session, jsonify
from firebase_config import firebase_auth, firebase_db
from openai_handler import generate_kannada_translation
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = "secret-key"
app.permanent_session_lifetime = timedelta(days=1)

ADMIN_NUMBERS = ["9876543210", "8830720742"]

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        user_ref = firebase_db.reference(f'users/{mobile}')
        user = user_ref.get()

        if user and user['password'] == password:
            session['mobile'] = mobile
            session['name'] = user['name']
            session['credits'] = user['credit']
            return redirect('/dashboard')
        else:
            return "Invalid credentials", 401

    return render_template("login.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'mobile' not in session:
        return redirect('/login')

    name = session.get('name')
    credits = session.get('credits')
    intro_message = "👋 Welcome to Speak Kannada – Your personal AI assistant to learn Kannada with proper pronunciation and examples. Ask how to say anything in Kannada!"

    return render_template("dashboard.html", name=name, credits=credits, intro_message=intro_message)

@app.route('/translate', methods=['POST'])
def translate():
    if 'mobile' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_input = request.json.get('message', '')

    if not user_input.strip():
        return jsonify({'error': 'Empty message'}), 400

    # English-only check
    if not all(ord(c) < 128 for c in user_input):
        return jsonify({'error': 'Please ask your question in English only.'}), 400

    mobile = session['mobile']
    user_ref = firebase_db.reference(f'users/{mobile}')
    user_data = user_ref.get()

    credits = int(user_data.get('credit', 0))
    if credits <= 0:
        return jsonify({'error': 'You are out of credits. Please contact admin.'}), 402

    # Generate response
    response = generate_kannada_translation(user_input)

    # Deduct credit
    new_credits = credits - 1
    user_ref.update({'credit': new_credits})
    session['credits'] = new_credits

    return jsonify({
        'response': response,
        'remaining_credits': new_credits
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin', methods=['GET'])
def admin_panel():
    if 'mobile' not in session or session['mobile'] not in ADMIN_NUMBERS:
        return "Unauthorized", 403

    users_ref = firebase_db.reference('users')
    users = users_ref.get() or {}

    return render_template("admin.html", users=users)

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'mobile' not in session or session['mobile'] not in ADMIN_NUMBERS:
        return "Unauthorized", 403

    data = request.form
    mobile = data['mobile']

    user_ref = firebase_db.reference(f'users/{mobile}')
    user_ref.update({
        'name': data.get('name'),
        'password': data.get('password'),
        'credit': int(data.get('credit', 0))
    })

    return redirect('/admin')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'mobile' not in session or session['mobile'] not in ADMIN_NUMBERS:
        return "Unauthorized", 403

    mobile = request.form['mobile']
    firebase_db.reference(f'users/{mobile}').delete()
    return redirect('/admin')

if __name__ == "__main__":
    app.run(debug=True)
