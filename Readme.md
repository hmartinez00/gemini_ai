# gemini_ai — Uso y configuración del script `app.py`

Este repositorio contiene un script sencillo (`app.py`) que usa la SDK de Google GenAI para enviar prompts a un modelo (streaming o no), y guardar la respuesta en un archivo `reply.md`.

---

## ✅ Requisitos previos

- Python 3.10 o superior.
- Una API key de Google GenAI (Gemini Developer API / Gemini API). No es recomendable subir la API Key a un repositorio público.
- Conexión a internet para invocar la API.

---

## 🔧 Estructura básica del proyecto

- `app.py` — Script principal que carga la configuración, lee el prompt y escribe la respuesta en `consultas_gemini/reply.md`.
- `settings/api/settings.json` — Archivo donde almacenamos la API key y otras variables de configuración.
- `consultas_gemini/ask.md` — Archivo de entrada con el texto/pregunta a enviar a la API (ahora reemplaza a `quest.md`).
- `consultas_gemini/reply.md` — Resultado de la respuesta (salida), creado por `app.py`.
- `consultas_gemini/backups/` — Carpeta de respaldo (no necesaria para ejecución), se puede usar para almacenar backups.

---

## 📂 Archivo de configuración `settings/api/settings.json`

Ejemplo básico del contenido que requiere el script:

```json
{
  "api": "YOUR_GOOGLE_GENERATIVE_API_KEY"
}
```

Notas:
 - Cambiar `YOUR_GOOGLE_GENERATIVE_API_KEY` con la API key real.
 - Si trabajas con un equipo o repositorio público, evita almacenar claves dentro del repo. En su lugar, carga la key por variable de entorno o en un archivo fuera del control de versiones.
 - Si desea incluir varios prompts o `queries`, puede ampliar el archivo `settings.json` con campos adicionales, pero no es requerido por `app.py` si solo utiliza la clave `api`.

---

## 🧰 Dependencias (sugeridas)
Basado en `app.py` y la SDK encontrada, se recomiendan las siguientes librerías:

- `google-genai>=1.52.0` (SDK de Google GenAI)
- `ipython` (solo si necesitas usar IPython.display; opcional)

Puedes crear un `requirements.txt` con:

```
google-genai==1.52.0
ipython
```

---

## 🛠️ Crear entorno virtual & instalar dependencias (PowerShell — Windows)

Ejecuta estos comandos en tu terminal PowerShell en la raíz del proyecto (`C:\laragon\www\gemini_ai`):

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate

# Actualizar pip (recomendado)
python -m pip install --upgrade pip

# Instalar dependencias (si existe requirements.txt)
pip install -r requirements.txt

# O instalar paquetes manualmente
pip install google-genai ipython
```

---

## ⚙️ Configuración de la API Key

El script `app.py` lee la API key desde `settings/api/settings.json` en la clave `api`. Asegúrate de colocar la key en ese fichero.

Alternativa (recomendado por seguridad): usar variables de entorno:

```powershell
setx GOOGLE_API_KEY "<YOUR_KEY>"
```

y modificar `app.py` para leer la variable de entorno:

```python
import os
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

---

## ▶️ Funcionamiento principal del `app.py`

Resumen del flujo en `app.py`:

1. Carga la API key desde `settings/api/settings.json` (o similar).
2. Inicializa la instancia del cliente: `client = genai.Client(api_key=GOOGLE_API_KEY)`.
3. Abre el archivo `consultas_gemini/ask.md` para leer el prompt que se enviará a la API.
4. Llama a `client.models.generate_content_stream(...)` para obtener la respuesta en streaming.
5. Recorre el `response_stream`, escribe fragmentos en `consultas_gemini/reply.md` y los imprime en la consola.

Ejemplo (fragmento relevante):

```python
response_stream = client.models.generate_content_stream(
		model='gemini-2.0-flash-001',
		contents=types.Part.from_text(text=quest),
		config=types.GenerateContentConfig(temperature=0, top_p=0.95, top_k=20),
)

with open(r'consultas_gemini\reply.md', 'w', encoding='utf-8') as f:
		for chunk in response_stream:
				if chunk.text:
						f.write(chunk.text)
						f.flush()
						print(chunk.text, end='', flush=True)

client.close()
```

