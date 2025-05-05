import firebase_admin
from firebase_admin import credentials, db
import os

# Get the path to the uploaded JSON file in Railway
firebase_key_path = os.getenv("FIREBASE_KEY_PATH", "firebase-adminsdk.json")

# Get the Firebase Realtime Database URL from Railway environment variables
firebase_db_url = os.getenv("FIREBASE_DB_URL")

# Only initialize once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
    })
