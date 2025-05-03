"""
Script para convertir archivos de video (.flv y .mp4) a MP4 optimizado

Este script busca archivos de video en el directorio donde se ejecuta y los convierte a un formato 
más compatible y optimizado en tamaño, utilizando FFmpeg. 

### Características del script:
- Convierte archivos **.flv** y **.mp4** a **MP4** con el códec **H.264 (libx264)**.
- Optimiza la compresión de video usando **CRF 28** (buena calidad con menor tamaño).
- Reduce la calidad del audio a **AAC 48kbps, mono y 22050 Hz** para ahorrar espacio.
- Reemplaza **espacios** en los nombres de los archivos por **guiones bajos** y normaliza nombres.
- Cambia la nomenclatura de episodios de **"1x01"** a **"T01C01"**.
- Crea una carpeta **"convertidos"** para almacenar los archivos procesados.
- Usa **FFmpeg** para la conversión.

### Requisitos:
- Tener **FFmpeg** instalado y accesible desde la terminal/comando (`ffmpeg` debe estar en el PATH).
- Archivos **.flv** y **.mp4** en el mismo directorio donde se ejecuta el script.

### Salida:
- Se generarán archivos **.mp4** optimizados en la carpeta `convertidos/`, con nombres formateados.

"""

import os
import subprocess
import unicodedata
import re

# Directorio donde está el script (y los archivos de video)
input_dir = os.path.dirname(os.path.abspath(__file__))

# Crear el directorio de salida "convertidos"
output_dir = os.path.join(input_dir, "convertidos")
os.makedirs(output_dir, exist_ok=True)

# Buscar archivos .flv y .mp4 en el directorio actual
video_files = [f for f in os.listdir(input_dir) if f.endswith((".flv", ".mp4"))]

# Parámetros optimizados para menor tamaño sin perder calidad
codec = "libx264"
preset = "veryslow"  # Mejor compresión, más lento
crf = "28"  # Reducir tamaño sin perder demasiada calidad
audio_bitrate = "48k"  # Audio más ligero (baja calidad)
audio_sample_rate = "22050"  # Reducir frecuencia de muestreo
audio_channels = "1"  # Forzar a mono


def normalize_filename(filename):
    """ 
    Convierte el nombre del archivo al formato requerido:
    - Elimina acentos y caracteres especiales.
    - Sustituye espacios por guiones bajos (_).
    - Cambia la nomenclatura "1x01" a "T01C01".
    - Limpia guiones bajos redundantes.
    """
    # Eliminar acentos y caracteres especiales
    filename = unicodedata.normalize("NFKD", filename).encode("ASCII", "ignore").decode("utf-8")

    # Reemplazar espacios por guiones bajos
    filename = filename.replace(" ", "_")

    # Reemplazar 1x01 por T01C01
    filename = re.sub(r"(\d+)x(\d+)", r"T\1C\2", filename)

    # Limpiar guiones innecesarios
    filename = re.sub(r"_-_", "_", filename)  # Si hay "_-_", lo limpia
    filename = re.sub(r"-_", "_", filename)   # Si hay "-_" al inicio, lo limpia
    filename = re.sub(r"_-$", "", filename)   # Si hay "_" al final, lo limpia

    return filename


for video in video_files:
    input_path = os.path.join(input_dir, video)

    # Obtener el nuevo nombre del archivo
    new_filename = normalize_filename(os.path.splitext(video)[0]) + ".mp4"
    output_path = os.path.join(output_dir, new_filename)

    # Comando FFmpeg para conversión optimizada
    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", codec,
        "-preset", preset,
        "-crf", str(crf),
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-ar", audio_sample_rate,
        "-ac", audio_channels,  # Forzar audio a mono
        "-movflags", "+faststart",
        output_path
    ]

    print(f"Convirtiendo {video} a {output_path}...")

    subprocess.run(command, check=True)

print("Conversión completada. Los archivos están en la carpeta 'convertidos'.")
