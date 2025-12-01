# Importamos Gemini Pro, textwrap, IPython, sys, para soporte Para Caracteres Especiales en la Terminal de Python
from google import genai
from google.genai import types
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

# Abrir el archivo JSON
with open(r'settings\api\settings.json', 'r') as f:
    data = json.load(f)

# Configuramos la API KEY
GOOGLE_API_KEY=data['api']
# genai.configure(api_key=GOOGLE_API_KEY)
client = genai.Client(api_key=GOOGLE_API_KEY)

# Abrir el archivo en modo lectura
with open(r'consultas_gemini\ask.md', 'r', encoding='utf-8') as archivo:
    # Leer el contenido del archivo
    quest = archivo.read()

# Obtenemos la respuesta en streaming
response_stream = client.models.generate_content_stream(
    model='gemini-2.0-flash-001',
    contents=types.Part.from_text(text=quest),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
    ),
)

# Abrir el archivo en modo escritura (append)
with open(r'consultas_gemini\reply.md', 'w', encoding='utf-8') as f:  # Usamos 'w' para sobreescribir el archivo al inicio
    for chunk in response_stream:
        if chunk.text:  # Verifica que el fragmento contenga texto
            f.write(chunk.text)
            f.flush()  # Asegura que los datos se escriban inmediatamente en el disco
            print(chunk.text, end="", flush=True) # Imprime en la consola para ver el progreso

print("\nRespuesta completa escrita en reply.md")