Notas:
- El `model` usado por defecto en este repositorio es `gemini-2.0-flash-001`. Si obtienes un error 404, verifica que el modelo sea compatible con la API version (p. ej., `gemini-pro` puede no soportar `generate_content` en la API actual, o el endpoint/API version puede no admitirlo).
- `types.Part.from_text` crea un objeto con el texto a enviar al modelo.
- El streaming permite ver progresivamente la respuesta y escribirla en disco a medida que llega.

---

## ⏸️ Añadir una pausa interactiva: "¿Desea continuar con la iteración?" (opcional)

Si deseas pausar la iteración para confirmar que continúe entre fragmentos (o al finalizar cada chunk), puedes modificar el bucle de streaming con algo como esto:

```python
with open(r'consultas_gemini\reply.md', 'w', encoding='utf-8') as f:
		for i, chunk in enumerate(response_stream, start=1):
				if chunk.text:
						f.write(chunk.text)
						f.flush()
						print(chunk.text, end='', flush=True)

				# Pausar tras cada X fragments o tras cada chunk (según prefieras)
				if i % 3 == 0:  # pausar cada 3 chunks
						respuesta = input('\nPausado: ¿Desea continuar con la iteración? [s/N]: ').strip().lower()
						if respuesta not in ('s', 'si', 'y', 'yes'):
								print('Interrupción solicitada. Finalizando stream.')
								break

client.close()
```

Esto es útil cuando se requiere revisión humana durante la generación o para evitar consumir tokens innecesarios.

---

## ❗ Errores comunes y soluciones

- Error 404 NOT_FOUND - "models/gemini-pro is not found for API version v1beta":
	- Cambia el `model` a uno soportado por tu API version, por ejemplo `gemini-2.0-flash-001`. También revisa la documentación o lista de modelos soportados.
	- También puedes invocar la API para listar modelos con `client.models.list()` y revisar los modelos disponibles.

	Ejemplo para listar modelos disponibles:

	```python
	from google import genai
	import json

	with open('settings/api/settings.json') as f:
			data = json.load(f)
	client = genai.Client(api_key=data.get('api'))

	models = client.models.list()
	for m in models:
			print(m.name)

	client.close()
	```

- ModuleNotFoundError: No module named 'pkg_resources':
	- Ejecuta `pip install setuptools` o `pip install -r requirements.txt` para asegurar paquetes base como setuptools y pkg_resources.

- Problemas de encoding o caracteres raros en Windows:
	- Asegúrate de que se configure `sys.stdout.reconfigure(encoding='utf-8')` si usas consola con problemas de encoding. Alternativamente, usa PowerShell o Windows Terminal que soporte UTF-8.

- Protección de la API Key:
	- No subas `settings/api/settings.json` con la API key en git. Añade esa ruta al `.gitignore` o usa variables de entorno.

---

## 🔍 Pruebas y ejecución rápida

Después de configurar el entorno y la API key, ejecuta el script con:

```powershell
# Activar venv
.\venv\Scripts\Activate

# Ejecutar el script
py .\app.py
```

Observa la consola para la salida en streaming y revisa `consultas_gemini/reply.md` cuando termine.

---

## 📌 Resumen y recomendaciones

- Usa `google-genai` versión compatible con tu Python (>=3.10)
- Mantén la `api_key` fuera del control de versiones.
- Si necesitas implementar un modo interactivo (pausa), usa `input()` en el bucle de streaming tal como se muestra.
- Revisa los modelos disponibles en la SDK si obtienes errores 404: `client.models.list()`.

Si deseas, puedo:
- Añadir un `requirements.txt` y/o `pyproject.toml` con las dependencias.
- Añadir validación en `app.py` para detectar si la API key está presente y avisar al usuario si falta.
- Implementar el comportamiento de pausa por defecto (opcional).

---

¡Listo! Si quieres, hago cambios adicionales o agrego scripts para automatizar la creación del venv y la instalación de dependencias.

