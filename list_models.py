import os
import requests

API_KEY = os.getenv("GOOGLE_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json().get("models", [])
    for m in models:
        print(m["name"])
else:
    print(f"Failed: {response.text}")
