import json
import os
import firebase_admin
from firebase_admin import credentials, db

# Get the stringified JSON from the Railway env variable
firebase_json = os.environ.get("FIREBASE_KEY_JSON")

# Load the JSON credentials
cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)

# Initialize the Firebase app
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})

firebase_auth = firebase_admin.auth
firebase_db = db
