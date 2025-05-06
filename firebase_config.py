import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase credentials from environment variable
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if not firebase_key_json:
    raise ValueError("FIREBASE_KEY_JSON env variable is missing.")

# Convert stringified JSON into a dictionary
firebase_creds_dict = json.loads(firebase_key_json)
cred = credentials.Certificate(firebase_creds_dict)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})

# Export the DB reference
firebase_db = db.reference()
