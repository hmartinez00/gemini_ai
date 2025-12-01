# Importamos Gemini Pro, textwrap, IPython, sys, para soporte Para Caracteres Especiales en la Terminal de Python
from google import genai
from google.genai import types
from pathlib import Path
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

# ----------------------------------------------------------
# Rutas y archivos usados en el script (ruta relativa al repo)
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / 'settings' / 'api' / 'settings.json'
ASK_PATH = BASE_DIR / 'consultas_gemini' / 'ask.md'
REPLY_PATH = BASE_DIR / 'consultas_gemini' / 'reply.md'
BACKUPS_DIR = BASE_DIR / 'consultas_gemini' / 'backups'

BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

if not SETTINGS_PATH.exists():
    print(f"Archivo de configuración no encontrado: {SETTINGS_PATH}")
    print("Crea el archivo con la clave `api` dentro o ajusta la ruta en el script.")
    sys.exit(1)

# Abrir el archivo JSON
with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Configuramos la API KEY
# Obtener API KEY
GOOGLE_API_KEY = data.get('api') or ''
if not GOOGLE_API_KEY:
    print('API key no encontrada en el archivo settings.json. Coloca "api": "<YOUR_KEY>" en el archivo')
    sys.exit(1)
# genai.configure(api_key=GOOGLE_API_KEY)
client = genai.Client(api_key=GOOGLE_API_KEY)

# Abrir el archivo en modo lectura
if not ASK_PATH.exists():
    print(f'Archivo de entrada {ASK_PATH} no encontrado. Crea `ask.md` y escribe la consulta en Markdown antes de ejecutar.')
    sys.exit(1)

# Leer el prompt del archivo ask.md (en UTF-8)
quest = ASK_PATH.read_text(encoding='utf-8')
if not quest.strip():
    print(f'El archivo {ASK_PATH} está vacío. Escribe la pregunta/prompt en Markdown y vuelve a ejecutar.')
    sys.exit(1)

print(f"Usando archivo de configuración: {SETTINGS_PATH}")
try:
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
    REPLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPLY_PATH, 'w', encoding='utf-8') as f:  # Usamos 'w' para sobreescribir el archivo al inicio
        for chunk in response_stream:
            if chunk.text:  # Verifica que el fragmento contenga texto
                f.write(chunk.text)
                f.flush()  # Asegura que los datos se escriban inmediatamente en el disco
                print(chunk.text, end="", flush=True) # Imprime en la consola para ver el progreso
finally:
    # Asegura que el cliente se cierre aún en caso de excepción
    try:
        client.close()
    except Exception:
        pass

print("\nRespuesta completa escrita en reply.md")