import firebase_admin
from firebase_admin import credentials, auth, db
import os

# Make sure the path is either hardcoded correctly or fetched from environment
FIREBASE_KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", "firebase-key.json")

cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://speak-kannada-4cd25-default-rtdb.asia-southeast1.firebasedatabase.app/users'  # ✅ update this with your actual Firebase DB URL
})

firebase_auth = auth
firebase_db = db
