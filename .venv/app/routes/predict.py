from fastapi import APIRouter
from app.models.schemas import Prediction_Input, myPredictionInput
from app.utils.geocode import get_location_details, encode_address_type
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrich_dining_beverage_tags, unified_enrichment, enrichment_pipeline
from app.utils.predictor_model import predict
import random
from math import cos, radians


router = APIRouter()


@router.post("/predict/light")
def simple_prediction(input: myPredictionInput):
    return predict(input)

@router.post("/predict/")
def prediction(input: Prediction_Input):
    model_averages = []
    all_probabilities = []

    for _ in range(10):  # Create enriched variants with jittered coordinates
        jittered_lat, jittered_lon = jitter_coordinates(input.latitude, input.longitude)

        # Create a modified input with jittered coordinates
        jittered_input = Prediction_Input(
            latitude=jittered_lat,
            longitude=jittered_lon,
            category=input.category,
            n_competitors_1km=input.n_competitors_1km,
            description=input.description
        )

        enriched_data = enrichment_pipeline(jittered_input)
        wrapped = myPredictionInput(data=enriched_data)

        probabilities = []
        for _ in range(10):
            prediction = predict(wrapped)  # {"probability": float}
            prob = prediction["probability"]
            probabilities.append(prob)
            all_probabilities.append(prob)

        model_avg = sum(probabilities) / len(probabilities)
        model_averages.append(model_avg)

    overall_average = sum(all_probabilities) / len(all_probabilities)
    return  overall_average




def jitter_coordinates(lat: float, lon: float, max_distance_km: float = 1.0):
    """
    Jitter latitude and longitude randomly within a given radius (in km).
    Assumes Earth's radius ≈ 6371 km.
    """
    # ~1 km in degrees
    delta_lat = max_distance_km / 110.574  # ~111 km per degree latitude
    delta_lon = max_distance_km / (111.320 * cos(radians(lat)))  # varies with latitude

    new_lat = lat + random.uniform(-delta_lat, delta_lat)
    new_lon = lon + random.uniform(-delta_lon, delta_lon)

    return new_lat, new_lon