import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(user_input):
    try:
        # Prompt that instructs GPT to return a clear 4-part structured response
        prompt = f"""
You are a Kannada language assistant. Given a sentence or phrase in English or Hindi, respond ONLY if the query is in English and provide:

1. Kannada Translation with pronunciation.
2. English Transliteration of Kannada.
3. Meaning / Context in English.
4. Example Sentence using Kannada with English transliteration.

Respond in the below format using Unicode Kannada + Transliteration and English:
👉 **Kannada Translation** – ...  
🎯 **Transliteration** – ...  
💬 **Meaning / Context** – ...  
✍️ **Example Sentence** – ...

Input: {user_input}
Only answer if question is in English.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for learning Kannada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = response['choices'][0]['message']['content']
        return reply.strip()

    except Exception as e:
        print("OpenAI Error:", e)
        return "⚠️ Sorry, something went wrong while generating the translation."
