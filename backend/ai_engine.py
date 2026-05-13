from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_content(content, platform, tone):

    prompt = f"""
    Convert the following content into a {platform} post.
    Tone: {tone}

    Content:
    {content}
    """

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