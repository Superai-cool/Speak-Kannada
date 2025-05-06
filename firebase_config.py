import json
import firebase_admin
from firebase_admin import credentials, db
import os

firebase_json = os.getenv("FIREBASE_KEY_JSON")

if not firebase_json:
    raise ValueError("FIREBASE_KEY_JSON environment variable is missing.")

firebase_dict = json.loads(firebase_json)
cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})

firebase_auth = firebase_admin.auth
firebase_db = db
