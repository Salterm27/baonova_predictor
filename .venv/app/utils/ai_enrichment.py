import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.models.schemas import Prediction_Input

# Load environment variables
load_dotenv()
api_key = os.getenv("openai_key")

client = OpenAI(api_key=api_key)

TAGS = [
    "active_life", "arts", "auto_repair", "automotive", "bakeries", "bars", "beauty", "food", "cafes",
    "frozen_yogurt", "coffee", "contractors", "convenience_stores", "delis", "dentists", "desserts", "doctors",
    "entertainment", "event_planning", "event_spaces", "fashion", "fitness", "grocery", "hair_removal",
    "hair_salons", "health", "home", "home_services", "hotels", "ice_cream", "instruction", "local_services",
    "medical", "nail_salons", "nightlife", "pet_services", "pets", "professional_services", "real_estate",
    "restaurants", "services", "shopping", "skin_care", "spas", "specialty_food", "tea", "travel", "venues", "waxing"
]
def enrich_business_tags(city: str, category: str) -> dict:
    prompt = f"""
You are a classification system that enriches business data. Given a city and a business category, return a JSON object where each tag from the following list is labeled as 1 (relevant) or 0 (not relevant) to the business context:

{json.dumps(TAGS, indent=2)}

### Input
City: {city}
Business Category: {category}

### Output
Return only a JSON object with the corresponding tags set to 1 or 0 based on the relevance of the business type and city.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You classify business categories into relevant tags."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Handle triple-backtick code blocks
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(line for line in lines if not line.strip().startswith("```"))

        return json.loads(content)

    except json.JSONDecodeError as je:
        print(f"JSON Decode Error: {je}")
        return None
    except Exception as e:
        print(f"Error during enrichment: {e}")
        return None


def enrich_attributes_vector(data: dict) -> dict:
    prompt = f"""
You are a classification system that enriches business data. Based on the following JSON input, return an "attributes_vector" JSON object that includes operational and service attributes for the business.

The input includes:
- city and postal code
- number of competitors nearby
- street type indicators (road, ave, st, etc.)
- category tags with 1 or 0 relevance

Your output must only contain this JSON structure with values 1 or 0 (except where noted):

[
  "BusinessAcceptsCreditCards", "BusinessParking", "BikeParking", "ByAppointmentOnly", "WiFi", "WheelchairAccessible",
  "GoodForKids", "HasTV", "DogsAllowed", "BusinessAcceptsBitcoin", "AcceptsInsurance", "CoatCheck", "Open24Hours",
  "total_open_hours_week", "avg_daily_hours", "open_morning_flag", "open_afternoon_flag",
  "open_evening_flag", "open_night_flag", "garden"
]

### Input
{json.dumps(data, indent=2)}

### Output
Return only a flat JSON object with no nesting.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You generate operational attributes for businesses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        print("🔍 Raw model response:\n", content)

        # Remove backticks/markdown fences if needed
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(line for line in lines if not line.strip().startswith("```"))

        attributes_dict = json.loads(content)
        return attributes_dict

    except json.JSONDecodeError as je:
        print(f" JSON Decode Error: {je}")
        return None
    except Exception as e:
        print(f" An error occurred during attribute enrichment: {e}")
        return None

def conditionally_get_dining_tags(data: dict) -> dict:
    # Define triggering tags
    dining_tag_keys = [
        "italian", "japanese", "mexican", "pizza", "salad", "sandwiches", "seafood", "spirits", "wine",
        "RestaurantsDelivery", "OutdoorSeating", "RestaurantsPriceRange2", "RestaurantsTakeOut", "Alcohol",
        "Caters", "RestaurantsReservations", "RestaurantsGoodForGroups", "HappyHour", "RestaurantsTableService",
        "DriveThru", "Corkage", "RestaurantsCounterService", "american_new", "american_traditional", "beer",
        "burgers", "caterers", "chicken_wings", "chinese", "breakfast", "brunch", "fast_food", "BYOB", "GoodForDancing"
    ]

    trigger_tags = [
        "restaurants", "bars", "food", "coffee", "tea", "nightlife", "specialty_food"
    ]


    should_trigger = any(data.get(tag, 0) == 1 for tag in trigger_tags)

    if not should_trigger:
        return {key: 0 for key in dining_tag_keys}

    return get_dining_beverage_tags(data)  # The GPT call


def enrich_dining_beverage_tags(data: dict) -> dict:
    prompt = f"""
You are a classification system that enriches business data. Given detailed information about a business (including city, type, tags, and attributes), determine which of the following tags apply.

These tags relate to food, alcohol, beverages, service types, or cuisine styles. Return a JSON object where each key is 1 (relevant) or 0 (not relevant):

[
  "italian", "japanese", "mexican", "pizza", "salad", "sandwiches", "seafood", "spirits", "wine",
  "RestaurantsDelivery", "OutdoorSeating", "RestaurantsPriceRange2", "RestaurantsTakeOut", "Alcohol", "Caters",
  "RestaurantsReservations", "RestaurantsGoodForGroups", "HappyHour", "RestaurantsTableService", "DriveThru",
  "Corkage", "RestaurantsCounterService", "american_new", "american_traditional", "beer", "burgers", "caterers",
  "chicken_wings", "chinese", "breakfast", "brunch", "fast_food", "BYOB", "GoodForDancing"
]

Return only a flat JSON object where each tag is a top-level key. Use your best judgment based on the presence of food, drink, and entertainment tags in the input.

### Input
{json.dumps(data, indent=2)}

### Output
Return only a flat JSON object with no nesting.
"""



    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Using a generally available model
            messages=[
            {"role": "system", "content": "You classify service, cuisine, and alcohol-related tags."},
            {"role": "user", "content": prompt}
        ],
            temperature=0.2,
            response_format={ "type": "json_object" } # Requesting JSON output
        )

        # Extract the content and parse the JSON
        dining_json_string = response.choices[0].message.content
        dining_dict = json.loads(dining_json_string)
        return dining_dict

    except Exception as e:
        print(f"An error occurred during dining & beverage enrichment: {e}")
        return None

def unified_enrichment(data: dict) -> dict:
    prompt = f"""
You are a business enrichment system. Given a JSON object with basic information about a business (location, competitors, street type, and base tags), return a unified enrichment result.

The result should include:
1. `tags`: Relevance of general business category tags (1 or 0)
2. `attributes`: Operational/service attributes (1 or 0)
3. `dining_tags`: Food, beverage, and dining-related tags (1 or 0)

All three should be returned as flat JSON objects.

### Input
{json.dumps(data, indent=2)}

### Output
Return tags, attributes and dining_tags as a plain JSON with all attributes in the same hierarchical level. Do not add comments or explanations.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You enrich business data across multiple tag systems."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = "\n".join(line for line in content.splitlines() if not line.strip().startswith("```"))
    return json.loads(content)

def enrichment_pipeline(input: Prediction_Input):
    merged_data=get_location_details(input.latitude, input.longitude)
    merged_data.update(encode_address_type(input.latitude, input.longitude))
    merged_data.update(enrich_business_tags(merged_data["city"], input.category))
    merged_data.update(enrich_attributes_vector(merged_data))
    merged_data.update(enrich_dining_beverage_tags(merged_data))
    merged_data.update({"n_competitors_1km": input.n_competitors_1km})
    return merged_data