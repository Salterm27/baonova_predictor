from fastapi import APIRouter
from app.models.schemas import Coordinates
from app.utils.geocode import get_location_details, encode_address_type

router = APIRouter()

@router.post("/location/")
def expand_location_endpoint(coords: Coordinates):
    city, postal_code = get_location_details(coords.latitude, coords.longitude)
    road_type_data = encode_address_type(coords.latitude, coords.longitude)
    return {
        "city": city,
        "postal_code": postal_code,
        **road_type_data
    }