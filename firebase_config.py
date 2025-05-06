import os
import json
import firebase_admin
from firebase_admin import credentials, db, auth

# Get the stringified JSON from the FIREBASE_KEY_JSON env variable
firebase_json = os.environ.get("FIREBASE_KEY_JSON")

if not firebase_json:
    raise ValueError("❌ FIREBASE_KEY_JSON is missing in environment variables.")

try:
    cred_dict = json.loads(firebase_json)
except json.JSONDecodeError as e:
    raise ValueError("❌ FIREBASE_KEY_JSON is not valid JSON: " + str(e))

cred = credentials.Certificate(cred_dict)

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

# Export objects for use
firebase_auth = auth
firebase_db = db
