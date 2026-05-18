import os
import random
import numpy as np
from pedalboard.io import AudioFile

# ================= CONFIGURACIÓN =================
VOLUMEN_AFIRMACIONES = 0.8  # 0.1 a 0.5 (subliminal) | 0.8+ (audible)
VOLUMEN_BASE = 1.0 # 1 volumen total       
ARCHIVO_BASE = "Gentle Ocean Waves 20 Minutes Meditation Relaxation Sleep Better Reduce Stress.mp3"
CARPETA_AUDIOS = "./"
ARCHIVO_SALIDA = "Subliminal_Final.wav"
# =================================================

def crear_subliminal_wav():
    if not os.path.exists(ARCHIVO_BASE):
        print(f"Error: No se encuentra {ARCHIVO_BASE}")
        return

    # 1. Cargar base
    print("Leyendo audio base...")
    with AudioFile(ARCHIVO_BASE) as f:
        samplerate = f.samplerate
        base_audio = f.read(f.frames) * VOLUMEN_BASE
    
    num_canales = base_audio.shape[0]
    duracion_base_samples = base_audio.shape[1]

    # 2. Cargar afirmaciones (001 a 033)
    afirmaciones = []
    print("Cargando afirmaciones...")
    for i in range(1, 34):
        ruta = os.path.join(CARPETA_AUDIOS, f"{i:03d}.mp3")
        if os.path.exists(ruta):
            with AudioFile(ruta) as f:
                audio = f.read(f.frames)
                afirmaciones.append(audio * VOLUMEN_AFIRMACIONES)

    if not afirmaciones:
        print("No se encontraron archivos de afirmaciones.")
        return

    # 3. Distribución por bloques para evitar empalmes
    samples_por_bloque = duracion_base_samples // len(afirmaciones)
    
    print(f"Mezclando {len(afirmaciones)} audios en la línea de tiempo...")

    for i, clip in enumerate(afirmaciones):
        duracion_clip = clip.shape[1]
        inicio_bloque = i * samples_por_bloque
        
        # Dejamos un margen de 1 segundo para estar seguros
        espacio_libre = samples_por_bloque - duracion_clip - samplerate
        
        if espacio_libre > 0:
            offset = random.randint(0, espacio_libre)
            start_sample = inicio_bloque + offset
        else:
            start_sample = inicio_bloque
            
        end_sample = start_sample + duracion_clip

        # Evitar salirnos del final de la base
        if end_sample > duracion_base_samples:
            end_sample = duracion_base_samples
            clip = clip[:, :end_sample - start_sample]

        # Aplicar overlay
        if clip.shape[0] < num_canales:
            for c in range(num_canales):
                base_audio[c, start_sample:end_sample] += clip[0]
        else:
            base_audio[:, start_sample:end_sample] += clip[:, :]

    # 4. Normalizar para evitar distorsión
    max_peak = np.max(np.abs(base_audio))
    if max_peak > 1.0:
        base_audio /= max_peak

    # 5. Guardar en WAV (Sin complicaciones de bitrate o codecs)
    print(f"Exportando a {ARCHIVO_SALIDA}...")
    with AudioFile(ARCHIVO_SALIDA, 'w', samplerate, num_canales) as f:
        f.write(base_audio)
    
    print("¡Listo! El archivo .wav se generó sin errores.")

if __name__ == "__main__":
    crear_subliminal_wav()