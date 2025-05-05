import os
import firebase_admin
from firebase_admin import credentials, db
import json

firebase_json = json.loads(os.environ.get("FIREBASE_JSON"))
cred = credentials.Certificate(firebase_json)

firebase_admin.initialize_app(cred, {
    "databaseURL": os.environ.get("FIREBASE_DB_URL")
})
