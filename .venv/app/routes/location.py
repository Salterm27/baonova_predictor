from fastapi import APIRouter, HTTPException
from app.models.schemas import Coordinates
from app.utils.geocode import get_location_details, encode_address_type, GeocodingError, APIGeocodingError, LocationNotFoundError

router = APIRouter()

@router.post("/location/")
def expand_location_endpoint(coords: Coordinates):
    try:
        location_details = get_location_details(coords.latitude, coords.longitude)
        if not location_details.get("city") and not location_details.get("postal_code"):
            raise HTTPException(status_code=404, detail="Location details not found")

        road_type_data = encode_address_type(coords.latitude, coords.longitude)
        return {
            **location_details,
            **road_type_data
        }
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except APIGeocodingError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway for API errors
    except GeocodingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location expansion failed: {str(e)}")
