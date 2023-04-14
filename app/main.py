from fastapi import FastAPI
from app.routers import user
from app.routers import firestore

app = FastAPI()
app.include_router(user.router, prefix="/user")
app.include_router(firestore.router, prefix="/firestore")

@app.get("/")
async def root():
    return {"message": "Hello, Firebridge!"}




