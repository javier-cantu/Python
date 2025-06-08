Creador de EPUB Personalizado

Este conjunto de scripts te permite generar un EPUB a partir de texto plano y recursos específicos, incluyendo la creación de una portada personalizada y la estructuración del contenido.

Estructura de Carpetas Necesaria

Asegúrate de tener la siguiente estructura de directorios antes de comenzar:
├── fonts/
│   └── roboto-bold-condensed.ttf  (O la fuente que elijas para la portada)
├── Images/
│   └── cover_art.jpg             (Tu imagen de arte para la portada)
│   └── [otras_imagenes_del_libro].jpg
├── Styles/
│   └── Style001.css              (Hoja de estilos para el contenido y centrado de imágenes)
├── raw_wikipedia.txt             (Tu archivo de texto fuente sin procesar)
├── 01_parse_raw.py
└── 02_generate_fragments_and_cover.py

Preparacion de Archivos

1.  fonts/:
    * Coloca la fuente que deseas usar para el titulo y subtitulo de la portada aqui (ej. roboto-bold-condensed.ttf). Asegurate de que la ruta en 02_generate_fragments_and_cover.py coincida.

2.  Images/:
    * cover_art.jpg: Esta es la imagen artistica que se usara como base para generar tu cover.jpg final.
    * Asegurate de que todas las imagenes referenciadas en raw_wikipedia.txt (usando @img:) existan en esta carpeta y tengan el mismo nombre de archivo.

3.  Styles/Style001.css:
    * Este archivo CSS contiene los estilos para tu EPUB. Es crucial para el centrado de imagenes. Asegurate de que incluya las reglas CSS necesarias para centrar las imagenes como se explico previamente.

4.  raw_wikipedia.txt:
    * Este es tu archivo de texto fuente.
    * Formato de Parrafos: Es crucial que los parrafos de texto esten correctamente unidos. Si copias y pegas desde un PDF, es posible que los saltos de linea esten incorrectos. Asegurate de que cada parrafo de tu libro sea una sola "linea" en este archivo, con un salto de linea en blanco entre parrafos para separarlos.
    * Imagenes: Las lineas de imagen deben seguir el formato: @img:nombre_imagen.jpg|Texto alternativo/Leyenda de la imagen
    * Titulos/Navegacion: Las lineas de titulo para la navegacion deben seguir el formato: [Capitulo 1 > Seccion A] o [Introduccion].

Pasos para Generar el EPUB

1.  Preparar input.txt:
    Ejecuta el script 01_parse_raw.py para procesar raw_wikipedia.txt y generar el archivo input.txt. Este input.txt sera utilizado por el siguiente script.

    python 01_parse_raw.py

2.  Generar Fragmentos XHTML y Portada:
    Ejecuta el script 02_generate_fragments_and_cover.py. Este script leera input.txt, creara la imagen de portada cover.jpg en la carpeta Images, y generara los archivos XHTML individuales para cada seccion y parrafo en la carpeta xhtmls_sequences.

    python 02_generate_fragments_and_cover.py

3.  Ensamblar el EPUB en Sigil:
    Una vez que los fragmentos XHTML y la portada se han generado:
    * Abre Sigil.
    * Importa la carpeta xhtmls_sequences (o arrastra los archivos).
    * Importa la carpeta Images.
    * Importa la carpeta Styles.
    * Anade la fuente roboto-bold-condensed.ttf (o la que uses) a Fonts en Sigil.
    * Utiliza las herramientas de Sigil para generar la Tabla de Contenidos (TOC), Portada (apuntando a cover.jpg), y otras propiedades del EPUB.
    * Guarda tu archivo .epub.

¡Listo! Con estos pasos, tendras tu EPUB personalizado generado y estructurado.
