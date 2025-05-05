import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Read JSON from environment variable
firebase_json = os.environ.get("FIREBASE_JSON")
if not firebase_json:
    raise ValueError("Missing FIREBASE_JSON variable")

cred = credentials.Certificate(json.loads(firebase_json))

firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})
