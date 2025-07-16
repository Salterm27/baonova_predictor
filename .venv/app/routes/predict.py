from fastapi import APIRouter
from app.models.schemas import Prediction_Input, myPredictionInput
from app.utils.geocode import get_location_details, encode_address_type
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrich_dining_beverage_tags, unified_enrichment, enrichment_pipeline
from app.utils.predictor_model import predict


router = APIRouter()


@router.post("/predict/light")
def simple_prediction(input: myPredictionInput):
    return predict(input)

@router.post("/predict/")
def prediction(input: Prediction_Input):
    probabilities = []
    all_predictions = []

    for _ in range(5):
        enriched_data = enrichment_pipeline(input)
        wrapped = myPredictionInput(data=enriched_data)
        prediction = predict(wrapped)
        all_predictions.append(prediction)
        probabilities.append(prediction["probability"])

    average_probability = sum(probabilities) / len(probabilities)

    return  average_probability