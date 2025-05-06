import os
import json
import firebase_admin
from firebase_admin import credentials, db, auth

firebase_json = os.getenv("FIREBASE_KEY_JSON")
firebase_db_url = os.getenv("FIREBASE_DB_URL")

if not firebase_json:
    raise Exception("FIREBASE_KEY_JSON is not set or empty.")

cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_db_url
})

firebase_auth = auth
firebase_db = db
