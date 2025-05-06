import os
import json
import firebase_admin
from firebase_admin import credentials, auth, db

firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if firebase_key_json and firebase_key_json.startswith('{'):
    firebase_key_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(firebase_key_dict)
else:
    cred = credentials.Certificate("firebase-key.json")  # fallback for local dev

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DB_URL")
    })

firebase_auth = auth
firebase_db = db
