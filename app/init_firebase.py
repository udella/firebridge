import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from app.constants import GOOGLE_APPLICATION_CREDENTIALS

cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()