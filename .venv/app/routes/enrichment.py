from fastapi import APIRouter
from app.models.schemas import TagRequest, AttributeRequest, Enriched_Business, Prediction_Input
from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector, enrichment_pipeline

router = APIRouter()

@router.post("/tags/")
def enrich_tags_endpoint(request: TagRequest):
    tags = enrich_business_tags(request.city, request.category)
    if tags is None:
        return {"error": "Tag enrichment failed"}
    return tags

@router.post("/attributes/")
async def enrich_attributes_endpoint(business_data: AttributeRequest):
    try:
        # Convert Pydantic model to plain dict
        input_dict = business_data.dict()
        result = enrich_attributes_vector(input_dict)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to enrich attributes.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dining-tags/")
def get_dining_tags_endpoint(input: Enriched_Business):
    try:
        result = conditionally_get_dining_tags(input.data)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to enrich dining tags.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrich/")
def enrich_only(input: Prediction_Input):
    return enrichment_pipeline(input)