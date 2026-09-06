"""
================================================================================
SCRIPT: Gestor de Descarga por Lotes de YouTube (Anti-Error 403 / SABR)
================================================================================
DESCRIPCIÓN:
    Lee una lista de enlaces desde 'videos.txt' y descarga cada video en la
    máxima calidad posible disponible (video + audio fusionados en formato MP4).
    
    Está especialmente adaptado para evitar las restricciones recientes de 
    YouTube (como los errores 403 Forbidden y el bloqueo del player SABR en 
    transmisiones en vivo o videos largos).

ESTRUCTURA DE ARCHIVOS EN LA CARPETA:
    ├── 001_youtube_downloader_2026.py   <- Este script
    ├── videos.txt                      <- Archivo de entrada (1 URL por línea)
    ├── completados.txt                 <- Historial automático (no tocar)
    └── videos_descargados/             <- Carpeta de salida con los .mp4

CÓMO FUNCIONA CADA PARÁMETRO:
    - player_client=android,web_creator,tv:
        Engaña a los servidores de YouTube simulando peticiones desde clientes 
        móviles y Smart TV, esquivando el bloqueo de peticiones web estándar.
    - -f bestvideo+bestaudio/best:
        Obtiene el stream de video de mayor resolución y el de mejor audio por
        separado para combinarlos con FFmpeg sin pérdida de calidad.
    - --merge-output-format mp4:
        Empaqueta el resultado final en un contenedor compatible (.mp4).
    - --download-archive:
        Registra el ID de cada video terminado. Si cancelas el script o añades 
        nuevos links a 'videos.txt', omite al instante los ya descargados.
    - --retries 10 / --fragment-retries 10:
        Reintenta automáticamente fragmentos cortados por inestabilidad de red.
    - --ignore-errors:
        Si una URL es inválida, privada o eliminada, la salta y continúa con el
        resto de la cola sin detener la ejecución.

REQUISITOS DEL SISTEMA:
    1. Python 3.10+
    2. yt-dlp actualizado:  python -m pip install --upgrade yt-dlp
    3. FFmpeg instalado y agregado al PATH de Windows.
================================================================================
"""

import os
import shutil
import subprocess
import sys

# ============================================================
# CONFIGURACIÓN DE RUTAS Y CARPETAS
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(SCRIPT_DIR, "videos.txt")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "videos_descargados")
ARCHIVE_FILE = os.path.join(SCRIPT_DIR, "completados.txt")

# ============================================================
# VALIDACIONES INICIALES
# ============================================================
print("\n🎬 INICIANDO GESTOR DE DESCARGAS DE YOUTUBE...")

# 1. Crear carpeta destino si aún no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Comprobar que existe el archivo de enlaces
if not os.path.exists(INPUT_FILE):
    print("\n❌ ERROR: No se encontró el archivo de URLs:")
    print(f"   {INPUT_FILE}")
    print("👉 Crea un archivo llamado 'videos.txt' en esa misma carpeta con los enlaces.")
    sys.exit(1)

# 3. Comprobar si hay enlaces válidos dentro del archivo
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip().startswith("http")]

if not urls:
    print("\n⚠️ AVISO: El archivo 'videos.txt' está vacío o no contiene enlaces válidos (que empiecen por http).")
    sys.exit(0)

# ============================================================
# DEFINICIÓN DEL COMANDO (CONFIGURACIÓN OPTIMIZADA)
# ============================================================
comando = [
    "yt-dlp",
    "-a", INPUT_FILE,
    "--extractor-args", "youtube:player_client=android,web_creator,tv",
    "-f", "bestvideo+bestaudio/best",
    "--merge-output-format", "mp4",
    "-o", os.path.join(OUTPUT_DIR, "%(title)s [%(id)s].%(ext)s"),
    "--download-archive", ARCHIVE_FILE,
    "--retries", "10",
    "--fragment-retries", "10",
    "--ignore-errors",
    "--no-mtime"
]

# ============================================================
# EJECUCIÓN DEL PROCESO
# ============================================================
print(f"📋 Enlaces detectados : {len(urls)}")
print(f"📁 Carpeta de destino : {OUTPUT_DIR}")
print(f"📄 Archivo de enlaces : {INPUT_FILE}")
print(f"📝 Registro de avance : {ARCHIVE_FILE}\n")
print("Descargando videos...\n" + "-" * 60)

try:
    resultado = subprocess.run(comando, check=False)

    print("-" * 60)
    if resultado.returncode == 0:
        print("\n✅ TODAS LAS DESCARGAS COMPLETADAS CON ÉXITO.")
        print(f"📁 Revisa tus videos en: {OUTPUT_DIR}\n")
    else:
        print(f"\n⚠️ El proceso terminó con advertencias (algunos videos no se pudieron bajar). Código: {resultado.returncode}\n")

except KeyboardInterrupt:
    print("\n\n⏹️ Descarga pausada por el usuario.")
    print("💡 Si vuelves a correr el script continuará desde donde se quedó.")
    sys.exit(0)

except FileNotFoundError:
    print("\n❌ ERROR: El sistema no encuentra 'yt-dlp' en el PATH.")
    print("👉 Asegúrate de tenerlo instalado y accesible en tu entorno.")
    sys.exit(1)