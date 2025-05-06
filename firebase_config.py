import os
import json
import firebase_admin
from firebase_admin import credentials, auth, db

# Load Firebase credentials from environment variable
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if firebase_key_json and firebase_key_json.startswith('{'):
    firebase_key_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(firebase_key_dict)
else:
    # Fallback for local development
    cred = credentials.Certificate("firebase-key.json")

# Initialize Firebase app
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")  # also set this in Railway
    })

firebase_auth = auth
firebase_db = db
