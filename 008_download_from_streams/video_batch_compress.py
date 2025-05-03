# Este ya no es necesario con el nuevo script que descarga y comprime los streams al mismo tiempo 'download_from_stream_ffmpeg_01'

import subprocess
import os

# ========================== HEADER ==========================
#  Script: Comprimir Videos en Carpeta con FFmpeg
#  Descripción: Comprime todos los archivos .mp4 en el directorio actual 
#               a formato H.264 (libx264) optimizado con resolución 1280x720.
#  Autor: [Tu Nombre]
#  Versión: 1.0
#  Uso: Coloca este script en la misma carpeta que los videos y ejecútalo.
# ============================================================

print("\n🎬 INICIANDO COMPRESIÓN DE VIDEOS...\n")

# Obtener el directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde se guardarán los videos comprimidos
output_folder = os.path.join(script_dir, "comprimidos")

# Crear la carpeta si no existe
os.makedirs(output_folder, exist_ok=True)

# Buscar todos los archivos .mp4 en el directorio actual
video_files = [f for f in os.listdir(script_dir) if f.endswith(".mp4")]

if not video_files:
    print("❌ No se encontraron archivos .mp4 en la carpeta.")
    exit(1)

# Procesar cada archivo de video encontrado
for video in video_files:
    input_path = os.path.join(script_dir, video)
    output_filename = os.path.splitext(video)[0] + "_compressed.mp4"
    output_path = os.path.join(output_folder, output_filename)

    # Comando FFmpeg para comprimir el video
    command = f'ffmpeg -i "{input_path}" -vf "scale=1280:720" -crf 23 -preset slow -c:v libx264 -b:v 1200k -maxrate 1400k -bufsize 2800k -r 23.98 -c:a aac -b:a 96k -ac 2 -ar 44100 "{output_path}"'

    print(f"\n🔄 Comprimiendo: {video}")
    print(f"📁 Guardando en: {output_path}")

    # Ejecutar FFmpeg
    subprocess.run(command, shell=True)

print("\n✅ TODA LA COMPRESIÓN HA FINALIZADO CORRECTAMENTE.\n")
