from fastapi import FastAPI
import request
import openai
import json
import googlemaps
from dotenv import load_dotenv
import os

load_dotenv()  # this loads variables from .env
openai.api_key = os.getenv("openai_key")
googlemaps.api_key = os.getenv("gmaps_key")
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/location")
async def get_tags(name: str):
    return {"message": f"Hello {name}"}


@app.get("/api/tags")
async def get_tags(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/attributes")
async def get_tags(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/resto")
async def get_tags(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/model")


