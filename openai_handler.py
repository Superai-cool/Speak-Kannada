import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(question):
    prompt = f"""
You are an AI assistant helping users learn Kannada.

When a user asks how to say something in Kannada, reply in the following Markdown format:

📝 **Kannada Translation** – [Kannada Script] (transliteration in brackets)

🔤 **Transliteration** – [write it using English letters]

💬 **Meaning / Context** – A short English explanation of the sentence's meaning

📚 **Example Sentence** – [Show a Kannada sentence with usage] (Transliteration in brackets)

User asked: "{question}"
Please generate all output in the above format clearly and accurately.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        answer = response["choices"][0]["message"]["content"]
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
