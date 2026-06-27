import google.generativeai as genai

# Replace with your actual key
genai.configure(api_key="API_KEY")

# List all models available to your key
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)