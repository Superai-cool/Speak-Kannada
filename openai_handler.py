import openai
import os

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_kannada_translation(user_message):
    system_prompt = """
You are a Kannada language tutor. Your job is to help users translate and learn Kannada by responding to any sentence they type in any language.

Only give Kannada-related translations. Your format must be:

👉 Kannada Translation – [Kannada sentence] (transliterated form)
🎯 Transliteration – [transliterated Kannada sentence]
💬 Meaning / Context – [explanation in English]
✍️ Example Sentence – [example in Kannada with transliteration and meaning]

Do not reject or deny any sentence. Always assume the user wants to learn how to say that sentence in Kannada.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": user_message }
        ]
    )

    return response.choices[0].message.content.strip()
