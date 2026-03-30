import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]

for model in models:
    print(f"Testing model: {model}")
    try:
        llm = ChatGoogleGenerativeAI(model=model)
        response = llm.invoke("test")
        print(f"  Success: {response.content[:20]}...")
        break
    except Exception as e:
        print(f"  Failed: {e}")
