# prompts.py
GPT_PROMPTS = {
    "podcast_cover": f'''
        Use these news titles to generate a description of an image formed if I'm using these three titles to create a cover image for a podcast episode. Create 1 coherent image instead of images separately talking about each title. I don't want any text in the image. 
        Only output the description.
        Example: 
        A cohesive podcast cover image featuring a nighttime scene of the Earth from space, with a focus on Indonesia illuminated by city lights. A sleek satellite in orbit, symbolizing Elon Musk's Starlink, beams a vibrant signal down to the Indonesian archipelago. In the foreground, a modern computer monitor with a holographic AI interface glows with dynamic data streams, representing Microsoft's AI integration. To the right, a stylish pair of wireless headphones from Sonos hovers, emitting colorful sound waves that blend into the background. The elements merge seamlessly, creating a unified, futuristic composition that highlights the innovation and connectivity of these tech advancements.
    '''
}
