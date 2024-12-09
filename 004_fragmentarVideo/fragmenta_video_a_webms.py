"""
Script para dividir un archivo de video en fragmentos más pequeños.

Descripción:
Este script utiliza FFmpeg para dividir un archivo de video en fragmentos con una duración específica 
y un tamaño máximo por fragmento. Está diseñado para garantizar que cada fragmento respete un límite 
de tamaño ajustando dinámicamente el bitrate del video y del audio.

Características:
- Divide el video en fragmentos de una duración configurable (por defecto 20 segundos).
- Garantiza un tamaño máximo por fragmento (por defecto 3.5 MB).
- Calcula automáticamente los bitrates de video y audio para cumplir con el límite de tamaño.
- Utiliza codecs configurables para video y audio (por defecto libvpx-vp9 y libvorbis).
- Genera los fragmentos en un directorio llamado "output_parts" en la misma ubicación que el archivo de entrada.

Requisitos:
- FFmpeg instalado y disponible en el PATH.
- Archivo de video válido.

Configuración:
Modifique las variables en la sección "Configuración" para ajustar los parámetros de entrada, 
duración, tamaño máximo y códecs.
"""

import os
import subprocess
import math
import time

# ===========================
# Configuración
# ===========================
input_file = "D:\\03 coding\\Python random\\test.mkv"  # Ruta del archivo de entrada
duration = 20  # Duración de cada fragmento en segundos
max_size_mb = 3.5  # Tamaño máximo por fragmento en MB
codec_video = "libvpx-vp9"  # Códec de video
codec_audio = "libvorbis"  # Códec de audio

# ===========================
# Verificar si FFmpeg está disponible
# ===========================
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print("FFmpeg no está instalado o no está en el PATH. Instálalo para continuar.")
        exit(1)

# ===========================
# Verificar duración del video
# ===========================
def get_video_duration(input_file):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", input_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return math.ceil(float(result.stdout.strip()))
    except Exception as e:
        print(f"Error al obtener la duración del video: {e}")
        exit(1)

# ===========================
# Dividir el video
# ===========================
def split_video(input_file, output_dir, duration, codec_video, bitrate_video, codec_audio, bitrate_audio):
    base_dir = os.path.dirname(input_file)  # Directorio base
    output_dir = os.path.join(base_dir, "output_parts")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isfile(input_file):
        print(f"El archivo de entrada '{input_file}' no existe. Verifica la ruta.")
        exit(1)

    total_duration = get_video_duration(input_file)
    total_parts = math.ceil(total_duration / duration)
    print(f"Duración total del video: {total_duration} segundos")
    print(f"Partes totales estimadas: {total_parts}")

    part = 1
    times = []  # Lista para almacenar tiempos de procesamiento de cada parte

    for start_time in range(0, total_duration, duration):
        output_file = os.path.join(output_dir, f"part_{part:03d}.webm")
        print(f"Procesando fragmento {part}: {output_file} ({start_time}/{total_duration})")

        start_time_part = time.time()  # Tiempo inicial para esta parte

        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c:v", codec_video,
            "-b:v", bitrate_video,
            "-row-mt", "1",
            "-c:a", codec_audio,
            "-ac", "1",
            "-ar", "48000",
            "-b:a", bitrate_audio,
            output_file
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al procesar el fragmento {part}: {e}")
            continue

        # Tiempo final para esta parte
        end_time_part = time.time()
        elapsed_time = end_time_part - start_time_part
        times.append(elapsed_time)

        # Cálculo del tiempo estimado restante
        avg_time = sum(times) / len(times)  # Tiempo promedio por fragmento
        remaining_parts = total_parts - part
        estimated_remaining_time = avg_time * remaining_parts

        # Mostrar información con formato claro
        print("=" * 50)
        print(f"Fragmento {part} completado en {elapsed_time:.2f} segundos.")
        print(f"Tiempo estimado restante: {estimated_remaining_time / 60:.2f} minutos ({remaining_parts} partes restantes)")
        print("=" * 50)

        part += 1

    print(f"Fragmentación completa. Los fragmentos están en la carpeta '{output_dir}'")

# ===========================
# Calcular los bitrates
# ===========================
def calculate_bitrates(max_size_mb, duration):
    max_size_bits = max_size_mb * 8 * 1024 * 1024  # Convertir MB a bits
    total_bitrate_kbps = max_size_bits / duration / 1000  # Convertir a kbps

    # Distribuir el bitrate entre video y audio (90% video, 10% audio)
    video_bitrate_kbps = int(total_bitrate_kbps * 0.85 * 0.9)  # 85% de margen, 90% para video
    audio_bitrate_kbps = int(total_bitrate_kbps * 0.85 * 0.1)  # 85% de margen, 10% para audio

    return video_bitrate_kbps, audio_bitrate_kbps

# ===========================
# Ejecutar
# ===========================
if __name__ == "__main__":
    try:
        check_ffmpeg()
        
        # Calcular bitrates para fragmentos
        video_bitrate_kbps, audio_bitrate_kbps = calculate_bitrates(max_size_mb, duration)
        print(f"Bitrate calculado: Video = {video_bitrate_kbps} kbps, Audio = {audio_bitrate_kbps} kbps")
        
        split_video(
            input_file,
            None,  # La ruta de salida se calculará dentro de split_video
            duration,
            codec_video,
            f"{video_bitrate_kbps}k",
            codec_audio,
            f"{audio_bitrate_kbps}k"
        )
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        exit(1)
