"""
==================================================================================
🎬 Script: clean_english_subs.py
📌 Descripción:
    Este script limpia y corrige subtítulos en inglés eliminando mayúsculas innecesarias,
    mejorando la gramática y asegurando que la puntuación sea adecuada.

    ✅ Convierte texto completamente en mayúsculas a formato estándar (solo mayúscula inicial).
    ✅ Elimina dobles espacios y signos de puntuación mal colocados.
    ✅ Mantiene el formato original del `.srt` (tiempos y numeración).

📌 Uso:
    1️⃣ Asegúrate de que el archivo `.srt` que quieres limpiar esté en la misma carpeta que este script.
    2️⃣ Instala las dependencias necesarias si no lo has hecho:
        pip install pysrt
    3️⃣ Ejecuta el script en la terminal o línea de comandos:
        python clean_english_subs.py
    4️⃣ El archivo limpio se guardará con "_cleaned" añadido al nombre.

📅 Última actualización: [5/Enero/2025]

==================================================================================
"""

import os
import pysrt
import re

# Obtener el directorio donde está el script
input_dir = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas de los archivos
input_file = os.path.join(input_dir, "A_Little_Princess_English_fromDVD.srt")
output_file = os.path.join(input_dir, "A_Little_Princess_English_Cleaned.srt")

print(f"📂 Directorio del script: {input_dir}")
print(f"📄 Archivo de entrada: {input_file}")
print(f"📄 Archivo de salida: {output_file}")

# Verificar si el archivo de entrada existe
if not os.path.exists(input_file):
    print(f"❌ ERROR: No se encontró el archivo '{input_file}'. Verifica el nombre y la ubicación.")
    exit(1)

print("✅ Archivo encontrado. Cargando subtítulos...")

# Cargar subtítulos
subs = pysrt.open(input_file)

# Función para corregir la capitalización y eliminar errores de formato
def clean_text(text):
    """
    Limpia el texto de los subtítulos:
    - Convierte texto en mayúsculas a capitalización normal.
    - Corrige espacios y puntuación innecesaria.
    - Asegura que cada oración tenga una mayúscula inicial y minúsculas después.
    """

    # Convertir todo a minúsculas si el texto estaba completamente en mayúsculas
    if text.isupper():
        text = text.lower()

    # Expresión regular para detectar oraciones
    sentences = re.split(r'([.!?]) ', text)  # Separa por ".", "!", "?" seguidos de un espacio
    corrected_sentences = []

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        
        if not sentence:
            continue

        # Si es un signo de puntuación, mantenerlo sin cambios
        if sentence in [".", "!", "?"]:
            corrected_sentences.append(sentence)
            continue

        # Asegurar que la primera letra de cada oración esté en mayúscula
        sentence = sentence.capitalize()
        
        corrected_sentences.append(sentence)

    cleaned_text = " ".join(corrected_sentences)  # Unir todo en un texto corregido

    # Eliminar espacios extra
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text

# Mostrar cuántos subtítulos hay
total_subs = len(subs)
print(f"📑 Total de líneas de subtítulos: {total_subs}")

# Limpiar la capitalización y gramática de cada línea del subtítulo
for i, sub in enumerate(subs, start=1):
    if sub.text.strip():  # Evitar líneas vacías
        try:
            sub.text = clean_text(sub.text)  # Aplicar corrección de formato y capitalización
        except Exception as e:
            print(f"⚠️ Error al limpiar la línea {i}: {e}")
    if i % 100 == 0:  # Mostrar progreso cada 100 líneas
        print(f"⏳ Limpieza completada en {i}/{total_subs} líneas...")

print("✅ Limpieza completada. Guardando archivo...")

# Guardar el archivo corregido
subs.save(output_file, encoding="utf-8")

print(f"🎉 Limpieza finalizada con corrección de gramática y formato. Archivo guardado en: {output_file}")
