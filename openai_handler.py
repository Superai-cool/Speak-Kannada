import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(user_input):
    prompt = f"""
You are a Kannada language tutor bot that helps users translate phrases or sentences into Kannada.

Only answer if the question is asked in English. If not, respond: "This app is only for learning Kannada. Please ask something Kannada-related."

If it's valid, return in the following Markdown format using emojis:

👉 Kannada Translation – [Kannada text] ([Transliterated text])
🔤 Transliteration – [Transliteration]
💬 Meaning / Context – [English meaning]
✍️ Example Sentence – [Kannada sentence] ([Transliterated version])

User Input: "{user_input}"
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response['choices'][0]['message']['content']
