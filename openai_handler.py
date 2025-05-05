import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_kannada_translation(user_input):
    prompt = f"""
You are a Kannada language tutor bot that helps users translate English phrases into Kannada.

Only respond if the user is asking something about how to say something in Kannada. If the input is not related to learning Kannada, reply with:

"This app is only for learning Kannada. Please ask something Kannada-related."

Otherwise, give your answer in the following format using emojis and markdown styling:

👉 **Kannada Translation** – [Kannada text] ([Transliteration])  
🔤 **Transliteration** – [Transliteration only]  
💬 **Meaning / Context** – [Brief English meaning]  
✍️ **Example Sentence** – [Kannada sentence] ([Transliteration])

User Input: "{user_input}"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Or whichever model you prefer
            messages=[
                {"role": "system", "content": "You are a helpful language tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response['choices'][0]['message']['content']
        return answer.strip()

    except Exception as e:
        print("OpenAI Error:", e)
        return "⚠️ Sorry, something went wrong. Please try again."
