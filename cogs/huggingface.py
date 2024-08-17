import aiohttp
import os

# Assuming you will store the Hugging Face API key in your repository secrets or environment variables
async def generate_text(prompt: str) -> str:
    """
    Generates text using the Hugging Face Inference API.
    
    Args:
        prompt (str): The text prompt to generate a response for.
    
    Returns:
        str: The generated text or an error message.
    """
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    model = "gpt2"  # You can specify another model available on Hugging Face

    if not api_key:
        return "Hugging Face API key is missing. Please set the HUGGINGFACE_API_KEY environment variable."

    url = f"https://api-inference.huggingface.co/models/{model}"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'inputs': prompt
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result[0].get('generated_text', 'No output from Hugging Face API')
            else:
                return f"Error: {response.status} - {response.reason}"
