from flask import Flask, request, jsonify
import os
import requests
from pymongo import MongoClient
from bson.binary import Binary

app = Flask(__name__)

# Environment variables
api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")
hugging_face_api = os.getenv("HUGGING_FACE_API")
hugging_face_api_url = "https://api-inference.huggingface.co/models/XLabs-AI/flux-RealismLora"
openai_api_url = "https://api.openai.com/v1/images/generations"

# MongoDB connection
client = MongoClient(mongo_uri)
db = client["podcast-as-a-service"]
collection = db["episode_library"]

# Route to generate image
@app.route('/generate_image', methods=['POST'])

def generate_image():
    print(f"get hit")
    data = request.json
    image_prompt = data.get("image_prompt")
    episode_id = data.get("episode_id")


    headers_hf = {"Authorization": f"Bearer {hugging_face_api}"}
    headers_openai = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # First attempt: Hugging Face API
        print(f"calling hugsging face")
        response = requests.post(hugging_face_api_url, headers=headers_hf, json={"inputs": image_prompt})
        response.raise_for_status()
      
        image_data = response.content
        generation_source = "Hugging Face API"

    except requests.RequestException:
        # If Hugging Face API fails, fallback to OpenAI API
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

            # Fetch the image from the generated URL
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_data = image_response.content
            generation_source = "OpenAI API"

        except Exception as e:
            return jsonify({"error": f"Both Hugging Face and OpenAI requests failed: {str(e)}"}), 500

    # Store the generated image in MongoDB
    try:
        collection.update_one(
            {"episode_id": episode_id},
            {"$set": {"cover_image": Binary(image_data)}},
            upsert=True
        )
        return jsonify({"message": f"Image data generated using {generation_source}"})

    except Exception as e:
        return jsonify({"error": f"Error saving to MongoDB: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
