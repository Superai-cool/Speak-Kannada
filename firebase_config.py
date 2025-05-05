import firebase_admin
from firebase_admin import credentials, db
import json
import os

# Get full JSON string from Railway environment variable
firebase_json_string = os.getenv("FIREBASE_JSON")
firebase_db_url = os.getenv("FIREBASE_DB_URL")

# Load the JSON string into a Python dict
firebase_credential_dict = json.loads(firebase_json_string)

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credential_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
    })
