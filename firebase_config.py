import os
import json
import firebase_admin
from firebase_admin import credentials, auth, db

# Load Firebase credentials
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if firebase_key_json and firebase_key_json.startswith('{'):
    # Railway environment: use JSON string from environment variable
    firebase_key_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(firebase_key_dict)
else:
    # Local environment fallback
    cred = credentials.Certificate("firebase-key.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DB_URL")
    })

# Export auth and db for use elsewhere
firebase_auth = auth
firebase_db = db
