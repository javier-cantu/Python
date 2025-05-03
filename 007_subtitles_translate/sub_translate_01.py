"""
==================================================================================
🎬 Script: traducir_subs.py
📌 Descripción:
    Este script traduce archivos de subtítulos en formato `.srt` del inglés al español.
    Mantiene el formato original de los subtítulos (numeración y tiempos) y corrige
    la gramática en español, incluyendo:

    ✅ Capitalización correcta: solo la primera letra de cada oración en mayúscula.
    ✅ Soporte para signos de interrogación (¿) y exclamación (¡), asegurando que
       la primera letra después de ellos esté en mayúscula.
    ✅ Traducción automatizada con la API de Deep Translator (Google Translate).
    ✅ Muestra el progreso cada 100 líneas para archivos grandes.
    ✅ Guarda el resultado en un nuevo archivo `.srt`.

📌 Uso:
    1️⃣ Asegúrate de que el archivo `.srt` en inglés esté en la misma carpeta que este script.
    2️⃣ Instala las dependencias necesarias si no lo has hecho:
        pip install pysrt deep-translator
    3️⃣ Ejecuta el script en la terminal o línea de comandos:
        python traducir_subs.py
    4️⃣ El archivo traducido se guardará con el mismo nombre, pero con "_Spanish" añadido.

📌 Notas:
    - Si el archivo `.srt` es muy grande, puede tardar algunos minutos en procesarse.
    - En caso de errores en la traducción de alguna línea, el script continuará sin detenerse.
    - Se recomienda revisar el archivo final por posibles ajustes manuales.

🛠 Creado por: [Tu Nombre o Alias]
📅 Última actualización: [Fecha]

==================================================================================
"""

import os
import pysrt
from deep_translator import GoogleTranslator
import re

# Obtener el directorio donde está el script
input_dir = os.path.dirname(os.path.abspath(__file__))

# Definir las rutas de los archivos
input_file = os.path.join(input_dir, "A_Little_Princess_English.srt")
output_file = os.path.join(input_dir, "A_Little_Princess_Spanish.srt")

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

# Inicializar el traductor (Inglés -> Español)
translator = GoogleTranslator(source="en", target="es")

# Función para corregir la capitalización, incluyendo signos de interrogación y exclamación
def fix_capitalization(text):
    """
    Corrige la gramática en español:
    - Capitaliza la primera letra de cada oración.
    - Maneja correctamente los signos ¿ y ¡ asegurando que la primera letra después de ellos esté en mayúscula.
    """
    # Expresión regular para detectar oraciones
    sentences = re.split(r'([.!?¿¡] )', text)
    corrected_sentences = []
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        
        if not sentence:
            continue
        
        # Si es un signo de puntuación, mantenerlo sin cambios
        if sentence in [".", "!", "?", "¿", "¡"]:
            corrected_sentences.append(sentence)
            continue
        
        # Si la oración comienza con ¿ o ¡, aseguramos que la siguiente letra esté en mayúscula
        if sentence.startswith("¿") or sentence.startswith("¡"):
            if len(sentence) > 1:
                sentence = sentence[0] + sentence[1].upper() + sentence[2:]
        
        else:
            # Asegurar que la primera letra de una oración normal esté en mayúscula
            sentence = sentence.capitalize()
        
        corrected_sentences.append(sentence)
    
    return " ".join(corrected_sentences)  # Unir todo en un texto corregido

# Mostrar cuántos subtítulos hay
total_subs = len(subs)
print(f"📑 Total de líneas de subtítulos: {total_subs}")

# Traducir y corregir capitalización en cada línea del subtítulo
for i, sub in enumerate(subs, start=1):
    if sub.text.strip():  # Evitar traducir líneas vacías
        try:
            translated_text = translator.translate(sub.text)
            sub.text = fix_capitalization(translated_text)  # Aplicar corrección de mayúsculas y signos
        except Exception as e:
            print(f"⚠️ Error al traducir la línea {i}: {e}")
    if i % 100 == 0:  # Mostrar progreso cada 100 líneas
        print(f"⏳ Traducidas {i}/{total_subs} líneas...")

print("✅ Traducción completada. Guardando archivo...")

# Guardar el archivo traducido
subs.save(output_file, encoding="utf-8")

print(f"🎉 Traducción finalizada con corrección de gramática y signos de puntuación. Archivo guardado en: {output_file}")