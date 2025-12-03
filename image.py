from google import genai
from google.genai import types
from PIL import Image

prompt =  "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"

client = genai.Client(api_key="AIzaSyAEtsoD2w9OKC0S4lw85S0JEKo6r2K0JO4")

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt,
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")