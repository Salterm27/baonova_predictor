from fastapi import FastAPI
import request
import openai
import json
import googlemaps as gmaps
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
async def get_location(latitude: float, longitude: float):
    # Geocoding an address
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))

    # Extracting address components and identifying road type
    road_type_mapping = {
        'road': 'road',
        'avenue': 'ave',
        'street': 'st',
        'boulevard': 'boulevard',
        'drive': 'dr',
        'highway': 'hwy',
        'parkway': 'pkwy',
        'court': 'ct',
        'lane': 'ln',
    }

    road_type_one_hot = {
        'road': 0,
        'ave': 0,
        'st': 0,
        'boulevard': 0,
        'dr': 0,
        'hwy': 0,
        'pkwy': 0,
        'ct': 0,
        'ln': 0,
    }

    found_road_type = False
    if reverse_geocode_result:
        for component in reverse_geocode_result[0]['address_components']:
            if 'route' in component['types']:
                long_name = component['long_name'].lower()
                for key, value in road_type_mapping.items():
                    if key in long_name:
                        road_type_one_hot[value] = 1
                        found_road_type = True
                        break
                if found_road_type:
                    break

    return road_type_one_hot


@app.get("/api/tags")
async def get_tags(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/attributes")
async def get_attributes(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/resto")
async def get_resto(name: str):
    return {"message": f"Hello {name}"}

@app.get("/api/model")
async def get_model(name: str):
    return 1;


