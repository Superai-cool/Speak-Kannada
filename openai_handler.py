import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_kannada_translation(user_input):
    prompt = f"""You are a helpful AI assistant helping users learn conversational Kannada.

Translate the following user query to Kannada with:
1. Kannada Translation
2. Transliteration (Kannada in English letters)
3. Meaning / Context in English
4. Example sentence in Kannada + Transliteration

Input: {user_input}
Only return formatted output like this:

📌 Kannada Translation – ...
🔤 Transliteration – ...
💬 Meaning / Context – ...
✍️ Example Sentence – ...
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    reply = response["choices"][0]["message"]["content"]
    return reply
