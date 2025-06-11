from fastapi import FastAPI
from app.routes import location, enrichment, predict

from dotenv import load_dotenv
import os

load_dotenv()  # 👈 loads from .env

GOOGLE_MAPS_API_KEY = os.getenv("gmaps_key")
OPENAI_API_KEY = os.getenv("openai_key")

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

app.include_router(predict.router)
app.include_router(location.router)
app.include_router(enrichment.router)