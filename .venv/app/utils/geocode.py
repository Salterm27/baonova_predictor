import googlemaps
import requests

from dotenv import load_dotenv
import os

load_dotenv()  # 👈 loads from .env
gmaps = googlemaps.Client(key=os.getenv("gmaps_key"))
GOOGLE_MAPS_API_KEY = os.getenv("gmaps_key")


def encode_address_type(latitude: float, longitude: float) -> dict:
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude), language="en")

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

    if reverse_geocode_result:
        for component in reverse_geocode_result[0]['address_components']:
            if 'route' in component['types']:
                long_name = component['long_name'].lower()
                for key, value in road_type_mapping.items():
                    if key in long_name:
                        road_type_one_hot[value] = 1
                        break
                break  # Only check the first 'route' component

    # Fallback if no type matched
    if not any(road_type_one_hot.values()):
        road_type_one_hot['road'] = 1
        road_type_one_hot['st'] = 1

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
    return {
        "city": city,
        "postal_code": postal_code
    }