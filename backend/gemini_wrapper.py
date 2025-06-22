import os
from google import genai
from google.genai import types

class GeminiWrapper:
    def __init__(self):
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("gemini api key")
            or os.environ.get("gemini_api_key")
        )
        if not api_key:
            raise ValueError("Gemini API key not found. Please set 'GEMINI_API_KEY' or 'gemini api key' in your .env file.")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def stream_response(self, prompt: str):
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            yield chunk.text

def get_gemini_llm():
    return GeminiWrapper() 