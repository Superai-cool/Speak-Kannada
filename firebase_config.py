import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Load JSON from environment variable
firebase_json = os.environ.get("FIREBASE_JSON")
if not firebase_json:
    raise ValueError("FIREBASE_JSON not found in environment variables")

# Parse the JSON and initialize Firebase
cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})
