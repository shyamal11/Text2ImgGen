import redis
import os

# Connect to Redis
redis_url = os.getenv("REDIS_URL")
r = redis.from_url(redis_url)

# Define your episode ID
episode_id = 'your_episode_id'

# Fetch data from Redis
episode_data = r.get(episode_id)

if episode_data:
    print(f"Data for episode ID {episode_id}: {episode_data.decode('utf-8')}")
else:
    print(f"No data found for episode ID {episode_id}.")
