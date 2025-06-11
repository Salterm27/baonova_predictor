from fastapi import APIRouter
from app.models.schemas import Prediction_Input, myPredictionInput
from app.utils.geocode import get_location_details, encode_address_type
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrich_dining_beverage_tags, unified_enrichment
from app.utils.predictor_model import predict


router = APIRouter()

@router.post("/predict/")
def prediction_pipeline(input: Prediction_Input):
    merged_data=get_location_details(input.latitude, input.longitude)
    merged_data.update(encode_address_type(input.latitude, input.longitude))
    merged_data.update(enrich_business_tags(merged_data["city"], input.category))
    merged_data.update(enrich_attributes_vector(merged_data))
    merged_data.update(enrich_dining_beverage_tags(merged_data))
    merged_data.update({"n_competitors_1km": input.n_competitors_1km})
    return merged_data

@router.post("/cheap_predict/")
def prediction_pipeline(input: Prediction_Input):
    merged_data=get_location_details(input.latitude, input.longitude)
    merged_data.update(encode_address_type(input.latitude, input.longitude))
    merged_data.update({"n_competitors_1km":input.n_competitors_1km})
    merged_data.update(unified_enrichment(merged_data))
    return merged_data

@router.post("/predict_only/")
def simple_prediction(input: myPredictionInput):
    return predict(input)