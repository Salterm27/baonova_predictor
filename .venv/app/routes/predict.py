from fastapi import APIRouter
from app.models.schemas import Prediction_Input, myPredictionInput
from app.utils.geocode import get_location_details, encode_address_type
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrich_dining_beverage_tags, unified_enrichment
from app.utils.predictor_model import predict


router = APIRouter()


@router.post("/predict_only/")
def simple_prediction(input: myPredictionInput):
    return predict(input)