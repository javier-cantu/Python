import subprocess
import os
import re

# ========================== HEADER ==========================
#  Script: Unir Streams de Video y Audio con FFmpeg
#  Descripción:
#      Busca archivos de video/audio (.mp4/.webm con sufijos .fXXX)
#      dentro del subdirectorio 'videos_descargados' y los fusiona.
#
#  Uso:
#      1. Coloca este script en la misma carpeta que 'descargar_yt.py'.
#      2. Asegúrate de que FFmpeg esté en el PATH.
#      3. Ejecuta el script: python unir_videos.py
# ============================================================

print("\n🎬 INICIANDO UNIÓN DE ARCHIVOS DE VIDEO Y AUDIO...\n")

# Obtener el directorio donde está este script
script_dir = os.path.dirname(os.path.abspath(__file__))

# 🔑 CARPETA DE ENTRADA/SALIDA: Ahora siempre apunta al subdirectorio
target_dir_name = "videos_descargados"
target_dir = os.path.join(script_dir, target_dir_name)

# Verificar que la carpeta de descargas existe
if not os.path.isdir(target_dir):
    print(f"❌ ERROR: No se encontró el subdirectorio '{target_dir_name}'.")
    print("Asegúrate de que el script de descarga se haya ejecutado correctamente.")
    exit(1)

# Diccionario para almacenar los pares de archivos:
# Clave: Prefijo limpio
# Valor: [Ruta_Video, Ruta_Audio]
file_pairs = {}

# Patrón regex para identificar y separar el sufijo (.fXXX)
suffix_pattern = re.compile(r'\.f\d{2,}\.(mp4|webm)$')

# ----------------------------------------------------------------
# 1. ENCONTRAR Y AGRUPAR LOS PARES DE ARCHIVOS (dentro de target_dir)
# ----------------------------------------------------------------

print(f"🔎 Buscando archivos dentro de: {target_dir}")

for filename in os.listdir(target_dir):
    
    # Si el archivo tiene el sufijo .fXXX.mp4 o .fXXX.webm
    match = suffix_pattern.search(filename)
    if match:
        extension = match.group(1)
        # El prefijo es el nombre del archivo sin el sufijo .fXXX.ext
        clean_prefix = suffix_pattern.sub('', filename) 

        # Crear la ruta completa del archivo dentro del directorio target
        full_path = os.path.join(target_dir, filename)

        if clean_prefix not in file_pairs:
            file_pairs[clean_prefix] = [None, None] # [Video, Audio]

        if extension == 'mp4': # Asumimos que el .mp4 es el video
            file_pairs[clean_prefix][0] = full_path
        elif extension == 'webm': # Asumimos que el .webm es el audio
            file_pairs[clean_prefix][1] = full_path

# ----------------------------------------------------------------
# 2. PROCESAR Y UNIR CADA PAR
# ----------------------------------------------------------------

total_pairs = len(file_pairs)
print(f"✅ Encontrados {total_pairs} pares de video/audio listos para unir.")

if total_pairs == 0:
    print("⚠️ ADVERTENCIA: No se encontraron pares de archivos .mp4/.webm con sufijos .fXXX para unir.")
    exit(0)

for i, (prefix, paths) in enumerate(file_pairs.items()):
    video_path, audio_path = paths

    # Nombre del archivo de salida limpio (sin sufijo .fXXX)
    output_filename = f"{prefix}.mp4"
    # 🔑 El archivo de salida se guarda DENTRO de la carpeta videos_descargados
    output_path = os.path.join(target_dir, output_filename)

    # Verificar que tenemos ambos archivos
    if video_path and audio_path:
        print(f"\n--- 🔄 PROCESANDO PAR {i+1} de {total_pairs} ---")
        print(f"📁 Uniendo: '{prefix}'")
        
        # Comando FFmpeg para unir video y audio
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            '-map', '0:v',
            '-map', '1:a',
            output_path
        ]
        
        # Ejecutar FFmpeg
        try:
            # Silenciamos la salida de FFmpeg para que sea más limpio
            subprocess.run(command, check=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"✅ UNIÓN EXITOSA: Archivo guardado como '{output_filename}' en '{target_dir_name}'")
            
            # Opcional: ELIMINAR LOS ARCHIVOS ORIGINALES DESPUÉS DE UNIR
            # print("🗑️ Eliminando archivos temporales...")
            # os.remove(video_path)
            # os.remove(audio_path)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR al ejecutar FFmpeg para '{prefix}': {e}")
            print("Asegúrate de que FFmpeg está instalado correctamente.")
        except FileNotFoundError:
            print("❌ ERROR: FFmpeg no se encontró. Asegúrate de que está instalado y en el PATH del sistema.")
            break
    else:
        print(f"\n⚠️ ADVERTENCIA: El par '{prefix}' está incompleto. Faltan archivos de video o audio. Saltando...")


print("\n✅ PROCESO DE UNIÓN DE ARCHIVOS FINALIZADO.\n")