from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import googlemaps
import requests

load_dotenv()  # loads variables from .env into environment
GOOGLE_MAPS_API_KEY = os.getenv("gmaps_key")
OPENAI_API_KEY = os.getenv("openai_key")

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
OpenAI_key = os.getenv(key=OPENAI_API_KEY)
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}



class Coordinates(BaseModel):
    latitude: float
    longitude: float
class Competitors (BaseModel):
    n_competitors_1km: int
class Category(BaseModel):
    category: str
def encode_address_type(latitude: float, longitude: float) -> dict:
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))

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

def get_location_details(lat: float, lon: float):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lon}",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    city = None
    postal_code = None

    if data and data['results']:
        for component in data['results'][0]['address_components']:
            if 'locality' in component['types']:
                city = component['long_name']
            if 'postal_code' in component['types']:
                postal_code = component['long_name']
    return city, postal_code


@app.post("/location/")
def expand_location(coords: Coordinates):
    city, postal_code = get_location_details(coords.latitude, coords.longitude)
    road_type_data = encode_address_type(coords.latitude, coords.longitude)

    return {
        "city": city,
        "postal_code": postal_code,
        **road_type_data  # merge into the top-level response
    }

