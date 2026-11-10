# Arte de presentación de las novedades

Generado el 9 de noviembre de 2026 con **ImageGen integrado**, sin CLI ni clave de API. Se conservó la salida original fuera del repositorio y se guardó una copia WebP para la campaña. El arte no reemplaza ningún recurso de la aplicación.

Referencias: una imagen canónica de Capri suministrada por el autor del proyecto (rostro y geometría) y `assets/capri-escuchando-musica-v3.png` (diseño aprobado y manos). La nueva ilustración no lleva audífonos. Las capturas de funciones se añaden mediante composición HTML/CSS; no se generaron interfaces ficticias con IA.

Prompt exacto:

```text
Use case: ads-marketing. Asset type: portrait 9:16 illustration for a Spanish Capri desktop-companion update campaign; final artwork intended for 1080x1920 mobile posters. Generate a new polished vertical illustration using the two input images only as exact character-design references. Image 1 is Capri's canonical face, geometry, colors and hair texture; image 2 is another faithful approved depiction showing her hands. One Capri, no duplicate figures. Preserve giant angular scarlet/hot-pink hair with fine white static speckles, angular bright neon green eye-mask face, asymmetric circular cyan-blue eyes with tiny white centers, black lower face and fine zigzag white mouth, slender geometric black body with green and red fragments and subtle violet edges. Not human skin, not generic anime girl. NO headphones for this full-body depiction. Scene: Capri happily leaning out of an abstract angular cyberpunk frame, welcoming the viewer with one open angular hand, expressive tilted head, a playful dynamic pose. Background almost-black aubergine and deep midnight blue, restrained magenta and cyan electronic interference and broken scanlines. Crisp flat polygon animation aesthetic, sophisticated editorial poster lighting, controlled texture, no photorealism or 3D. Composition: full portrait 9:16, character dominant in middle and lower two thirds, keep upper quarter calm and dark to place a large headline later. Deliberate generous safe margins. No words, no letters, no numbers, no watermark, no UI, no logos. This is new campaign art, not a screenshot of the application.
```

El texto final de las siete láminas y su distribución están en `scripts/generar_novedades_verticales.py`. La exportación conserva la proporción de las imágenes.
