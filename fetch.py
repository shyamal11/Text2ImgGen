# fetch_cover_image.py

import os
import sys
from pymongo import MongoClient
from bson.binary import Binary
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["podcast-as-a-service"]  # Database name
collection = db["episode_library"]  # Collection name

def fetch_and_save_cover_image(episode_id, save_directory="images"):
    if not episode_id:
        raise ValueError("episode_id is required")

    try:
        # Fetch the document from MongoDB
        document = collection.find_one({"episode_id": episode_id})

        if not document or "cover_image" not in document:
            raise FileNotFoundError(f"No cover image found for episode ID: {episode_id}")

        # Get the image data from the document
        image_data = document["cover_image"]

        # Ensure the save directory exists
        os.makedirs(save_directory, exist_ok=True)

        # Define the local file path where the image will be saved
        file_path = os.path.join(save_directory, f"{episode_id}_cover.jpg")

        # Save the image data to a file
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)

        print(f"Cover image for episode ID {episode_id} saved successfully at {file_path}.")
        return file_path

    except Exception as e:
        print(f"Error fetching or saving image: {e}")
        raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_cover_image.py <episode_id>")
        sys.exit(1)

    episode_id = sys.argv[1]

    try:
        fetch_and_save_cover_image(episode_id)
    except Exception as e:
        print(f"Failed to fetch and save cover image: {e}")

if __name__ == "__main__":
    main()
