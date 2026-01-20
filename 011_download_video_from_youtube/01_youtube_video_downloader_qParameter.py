import subprocess
import os

# ========================== HEADER ==========================
# Script: Descargar Videos de YouTube/Rumble con Calidad Variable
# Descripción:
#     - Permite seleccionar la calidad de descarga con el parámetro DOWNLOAD_PRESET.
#
# Requisitos:
#     - Python, yt-dlp (actualizado), FFmpeg
#     - Paquete 'browser-cookie3' instalado.
#     - Node.js o Deno (Runtime JS) para desencriptar firmas.
# ============================================================

# ----------------- ⚙️ CONFIGURACIÓN DE DESCARGA -----------------
# 1: Máxima Calidad Disponible (Formato original, sin forzar resolución ni códec)
# 2: 1080p MP4 (Fuerza 1080p, Códec H.264, Salida MP4)
# 3: 720p MP4 (Fuerza 720p, Códec H.264, Salida MP4)
DOWNLOAD_PRESET = 1 
# -------------------------------------------------------------

# --- Definición de Preajustes ---
# 'format_string': El filtro -f de yt-dlp
# 'output_format': El formato de fusión (--merge-output-format)
PRESETS = {
    1: {
        'format_string': 'bestvideo+bestaudio/best', # Mejor video y audio, o el mejor disponible (formato original)
        'output_format': 'mkv', # mkv es más flexible para la máxima calidad
        'description': 'Máxima Calidad Disponible (Auto)'
    },
    2: {
        # Mejor video con altura 1080 y códec que inicie con 'avc' (H.264), más el mejor audio
        'format_string': 'bestvideo[height=1080][vcodec^=avc]+bestaudio/best',
        'output_format': 'mp4',
        'description': '1080p H.264 (MP4)'
    },
    3: {
        # Mejor video con altura 720 y códec que inicie con 'avc' (H.264), más el mejor audio
        'format_string': 'bestvideo[height=720][vcodec^=avc]+bestaudio/best',
        'output_format': 'mp4',
        'description': '720p H.264 (MP4)'
    }
}

# -------------------------------------------------------------

if DOWNLOAD_PRESET not in PRESETS:
    print(f"❌ ERROR: El valor de DOWNLOAD_PRESET ({DOWNLOAD_PRESET}) no es válido.")
    print("Por favor, usa 1, 2 o 3.")
    exit(1)

# Obtener la configuración del preajuste seleccionado
config = PRESETS[DOWNLOAD_PRESET]

print(f"\n🎬 INICIANDO DESCARGA DE VIDEOS (USANDO COOKIES DE FIREFOX)...\n")
print(f"🔧 PREAJUSTE SELECCIONADO: {DOWNLOAD_PRESET} - {config['description']}")

# Obtener el directorio donde está el script, para asegurar la ruta correcta.
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file_name = "videos.txt"
input_file = os.path.join(script_dir, input_file_name)
# El directorio de salida ahora incluye el preajuste para evitar conflictos
output_dir_name = f"videos_descargados_P{DOWNLOAD_PRESET}_{config['output_format']}" 
output_dir = os.path.join(script_dir, output_dir_name)

os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(input_file):
    print(f"❌ ERROR: No se encontró el archivo '{input_file_name}' en la ruta esperada.")
    exit(1)

with open(input_file, "r", encoding="utf-8") as file:
    urls = [line.strip() for line in file if line.strip().startswith("http")]

if not urls:
    print(f"⚠️ ADVERTENCIA: El archivo '{input_file_name}' está vacío o no contiene URLs válidas.")
    exit(0)

print(f"✅ Se encontraron {len(urls)} videos para descargar.")
print(f"💾 Los videos se guardarán en: {output_dir}\n")

# --- PROCESAMIENTO DE DESCARGA ---
for i, url in enumerate(urls):
    # Define el navegador para extraer las cookies
    browser_name = 'firefox'
    
    # El comando de yt-dlp
    command = [
        'yt-dlp',
        
        # ** AUTENTICACIÓN: Usa las cookies de Firefox **
        '--cookies-from-browser', browser_name,
        
        # ** PRECAUCIÓN: Añadir Referer (ayuda contra ciertos bloqueos) **
        '--referer', url, 
        
        # *** CONFIGURACIÓN DE FORMATO USANDO EL PREAJUSTE ***
        '-f', config['format_string'],
        
        # *** FORMATO FINAL DE FUSIÓN ***
        '--merge-output-format', config['output_format'],
        
        # Define la ruta y nombre de salida
        '-o', os.path.join(output_dir, '%(title)s.%(ext)s'),
        url
    ]

    print(f"\n--- ⬇️ PROCESANDO VIDEO {i+1} de {len(urls)} ---")
    print(f"🔗 URL: {url}")
    print(f"🍪 Usando cookies de: {browser_name}")
    print(f"🎥 Formato/Calidad: {config['description']}")
    
    # Ejecutar yt-dlp
    try:
        subprocess.run(command, check=True, text=True, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR al descargar la URL {url}. Detalles: {e}")
    except FileNotFoundError:
        print("❌ ERROR: 'yt-dlp' no se encontró. Asegúrate de haberlo instalado y de que FFmpeg esté en tu PATH.")
        break

print("\n✅ TODAS LAS DESCARGAS HAN FINALIZADO CORRECTAMENTE (o se reportaron los errores).\n")