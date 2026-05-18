# 🎧 Generador de Audios Subliminales

Este script en Python automatiza la creación de pistas de audio subliminal, mezclando una base de ruido ambiental con afirmaciones distribuidas matemáticamente para evitar que se empalmen.

## 🛠️ Requisitos Técnicos

El script es compatible con **Python 3.13** y utiliza `pedalboard` para el procesamiento de audio de alto rendimiento.

Para instalar las librerías necesarias, ejecuta:
pip install pedalboard numpy

## 📂 Estructura del Proyecto

Para que el script funcione sin cambios, organiza tus archivos así dentro de la misma carpeta:

* **Audio Base:** El archivo de fondo (ej: `Base Audio - 20 Minutes...mp3`).
* **Afirmaciones:** Archivos numerados del `001.mp3` al `033.mp3`.
* **Script:** El archivo `.py` que contiene el código de mezcla.

## ⚙️ Configuración (Variables al inicio del Script)

| Variable | Función | Valor Recomendado |
| :--- | :--- | :--- |
| `VOLUMEN_AFIRMACIONES` | Nivel de las voces. | `0.1` a `0.3` (Subliminal) |
| `VOLUMEN_BASE` | Nivel del ruido de fondo. | `1.0` |
| `ARCHIVO_SALIDA` | Nombre del archivo final. | `Subliminal_Final.wav` |

## 🧠 Lógica de Funcionamiento

1.  **Distribución por Bloques:** El script calcula la duración total y la divide entre el número de afirmaciones. Esto crea "ventanas" de tiempo individuales, lo que garantiza que **nunca se empalmen dos audios**.
2.  **Offset Aleatorio:** Dentro de cada ventana, la afirmación se posiciona al azar para evitar un ritmo monótono.
3.  **Normalización de Audio:** Analiza el resultado final y ajusta el volumen para evitar el *clipping* (distorsión por exceso de volumen) si las frecuencias se suman demasiado.
4.  **Formato WAV:** Exporta en alta fidelidad sin comprimir para evitar errores de codecs en Python 3.13.

## 📝 Ejecución

Corre el script desde tu terminal o consola de VS Code:

python subliminal_affirmations_join.py