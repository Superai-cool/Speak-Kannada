import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Get the JSON string from Railway variable
firebase_json = os.environ.get("FIREBASE_JSON")

if not firebase_json:
    raise ValueError("FIREBASE_JSON environment variable not set")

# Parse JSON string to dictionary
cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})
