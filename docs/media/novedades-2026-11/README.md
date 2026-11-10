# Capri · Novedades en vertical

Siete láminas **1080 × 1920 (9:16)**, con textos grandes, composición para móvil y estética cyberpunk. La galería usa los mismos archivos que el README principal. Pulsa una imagen para abrirla completa.

| | | |
| --- | --- | --- |
| [![Portada](vertical/01-capri.webp)](vertical/01-capri.webp) | [![Playlists](vertical/02-playlists.webp)](vertical/02-playlists.webp) | [![Juegos](vertical/03-juegos.webp)](vertical/03-juegos.webp) |
| [![Confirmaciones](vertical/04-confirmaciones.webp)](vertical/04-confirmaciones.webp) | [![Monitor](vertical/05-monitor.webp)](vertical/05-monitor.webp) | [![Recordatorios](vertical/06-recordatorios.webp)](vertical/06-recordatorios.webp) |

[![Multimedia](vertical/07-multimedia.webp)](vertical/07-multimedia.webp)

## Qué muestran

1. **Capri:** portada de la actualización.
2. **Playlists:** biblioteca persistente y nombres fáciles para pedir música.
3. **Juegos:** LoL, Valorant, Fortnite, Counter-Strike 2 y Roblox dentro de Ajustes.
4. **Confirmaciones:** beneficio, coste y orientación según los recursos del equipo.
5. **Monitor:** CPU, RAM, GPU y VRAM encima del campo de escritura, activable en Ajustes.
6. **Recordatorios:** agenda general y creación de avisos por voz.
7. **Multimedia:** reproductor independiente y arte de escucha del modo pantalla.

## Procedencia y alcance

- `arte-capri.webp` es una **ilustración promocional nueva**, generada con la herramienta integrada ImageGen a partir de referencias del diseño de Capri. No es una captura ni un cambio del personaje instalado. El [prompt completo](PROMPT_ARTE.md) documenta la generación.
- Los PNG de `capturas/` muestran **controles reales de la aplicación**, capturados en ventanas propias con una instalación temporal y datos de demostración. No se utilizaron cuentas, preferencias, playlists, conversaciones ni datos de hardware de la instalación personal.
- Los nombres de playlists y sus identificadores son ejemplos. Sus portadas utilizan el icono incluido de Capri. No representan listas recuperadas de Spotify. La recomendación de modelos utiliza nombres y componentes de prueba; no es un diagnóstico de quien lee la imagen.
- El reproductor muestra una sesión sintética de ejemplo. No se abrió una cuenta de Spotify ni se inició música. LoL y Valorant se capturaron sin conexión al cliente y sin iniciar o aceptar partidas. Los recordatorios pertenecen a la instalación temporal. Los valores de CPU/RAM/GPU/VRAM son ejemplos.
- Las imágenes son composiciones editoriales con HTML/CSS, capturas y arte de presentación. No representan un pantallazo único del escritorio ni una prueba del reconocimiento por micrófono.
- El arte de escucha de la última lámina es el recurso existente `assets/capri-escuchando-musica-v3.png`, usado en modo pantalla. Las marcas y personajes conservan sus derechos; véanse [avisos de terceros](../../../THIRD_PARTY_NOTICES.md).

## Archivos y regeneración

El repositorio guarda **WebP** para reducir el peso, las capturas originales y los HTML/CSS editables de `vertical/`. Puedes abrir `vertical/VER-IMAGENES.html` o cada lámina HTML en un navegador. Para exportar PNG se necesita Chrome o Edge instalado; el script usa un perfil temporal y solo carga documentos locales.

Desde el repositorio, con las dependencias de Capri:

```powershell
python scripts/capturar_novedades.py
python scripts/generar_novedades_verticales.py
```

La exportación deja los **siete PNG, una galería HTML y un ZIP** en `Pictures/Capri/Novedades-2026-11-09-Vertical`. `--salida` permite elegir otra carpeta. `--sin-render` actualiza solo los HTML/CSS. El arte seleccionado ya está incluido; no se vuelve a generar ni se hace una llamada a un servicio de imágenes al exportar.

Los recursos antiguos de la [galería anterior](../readme/README.md) se conservan y tienen su propia procedencia.
