from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from app.constants import GOOGLE_APPLICATION_CREDENTIALS
from app.routers import user
from app.routers import firestore

# cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
# firebase_admin.initialize_app(cred)
# db = firestore.client()

app = FastAPI()
app.include_router(user.router, prefix="/user")
app.include_router(firestore.router, prefix="/firestore")

@app.get("/")
async def root():
    return {"message": "Hello, Firebridge!"}




