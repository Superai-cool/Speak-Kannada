from flask import Flask, render_template, request, redirect, session, jsonify
import os
import firebase_admin
from firebase_admin import credentials, db
from openai_handler import generate_kannada_translation
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Firebase Init
firebase_json = os.environ.get("FIREBASE_JSON")
cred = credentials.Certificate(eval(firebase_json))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

users_ref = db.reference('users')

# Admin mobile number
ADMIN_MOBILE = '8830720742'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        user = users_ref.child(mobile).get()
        if user and user.get('password') == password:
            session['user'] = {
                'mobile': mobile,
                'name': user.get('name'),
                'credit': int(user.get('credit'))
            }
            if mobile == ADMIN_MOBILE:
                return redirect('/admin')
            return redirect('/dashboard')
        return render_template('login.html', error='Invalid mobile or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', name=session['user']['name'], credit=session['user']['credit'])

@app.route('/ask', methods=['POST'])
def ask():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_input = data.get('user_input', '')

    # Validate: must be in English (basic A-Z check)
    if not user_input or not user_input.replace(" ", "").isascii():
        return jsonify({'error': 'Please ask your question in English only.'}), 400

    user_mobile = session['user']['mobile']
    user_credit = session['user']['credit']

    if user_credit <= 0:
        return jsonify({'error': 'No credits remaining'}), 403

    try:
        output = generate_kannada_translation(user_input)

        # Deduct 1 credit
        new_credit = user_credit - 1
        users_ref.child(user_mobile).update({'credit': new_credit})
        session['user']['credit'] = new_credit

        return jsonify({'response': output})
    except Exception as e:
        return jsonify({'error': f'Failed to get response: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['mobile'] != ADMIN_MOBILE:
        return redirect('/')
    all_users = users_ref.get()
    return render_template('admin.html', users=all_users)

@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.form
    mobile = data['mobile']
    updated_data = {
        'name': data['name'],
        'password': data['password'],
        'credit': int(data['credit'])
    }
    users_ref.child(mobile).update(updated_data)
    return redirect('/admin')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    mobile = request.form['mobile']
    users_ref.child(mobile).delete()
    return redirect('/admin')

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form
    mobile = data['mobile']
    if users_ref.child(mobile).get():
        return 'User already exists'
    users_ref.child(mobile).set({
        'name': data['name'],
        'password': data['password'],
        'credit': int(data['credit'])
    })
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
