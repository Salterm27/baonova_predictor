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
    model_averages = []
    all_probabilities = []

    for _ in range(5):  # Create enriched variants
        enriched_data = enrichment_pipeline(input)
        wrapped = myPredictionInput(data=enriched_data)

        probabilities = []
        for _ in range(20):
            prediction = predict(wrapped)  # {"probability": float}
            prob = prediction["probability"]
            probabilities.append(prob)
            all_probabilities.append(prob)

        model_avg = sum(probabilities) / len(probabilities)
        model_averages.append(model_avg)

    overall_average = sum(all_probabilities) / len(all_probabilities)
    return overall_average