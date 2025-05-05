import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(question):
    prompt = f"""
You are a Kannada language learning assistant.

If the input question is unrelated to learning Kannada, reply:
"This app is only for learning Kannada. Please ask something Kannada-related."

If it's a valid Kannada question, respond with:
👉 **Kannada Translation** – [Kannada text]  
🧿 **Transliteration** – [Transliteration]  
💬 **Meaning / Context** – [Context]  
✍️ **Example Sentence** – [Example sentence]

Question: {question}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Kannada tutor who gives translations with explanation."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']
