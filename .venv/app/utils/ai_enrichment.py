import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("openai_key")

# Create OpenAI client using new API (v1.x)
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
Return only the attributes_vector JSON object.
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

# Example usage
if __name__ == "__main__":
    # Example dummy data
    merged_data = {
        "city": "New York",
        "postal_code": "10001",
        "num_competitors": 12,
        "street_type": {
            "road": 0,
            "ave": 1,
            "st": 0
        },
        "tags": {
            "restaurants": 1,
            "coffee": 1,
            "fitness": 0,
            "nail_salons": 0,
            "bars": 1
        }
    }

    attributes = enrich_attributes_vector(merged_data)
    if attributes:
        print(json.dumps(attributes, indent=2))