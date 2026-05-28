from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


def generate_content(content, platform, tone):
    """
    Generates content using Groq API.
    Instantiates client inside the function to prevent import-time crashes.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is not configured. Please set it in your environment variables or .env file."

    prompt = f"""
    Convert the following content into a {platform} post.
    Tone: {tone}

    Content:
    {content}
    """

    try:
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant"
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error during AI content generation: {str(e)}"