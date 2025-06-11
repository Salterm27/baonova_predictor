from fastapi import APIRouter
from app.models.schemas import Prediction_Input
from app.utils.geocode import get_location_details, encode_address_type
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrich_dining_beverage_tags


router = APIRouter()

@router.post("/predict/")
def prediction_pipeline(input: Prediction_Input):
    merged_data=get_location_details(input.latitude, input.longitude)
    merged_data.update(encode_address_type(input.latitude, input.longitude))
    merged_data.update(enrich_business_tags(merged_data["city"], input.category))
    merged_data.update(enrich_attributes_vector(merged_data))
    merged_data.update(enrich_dining_beverage_tags(merged_data))
    return merged_data
