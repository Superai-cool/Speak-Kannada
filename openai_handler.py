import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(user_input):
    prompt = f"""
You are a Kannada language teacher. When someone gives a sentence or phrase in any language,
your task is to return the following in Kannada in a clear and helpful way.

Respond ONLY if it's a Kannada-learning-related sentence. If not, reply:
"This app is only for learning Kannada. Please ask something Kannada-related."

Example Output Format:
👉 **Kannada Translation** – ...
🧠 **Transliteration** – ...
💬 **Meaning / Context** – ...
✍️ **Example Sentence** – ...

Now respond to: "{user_input}"
"""

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    return completion.choices[0].message["content"]
