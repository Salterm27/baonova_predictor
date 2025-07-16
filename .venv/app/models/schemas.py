from pydantic import BaseModel
from typing import Dict, Any

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class TagRequest(BaseModel):
    city: str
    category: str
    description: str

class AttributeRequest(BaseModel):
    city: str
    postal_code: str
    num_competitors: int
    street_type: Dict[str, int]
    tags: Dict[str, int]
    description: str

class Enriched_Business(BaseModel):
    data: Dict[str, Any]

class Prediction_Input(BaseModel):
    latitude: float
    longitude: float
    category: str
    n_competitors_1km: int
    description: str

class myPredictionInput(BaseModel):
    data: Dict[str, Any]