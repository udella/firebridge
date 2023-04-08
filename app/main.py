from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from app.constants import GOOGLE_APPLICATION_CREDENTIALS
from app.routers import users

cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)

app = FastAPI()
app.include_router(users.router, prefix="/users")

@app.get("/")
async def root():
    return {"message": "Hello, Firebridge!"}




