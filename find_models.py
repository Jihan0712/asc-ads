from google import genai

# Paste your actual key here inside the quotes
client = genai.Client(api_key="AIzaSyAjqa8GQzLUidWFHic_xoRMA3PrSzvcly4") 

print("Checking available models for your API key...")
print("-" * 50)

try:
    # List all available models directly
    for model in client.models.list():
        print(f"Model ID: {model.name}")
except Exception as e:
    print(f"An error occurred: {e}")