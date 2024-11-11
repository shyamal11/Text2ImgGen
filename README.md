# Image Generation Service

This service generates podcast cover images using AI models like OpenAI's DALL·E and Hugging Face's model, and stores the generated images in MongoDB. The app takes podcast episode titles and an episode ID as input, generates a relevant image, and saves it in the MongoDB database under the corresponding episode.

## Features
- **Podcast Cover Image Generation**: Uses GPT-based prompts to create image descriptions and AI models to generate podcast cover art.
- **MongoDB Storage**: Saves the generated podcast cover image as binary data in MongoDB, ensuring easy retrieval.
- **Integration with OpenAI and Hugging Face APIs**: Uses both OpenAI (DALL·E) and Hugging Face for image generation with fallback logic.

## Prerequisites
- **MongoDB**: Access to a MongoDB instance.
- **OpenAI API Key**: For accessing GPT and DALL·E models.
- **Hugging Face API Key**: For image generation if OpenAI fails.
- **Environment Variables**:
  - `MONGODB_URI`: MongoDB connection URI
  - `OPENAI_API_KEY`: API key for OpenAI
  - `OPENAI_ORGANIZATION_ID`: OpenAI Organization ID
  - `HUGGING_FACE_API`: Hugging Face API key
  - **Dependencies**: Ensure Python libraries are installed using `pip install -r requirements.txt`



