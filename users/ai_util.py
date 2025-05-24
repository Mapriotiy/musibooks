from django.conf import settings
import requests
import json

# Use with Open Router API
#
def prompt_ai(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data = json.dumps({
            "model":"deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {
                    "role":"user",
                    "content":prompt,
                }
            ]

        })
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")

# Use with Hugging_Face API
#
# def hugging_face_prompt_ai(prompt):
#     headers = {
#         "Authorization": f"Bearer {settings.HUGGING_FACE_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "inputs": prompt,
#         "parameters": {
#             "max_new_tokens": 150,
#             "return_full_text": False
#         }
#     }
#
#     url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
#
#     response = requests.post(url, headers=headers, data=json.dumps(payload))
#
#     if response.status_code == 200:
#         result = response.json()
#         return result[0]['generated_text']
#     else:
#         raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")


def extract_json_from_text(text):
    try:
        first_brace = text.index('{')
        last_brace = text.rindex('}')
        json_str = text[first_brace:last_brace+1]
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Ошибка при извлечении JSON: {e}")
        return None

def find_books(tracks):
    pass