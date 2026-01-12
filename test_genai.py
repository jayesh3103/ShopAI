
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    genai.configure(api_key=api_key)
    
    # 1. Test Chat Model
    print("\n--- Testing Gemini Chat ---")
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        chat = model.start_chat(history=[
            {"role": "user", "parts": ["Hello"]},
            {"role": "model", "parts": ["Hi there!"]}
        ])
        response = chat.send_message("What is the capital of India?")
        print("Chat Success! Response:", response.text)
    except Exception as e:
        print(f"Chat execution failed: {e}")

    # 2. Test Embeddings
    print("\n--- Testing Embeddings ---")
    try:
        embed_service = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        vector = embed_service.embed_query("Test query")
        print(f"Embedding Success! Vector length: {len(vector)}")
    except Exception as e:
        print(f"Embedding failed: {e}")
