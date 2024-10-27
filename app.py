# app.py
import os
import time
import requests
import io
from flask import Flask, request, jsonify
from PIL import Image
from pymongo import MongoClient
from dotenv import load_dotenv
import openai
from bson.binary import Binary 
from prompts import GPT_PROMPTS  # Import the prompt dictionary

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["podcast-as-a-service"]  # Database name
collection = db["episode_library"]  # Collection name

# Constants
MAX_RETRIES = 1
RETRY_DELAY = 2
TEXT_MODEL = "gpt-4o-mini"
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/XLabs-AI/flux-RealismLora"


def initialize_openai():
    return openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORGANIZATION_ID")
    )


def ask_gpt(openai_client, input_ask, role="system"):
    for _ in range(MAX_RETRIES):
        try:
            completion = openai_client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": input_ask}
                ]
            )
            response = completion.choices[0].message.content
            return response.lower().strip().strip('.') if isinstance(response, str) else None
        except Exception as e:
            print(f"Error asking GPT: {e}")
            time.sleep(RETRY_DELAY)
    return None


def generate_image(image_prompt):
    headers = {"Authorization": f"Bearer {os.getenv('HUGGING_FACE_API')}"}

    try:
        response = requests.post(HUGGING_FACE_API_URL, headers=headers, json={"inputs": image_prompt})
        response.raise_for_status()
        huggingface_model_image = Image.open(io.BytesIO(response.content))

        image_file = io.BytesIO()
        huggingface_model_image.save(image_file, format='JPEG')
        image_file.seek(0)
        print("Image - HuggingFace successfully generated.")
        return image_file.read()
        
    except Exception as e:
        print(f"Error generating image from Hugging Face model: {e}")
        return fallback_to_openai(image_prompt)


def fallback_to_openai(image_prompt):
    openai_client = initialize_openai()
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        print("Image - OpenAI successfully generated.")
        return image_response.content
    except Exception as e:
        print(f"Error generating image with OpenAI API: {e}")
        return None


@app.route('/', methods=['GET'])
def home():
    return "Hi from the image generation module!"

@app.route('/generate_podcast_cover', methods=['POST'])
def generate_podcast_cover():
    data = request.json
    titles = data.get("titles")
    episode_id = data.get("episode_id")

    if not titles or not episode_id:
        return jsonify({"error": "Missing required 'titles' or 'episode_id'"}), 400

    print("Podcast Cover Art Generation Started...")

    openai_client = initialize_openai()
    gpt_prompt = titles + GPT_PROMPTS["podcast_cover"]
    image_prompt = ask_gpt(openai_client, gpt_prompt)
    
    if not image_prompt:
        return jsonify({"error": "Failed to generate image prompt"}), 500

    image_data = generate_image(image_prompt)

    if not image_data:
        return jsonify({"error": "Failed to generate image"}), 500

    # Check if the document with the given episode_id exists
    existing_document = collection.find_one({"episode_id": episode_id})

    if existing_document:
        print(f"Episode ID {episode_id} found. Updating cover image.")
        try:
            # Update the document if it exists
            collection.update_one(
                {"episode_id": episode_id},
                {"$set": {"cover_image": Binary(image_data)}}
            )
            print("Image updated in MongoDB successfully.")
        except Exception as e:
            print(f"Error updating image to MongoDB: {e}")
            return jsonify({"error": "Failed to update image to MongoDB"}), 500
    else:
        print(f"Episode ID {episode_id} not found. Inserting new document.")
        try:
            # If it does not exist, insert a new document
            collection.insert_one({
                "episode_id": episode_id,
                "cover_image": Binary(image_data)
            })
            print("Image saved to MongoDB successfully.")
        except Exception as e:
            print(f"Error saving image to MongoDB: {e}")
            return jsonify({"error": "Failed to save image to MongoDB"}), 500

    return jsonify({"message": "Podcast cover generated and saved successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

