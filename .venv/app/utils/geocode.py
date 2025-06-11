import googlemaps
import requests

from dotenv import load_dotenv
import os

class GeocodingError(Exception):
    """Base exception for geocoding errors"""
    pass

class APIGeocodingError(GeocodingError):
    """Exception raised when API calls fail during geocoding"""
    pass

class LocationNotFoundError(GeocodingError):
    """Exception raised when location cannot be found"""
    pass

load_dotenv()  # 👈 loads from .env
gmaps = googlemaps.Client(key=os.getenv("gmaps_key"))
GOOGLE_MAPS_API_KEY = os.getenv("gmaps_key")


def encode_address_type(latitude: float, longitude: float) -> dict:
    try:
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

        if not reverse_geocode_result:
            raise LocationNotFoundError(f"No geocoding results found for coordinates: {latitude}, {longitude}")

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
    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API error: {e}")
        raise APIGeocodingError(f"Google Maps API error: {str(e)}")
    except Exception as e:
        print(f"Error during address type encoding: {e}")
        raise GeocodingError(f"Address type encoding failed: {str(e)}")

def get_location_details(lat: float, lon: float):
    try:
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lon}",
            "key": GOOGLE_MAPS_API_KEY
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        if data.get('status') != 'OK':
            raise APIGeocodingError(f"Google Maps API returned status: {data.get('status')}")

        city = None
        postal_code = None

        if not data.get('results'):
            raise LocationNotFoundError(f"No geocoding results found for coordinates: {lat}, {lon}")

        for component in data['results'][0]['address_components']:
            if 'locality' in component['types']:
                city = component['long_name']
            if 'postal_code' in component['types']:
                postal_code = component['long_name']

        return {
            "city": city,
            "postal_code": postal_code
        }
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise APIGeocodingError(f"Error making request to Google Maps API: {str(e)}")
    except Exception as e:
        print(f"Error getting location details: {e}")
        raise GeocodingError(f"Location details retrieval failed: {str(e)}")
