import subprocess
import os

# ========================== HEADER ==========================
# Script: Descargar Videos de YouTube/Rumble en 720p (MP4 Compatible)
# Descripción:
#     *** FIX: Sintaxis de filtro corregida (vcodec^=avc) ***
#
# Requisitos:
#     - Python, yt-dlp (actualizado), FFmpeg
#     - Paquete 'browser-cookie3' instalado.
#     - Node.js o Deno (Runtime JS) para desencriptar firmas.
# ============================================================

print("\n🎬 INICIANDO DESCARGA DE VIDEOS (USANDO COOKIES DE FIREFOX)...\n")

# Obtener el directorio donde está el script, para asegurar la ruta correcta.
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file_name = "videos.txt"
input_file = os.path.join(script_dir, input_file_name)
output_dir_name = "videos_descargados_720p_mp4" 
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
        
        # *** CONFIGURACIÓN PARA FORZAR 720P (H.264) Y MEJOR AUDIO ***
        # FIX: Se reemplazó el filtro inválido [vcodec~*avc] por el correcto [vcodec^=avc].
        # Esto busca el mejor video con altura EXACTA 720 y cuyo códec empiece por 'avc' (H.264).
        '-f', 'bestvideo[height=720][vcodec^=avc]+bestaudio/best',
        
        # *** FORMATO FINAL MP4 ***
        '--merge-output-format', 'mp4',
        
        # Define la ruta y nombre de salida
        '-o', os.path.join(output_dir, '%(title)s.%(ext)s'),
        url
    ]

    print(f"\n--- ⬇️ PROCESANDO VIDEO {i+1} de {len(urls)} ---")
    print(f"🔗 URL: {url}")
    print(f"🍪 Usando cookies de: {browser_name}")
    print(f"🎥 Formato de salida: MP4 (FORZANDO 720p H.264)")
    
    # Ejecutar yt-dlp
    try:
        subprocess.run(command, check=True, text=True, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR al descargar la URL {url}. Detalles: {e}")
    except FileNotFoundError:
        print("❌ ERROR: 'yt-dlp' no se encontró. Asegúrate de haberlo instalado y de que FFmpeg esté en tu PATH.")
        break

print("\n✅ TODAS LAS DESCARGAS HAN FINALIZADO CORRECTAMENTE (o se reportaron los errores).\n")