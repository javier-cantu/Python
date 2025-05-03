import subprocess
import re
import os

# ========================== HEADER ==========================
#  Script: Descargar y Optimizar Streams con FFmpeg
#  Descripción:
#      Este script automatiza la descarga de videos desde una lista de URLs
#      contenida en un archivo de texto ('videos.txt'). Luego, los convierte
#      y optimiza usando el códec H.264 (libx264) a una resolución de 1280x720.
#
#  Funcionalidades:
#      - Lee un archivo de texto ('videos.txt') con nombres y URLs de los videos.
#      - Descarga cada video usando FFmpeg.
#      - Optimiza el video reduciendo su peso sin perder demasiada calidad.
#      - Guarda los archivos en el mismo directorio donde está el script.
#
#  Configuración FFmpeg:
#      - Video:
#          - Resolución: 1280x720 (reescala si es necesario)
#          - Códec: H.264 (libx264)
#          - CRF: 23 (balance entre calidad y peso)
#          - Preset: slow (compresión eficiente)
#          - Bitrate: 1200 kbps (máx. 1400 kbps)
#          - Frame rate: 23.98 FPS
#      - Audio:
#          - Códec: AAC
#          - Bitrate: 96 kbps
#          - Canales: 2 (stereo)
#          - Frecuencia: 44.1 kHz
#
#  Uso:
#      1. Coloca este script en la misma carpeta donde tienes 'videos.txt'.
#      2. Asegúrate de que FFmpeg esté instalado y en el PATH del sistema.
#      3. Ejecuta el script con Python:
#         > python descargar_streams.py
#      4. Los videos descargados y optimizados se guardarán en la misma carpeta.
#
# ============================================================

print("\n🎬 INICIANDO DESCARGA Y OPTIMIZACIÓN DE VIDEOS...\n")

# Obtener el directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo con los títulos y URLs (debe estar en la misma carpeta)
input_file = os.path.join(script_dir, "videos.txt")

# Función para transformar el título en un formato compatible
def format_filename(title):
    """
    Convierte un título de episodio en un nombre de archivo válido.
    
    Formato de entrada esperado:
        "Episodio 3 de la temporada 1: La odisea de Homero"
    
    Salida esperada:
        "Los_Simpsons_T01E03_La_odisea_de_Homero.mp4"
    """
    match = re.search(r"Episodio (\d+) de la temporada (\d+): (.+)", title, re.IGNORECASE)
    if match:
        ep_num = int(match.group(1))  # Número de episodio
        season_num = int(match.group(2))  # Número de temporada
        episode_name = match.group(3)  # Nombre del episodio
        
        # Formatear con prefijo estándar
        formatted_title = f"Los_Simpsons_T{season_num:02}E{ep_num:02}_{episode_name}"
        
        # Reemplazar espacios con "_", quitar caracteres especiales
        formatted_title = re.sub(r"[^a-zA-Z0-9_]", "", formatted_title.replace(" ", "_"))
        
        return formatted_title
    else:
        return None  # Si el formato no coincide, ignorar la línea

# Verificar si el archivo videos.txt existe
if not os.path.exists(input_file):
    print(f"❌ ERROR: No se encontró '{input_file}'. Asegúrate de que el archivo existe en la misma carpeta que este script.")
    exit(1)

# Leer el archivo de texto
with open(input_file, "r", encoding="utf-8") as file:
    lines = [line.strip() for line in file if line.strip()]  # Remover espacios y líneas vacías

# Procesar cada título y URL en pares consecutivos
for i in range(0, len(lines), 2):
    if i + 1 < len(lines):  # Verificar que hay un URL después del título
        title = lines[i]
        url = lines[i + 1]
        formatted_filename = format_filename(title)

        if formatted_filename:
            # Guardar el archivo en el mismo directorio del script
            output_filename = os.path.join(script_dir, f"{formatted_filename}.mp4")

            # Construir el comando FFmpeg con optimización
            command = f'ffmpeg -i "{url}" -vf "scale=1280:720" -crf 23 -preset slow -c:v libx264 -b:v 1200k -maxrate 1400k -bufsize 2800k -r 23.98 -c:a aac -b:a 96k -ac 2 -ar 44100 "{output_filename}"'

            print(f"\n⬇️ Descargando y optimizando: {title}")
            print(f"📁 Guardando en: {output_filename}")
            
            # Ejecutar FFmpeg
            subprocess.run(command, shell=True)

print("\n✅ TODAS LAS DESCARGAS Y OPTIMIZACIONES HAN FINALIZADO CORRECTAMENTE.\n")
