import subprocess
import os

# ========================== HEADER ==========================
#  Script: Descargar Videos de YouTube en Máxima Calidad con yt-dlp
#  Descripción:
#      Este script lee una lista de URLs desde 'videos.txt' (una URL por línea)
#      y descarga cada video de YouTube en la mejor calidad de video y audio
#      disponible, usando el programa yt-dlp.
#
#  Configuración yt-dlp:
#      - Calidad: Mejor stream de video + Mejor stream de audio.
#      - Formato: Los streams se combinan en un archivo MP4 final.
#      - Nombre de archivo: Título del video original.mp4
#
#  Requisitos:
#      - Python (con el paquete yt-dlp instalado)
#      - yt-dlp y FFmpeg deben estar en el PATH del sistema.
# ============================================================

print("\n🎬 INICIANDO DESCARGA DE VIDEOS DE YOUTUBE EN ALTA CALIDAD...\n")

# Obtener el directorio donde está el script, para asegurar la ruta correcta.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo con las URLs
input_file_name = "videos.txt"

# 🔑 CORRECCIÓN DE RUTA: Obtener la ruta completa (absoluta) de videos.txt
input_file = os.path.join(script_dir, input_file_name)

# Directorio donde se guardarán los videos descargados (también relativo al script)
output_dir_name = "videos_descargados"
output_dir = os.path.join(script_dir, output_dir_name)

# Crear el directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Verificar si el archivo de URLs existe USANDO LA RUTA COMPLETA
if not os.path.exists(input_file):
    print(f"❌ ERROR: No se encontró el archivo '{input_file_name}' en la ruta esperada:")
    print(f"Ruta completa verificada: {input_file}")
    print("Asegúrate de que el archivo existe en la misma carpeta que este script.")
    exit(1)

# Leer el archivo de texto
with open(input_file, "r", encoding="utf-8") as file:
    # Filtra y limpia las líneas para obtener solo URLs no vacías
    urls = [line.strip() for line in file if line.strip().startswith("http")]

if not urls:
    print(f"⚠️ ADVERTENCIA: El archivo '{input_file_name}' está vacío o no contiene URLs válidas.")
    exit(0)

print(f"✅ Se encontraron {len(urls)} videos para descargar.")

# Procesar cada URL
for i, url in enumerate(urls):
    # El comando de yt-dlp
    command = [
        'yt-dlp',
        '-f', 'bestvideo+bestaudio/best',
        '--merge-output-format', 'mp4',
        # El destino del archivo de salida ahora usa la ruta absoluta de output_dir
        '-o', os.path.join(output_dir, '%(title)s.%(ext)s'),
        url
    ]

    print(f"\n--- ⬇️ PROCESANDO VIDEO {i+1} de {len(urls)} ---")
    print(f"🔗 URL: {url}")
    print(f"📁 Destino: {output_dir}")
    
    # Ejecutar yt-dlp
    try:
        # Se ha quitado 'shell=True' para mayor seguridad y compatibilidad,
        # usando la lista de comandos como se recomienda para subprocess.
        subprocess.run(command, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR al descargar la URL {url}: {e}")
    except FileNotFoundError:
        print("❌ ERROR: 'yt-dlp' no se encontró. Asegúrate de haberlo instalado y de que FFmpeg esté en tu PATH.")
        break # Detener la ejecución si el ejecutable principal no está

print("\n✅ TODAS LAS DESCARGAS HAN FINALIZADO CORRECTAMENTE (o se reportaron los errores).\n")