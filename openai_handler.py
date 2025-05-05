# openai_handler.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_kannada_translation(user_input):
    prompt = f"""You are a Kannada language assistant.

When someone asks: "{user_input}", generate a Kannada learning response in the following format, each on a new line:

👉 **Kannada Translation** – [Kannada here]  
🧿 **Transliteration** – [English transliteration]  
💬 **Meaning / Context** – [Brief English explanation]  
✍️ **Example Sentence** – [Full Kannada + Transliteration + English meaning]  

Only respond in this format. Do not include extra messages or promotional text."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You help people learn Kannada with clarity and friendly tone."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
