import openai
import os
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def is_english(text):
    return re.fullmatch(r'[A-Za-z0-9\s\?\.\!\,\']+', text.strip()) is not None

def generate_kannada_translation(prompt):
    if not is_english(prompt):
        return {
            "error": "Please ask your question in English only."
        }

    system_instruction = """
You are a helpful Kannada language expert. You help users translate and understand Kannada from English phrases.

Format the response in 4 bold sections with emojis:
👉 **Kannada Translation** – (Kannada script with English transliteration in brackets)
🎯 **Transliteration** – (Latin script)
💬 **Meaning / Context** – (Short English explanation)
✍️ **Example Sentence** – (A real-world sentence in Kannada with English transliteration in brackets)

Avoid extra information. Keep it brief and relevant to the input. Always translate assuming the user is trying to speak in Kannada.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return {"answer": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": f"OpenAI error: {str(e)}"}
