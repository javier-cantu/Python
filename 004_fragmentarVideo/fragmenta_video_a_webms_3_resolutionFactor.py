import os
import subprocess
import math
import time

# ===========================
# Configuración
# ===========================
input_file = "D:\\03 coding\\Python random\\jews_ritual_murder.mp4"  # Ruta del archivo de entrada
max_size_mb = 3.5  # Tamaño máximo por fragmento en MB
resolution_scale = 0.75  # Escala de resolución (ejemplo: 0.75 para reducir a 75% de la original)
codec_video = "libvpx-vp9"  # Códec de video
codec_audio = "libvorbis"  # Códec de audio
crf_value = 30  # Factor de tasa constante (CRF)

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
# Verificar bitrate total del video
# ===========================
def get_total_bitrate(input_file):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", input_file, "-show_entries", "format=bit_rate", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return int(result.stdout.strip())  # Bitrate total en bits/seg
    except Exception as e:
        print(f"Error al obtener el bitrate total del video: {e}")
        exit(1)

# ===========================
# Obtener la resolución original del video
# ===========================
def get_video_resolution(input_file):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", input_file, "-show_entries", "stream=width,height", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        width, height = map(int, result.stdout.strip().split(","))
        return width, height
    except Exception as e:
        print(f"Error al obtener la resolución del video: {e}")
        exit(1)

# ===========================
# Dividir el video
# ===========================
def split_video(input_file, output_dir, max_duration, codec_video, bitrate_video, codec_audio, bitrate_audio, crf_value, scale_filter):
    base_dir = os.path.dirname(input_file)  # Directorio base
    output_dir = os.path.join(base_dir, "output_parts")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isfile(input_file):
        print(f"El archivo de entrada '{input_file}' no existe. Verifica la ruta.")
        exit(1)

    # Obtener el nombre base del archivo de entrada (sin extensión)
    file_base_name = os.path.splitext(os.path.basename(input_file))[0]

    total_duration = get_video_duration(input_file)
    print(f"Duración total del video: {total_duration} segundos")

    part = 1
    times = []  # Lista para almacenar tiempos de procesamiento de cada parte
    start_time = 0  # Tiempo inicial para el fragmento

    while start_time < total_duration:
        # Duración máxima dinámica
        max_duration = calculate_max_duration(max_size_mb, total_bitrate)
        end_time = min(start_time + max_duration, total_duration)

        # Generar el nombre del archivo de salida
        output_file = os.path.join(output_dir, f"{file_base_name}_{part:03d}.webm")
        print(f"Procesando fragmento {part}: {output_file} ({start_time}/{total_duration})")

        start_time_part = time.time()  # Tiempo inicial para esta parte

        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-ss", str(start_time),
            "-to", str(end_time),
            "-vf", scale_filter,
            "-c:v", codec_video,
            "-b:v", bitrate_video,
            "-row-mt", "1",
            "-crf", str(crf_value),
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

        end_time_part = time.time()
        elapsed_time = end_time_part - start_time_part
        times.append(elapsed_time)

        print("=" * 50)
        print(f"Fragmento {part} completado en {elapsed_time:.2f} segundos.")
        print("=" * 50)

        start_time = end_time
        part += 1

    print(f"Fragmentación completa. Los fragmentos están en la carpeta '{output_dir}'")

# ===========================
# Calcular la duración máxima
# ===========================
def calculate_max_duration(max_size_mb, total_bitrate):
    max_size_bits = max_size_mb * 8 * 1024 * 1024  # Convertir MB a bits
    max_duration = max_size_bits / total_bitrate  # Duración máxima en segundos
    return int(max_duration)

# ===========================
# Obtener la duración total del video
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
# Ejecutar
# ===========================
if __name__ == "__main__":
    try:
        check_ffmpeg()

        # Obtener el bitrate total del video
        total_bitrate = get_total_bitrate(input_file)  # En bits/seg
        print(f"Bitrate total del video: {total_bitrate / 1000:.2f} kbps")

        # Calcular bitrates para fragmentos
        video_bitrate_kbps = int(total_bitrate * 0.8 / 1000)  # 80% para video
        audio_bitrate_kbps = int(total_bitrate * 0.2 / 1000)  # 20% para audio

        # Obtener resolución original y aplicar escala
        original_width, original_height = get_video_resolution(input_file)
        scaled_width = int(original_width * resolution_scale)
        scaled_height = int(original_height * resolution_scale)
        scale_filter = f"scale={scaled_width}:{scaled_height}"

        split_video(
            input_file,
            None,  # La ruta de salida se calculará dentro de split_video
            None,  # La duración será dinámica
            codec_video,
            f"{video_bitrate_kbps}k",
            codec_audio,
            f"{audio_bitrate_kbps}k",
            crf_value,
            scale_filter
        )
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        exit(1)
