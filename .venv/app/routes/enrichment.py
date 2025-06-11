from fastapi import APIRouter, HTTPException
from app.models.schemas import TagRequest, AttributeRequest, Enriched_Business, Prediction_Input
from app.utils.ai_enrichment import (
    enrich_business_tags, enrich_attributes_vector, enrichment_pipeline, conditionally_get_dining_tags,
    EnrichmentError, JSONDecodeEnrichmentError, APIEnrichmentError
)
from app.utils.geocode import GeocodingError, APIGeocodingError, LocationNotFoundError

router = APIRouter()

@router.post("/tags/")
def enrich_tags_endpoint(request: TagRequest):
    try:
        tags = enrich_business_tags(request.city, request.category)
        return tags
    except JSONDecodeEnrichmentError as e:
        raise HTTPException(status_code=422, detail=str(e))  # Unprocessable Entity
    except APIEnrichmentError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway
    except EnrichmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tag enrichment failed: {str(e)}")

@router.post("/attributes/")
async def enrich_attributes_endpoint(business_data: AttributeRequest):
    try:
        # Convert Pydantic model to plain dict
        input_dict = business_data.dict()
        result = enrich_attributes_vector(input_dict)
        return result
    except JSONDecodeEnrichmentError as e:
        raise HTTPException(status_code=422, detail=str(e))  # Unprocessable Entity
    except APIEnrichmentError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway
    except EnrichmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attribute enrichment failed: {str(e)}")

@router.post("/dining-tags/")
def get_dining_tags_endpoint(input: Enriched_Business):
    try:
        result = conditionally_get_dining_tags(input.data)
        return result
    except JSONDecodeEnrichmentError as e:
        raise HTTPException(status_code=422, detail=str(e))  # Unprocessable Entity
    except APIEnrichmentError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway
    except EnrichmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dining tags enrichment failed: {str(e)}")

@router.post("/enrich/")
def enrich_only(input: Prediction_Input):
    try:
        result = enrichment_pipeline(input)
        return result
    except JSONDecodeEnrichmentError as e:
        raise HTTPException(status_code=422, detail=str(e))  # Unprocessable Entity
    except APIEnrichmentError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway
    except EnrichmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except LocationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except APIGeocodingError as e:
        raise HTTPException(status_code=502, detail=str(e))  # Bad Gateway
    except GeocodingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment pipeline failed: {str(e)}")
