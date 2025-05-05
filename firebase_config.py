import firebase_admin
from firebase_admin import credentials, db
import json
import os

# Load Firebase Admin credentials from environment variable (JSON string)
firebase_json = os.getenv("FIREBASE_JSON")
firebase_db_url = os.getenv("FIREBASE_DB_URL")

# Parse JSON and initialize app
cred = credentials.Certificate(json.loads(firebase_json))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
    })
