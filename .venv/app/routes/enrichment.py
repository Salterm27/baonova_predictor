from fastapi import APIRouter
from app.models.schemas import TagRequest
from app.models.schemas import AttributeRequest

from app.utils.ai_enrichment import enrich_business_tags, enrich_attributes_vector

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