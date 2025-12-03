# Importamos Gemini Pro, textwrap, IPython, sys, para soporte Para Caracteres Especiales en la Terminal de Python
from google import genai
from google.genai import types
from pathlib import Path
import sys
import json
import argparse

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SETTINGS_PATH = BASE_DIR / 'settings' / 'api' / 'settings.json'
DEFAULT_ASK_PATH = BASE_DIR / 'consultas_gemini' / 'ask.md'
DEFAULT_REPLY_PATH = BASE_DIR / 'consultas_gemini' / 'reply.md'
DEFAULT_BACKUPS_DIR = BASE_DIR / 'consultas_gemini' / 'backups'


def parse_args():
    parser = argparse.ArgumentParser(description='Enviar consultas a Gemini y guardar la respuesta en un fichero.')
    parser.add_argument('--ask', default=str(DEFAULT_ASK_PATH), help='Ruta del archivo Markdown con la pregunta/prompt (por defecto: consultas_gemini/ask.md)')
    parser.add_argument('--reply', default=str(DEFAULT_REPLY_PATH), help='Ruta del archivo de salida donde se escribirá la respuesta (por defecto: consultas_gemini/reply.md)')
    parser.add_argument('--settings', default=str(DEFAULT_SETTINGS_PATH), help='Ruta al archivo settings.json (por defecto: settings/api/settings.json)')
    parser.add_argument('--dry-run', action='store_true', help='No llamar a la API; solo validar archivos y rutas')
    return parser.parse_args()


def validate_and_build_paths(settings_path, ask_path, reply_path):
    SETTINGS_PATH = Path(settings_path)
    ASK_PATH = Path(ask_path)
    REPLY_PATH = Path(reply_path)
    BACKUPS_DIR = REPLY_PATH.parent / 'backups'

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_PATH.exists():
        print(f"Archivo de configuración no encontrado: {SETTINGS_PATH}")
        print("Crea el archivo con la clave `api` dentro o ajusta la ruta en el script.")
        sys.exit(1)

    return SETTINGS_PATH, ASK_PATH, REPLY_PATH, BACKUPS_DIR

client = None


def main():
    args = parse_args()
    settings_path, ask_path, reply_path, backups_dir = validate_and_build_paths(args.settings, args.ask, args.reply)

    # Abrir el archivo JSON
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Configuramos la API KEY
    google_api_key = data.get('api') or ''
    if not google_api_key:
        print('API key no encontrada en el archivo settings.json. Coloca "api": "<YOUR_KEY>" en el archivo')
        sys.exit(1)

    if args.dry_run:
        print('Modo dry-run. Rutas detectadas:')
        print(' - settings:', settings_path.resolve())
        print(' - ask:', ask_path.resolve())
        print(' - reply:', reply_path.resolve())
        print(' - backups:', backups_dir.resolve())
        return

    # Instanciar cliente
    global client
    client = genai.Client(api_key=google_api_key)

    # Abrir el archivo en modo lectura
    if not ask_path.exists():
        print(f'Archivo de entrada {ask_path} no encontrado. Crea `ask.md` y escribe la consulta en Markdown antes de ejecutar.')
        sys.exit(1)

    # Leer el prompt del archivo ask.md (en UTF-8)
    quest = ask_path.read_text(encoding='utf-8')
    if not quest.strip():
        print(f'El archivo {ask_path} está vacío. Escribe la pregunta/prompt en Markdown y vuelve a ejecutar.')
        sys.exit(1)

    print(f"Usando archivo de configuración: {settings_path}")
    try:
        # Obtenemos la respuesta en streaming
        response_stream = client.models.generate_content_stream(
        # model='gemini-2.0-flash-001',
        model='gemini-2.5-flash',
        contents=types.Part.from_text(text=quest),
        config=types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=20,
        ),
    )
        # Abrir el archivo en modo escritura (append)
        reply_path.parent.mkdir(parents=True, exist_ok=True)
        with open(reply_path, 'w', encoding='utf-8') as f:  # Usamos 'w' para sobreescribir el archivo al inicio
            for chunk in response_stream:
                if chunk.text:  # Verifica que el fragmento contenga texto
                    f.write(chunk.text)
                    f.flush()  # Asegura que los datos se escriban inmediatamente en el disco
                    print(chunk.text, end="", flush=True) # Imprime en la consola para ver el progreso
    finally:
        # Asegura que el cliente se cierre aún en caso de excepción
        try:
            if client:
                client.close()
        except Exception:
            pass

    print("\nRespuesta completa escrita en reply.md")


if __name__ == '__main__':
    main()