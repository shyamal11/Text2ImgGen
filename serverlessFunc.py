import os
import requests
from pymongo import MongoClient
from bson.binary import Binary 

# Load environment variables
api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")
hugging_face_api = os.getenv("HUGGING_FACE_API")
hugging_face_api_url = "https://api-inference.huggingface.co/models/XLabs-AI/flux-RealismLora"
openai_api_url = "https://api.openai.com/v1/images/generations"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["podcast-as-a-service"]
collection = db["episode_library"]

def main(request):
    # Parse JSON from request body
    image_prompt = request.get("image_prompt")
    episode_id = request.get("episode_id")  # Default episode ID if none provided

    headers_hf = {"Authorization": f"Bearer {hugging_face_api}"}
    headers_openai = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Try generating image with Hugging Face model
        raise requests.RequestException("Simulated failure for testing")
        response = requests.post(hugging_face_api_url, headers=headers_hf, json={"inputs": image_prompt})
        response.raise_for_status()
        image_data = response.content  # Hugging Face image data

    except requests.RequestException:
        # If Hugging Face API fails, fall back to OpenAI DALL-E 3
        payload = {
            "model": "dall-e-3",
            "prompt": image_prompt,
            "size": "1024x1024",
            "n": 1
        }
        try:
            response = requests.post(openai_api_url, headers=headers_openai, json=payload)
            response.raise_for_status()
            image_url = response.json()['data'][0]['url']
            
            # Fetch the image data from OpenAI's generated URL
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_data = image_response.content  # OpenAI image data

        except Exception as e:
            return {"body": f"Both Hugging Face and OpenAI requests failed: {e}"}

    # Store the final image data in MongoDB
    try:
        collection.update_one(
            {"episode_id": episode_id},
            {"$set": {"cover_image": Binary(image_data)}},
            upsert=True
        )
        return {"body": "Image data saved to MongoDB"}

    except Exception as e:
        return {"body": f"Error saving to MongoDB: {e}"}
