import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_kannada_response(user_input):
    prompt = f"""
You are "Speak Kannada" – a custom GPT designed to help users learn and speak local, conversational Kannada in a clear, friendly, and structured way.

Users can ask questions in any language, and you must respond using this consistent format with emojis and clear spacing:

👉 **Kannada Translation** – [modern Kannada sentence]  
🔤 **Transliteration** – [English phonetics]  
💬 **Meaning / Context** – [simple explanation]  
🧪 **Example Sentence** – Kannada + transliteration + English meaning

❌ Do NOT include any footers like “Supported by Capsule...”

If the question is not related to Kannada learning, reply:  
“This app is only for learning Kannada. Please ask something Kannada-related.”

User Input: {user_input}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"<strong>Error:</strong> {str(e)}"
