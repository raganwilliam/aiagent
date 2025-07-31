import sys

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

from google.genai import types

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

def main():
    try:
       response = client.models.generate_content(
            model="gemini-2.0-flash-001", 
            contents=messages,
            )
        print(response.text)
    except IndexError:
        print("No input provided. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()


