# Imágenes del README

La [selección actual de noviembre](../novedades-2026-11/seleccion-juegos/README.md) muestra once novedades de juegos, música y conversación, con portada corregida: formato horizontal para el README y vertical para TikTok. Usa capturas actuales con datos de demostración y una ilustración promocional editada con ImageGen; su procedencia se detalla por separado. La [primera edición](../novedades-2026-11/README.md) también se conserva.

## Galería actual · noviembre de 2026

Las imágenes de portada son **composiciones de capturas reales**, distribuidas sobre un fondo de presentación. No representan un único pantallazo simultáneo del escritorio. El visor de Capri y los diálogos se capturaron por separado; el visor procede de la misma versión de la aplicación. Las preferencias y conversaciones de la instalación principal no se utilizaron para las tomas de Capri.

| Archivo | Contenido |
| --- | --- |
| `capri-intro.webp` | Fotograma del renderizador nativo de la intro aprobada, con el saludo y la transformación al visor. |
| `capri-youtube.webp` | Reproductor real de YouTube después de enviar «Reanuda YouTube» a Capri, con la respuesta de la aplicación. |
| `capri-spotify.webp` | Playlist real de Spotify en pausa y respuesta de Capri a «Pausa Spotify». |
| `capri-lol.webp` | Cliente real de LoL y confirmación de la activación del monitor de aceptación automática. No había un ready-check pendiente: no se inició ni aceptó una partida para esta imagen. |
| `visor-actual.webp` | Ventana de Capri en modo pantalla. |
| `aspectos-actuales.webp` | Galería nativa de aspectos. |
| `capri-despedida.webp` | Fotograma de la despedida con el renderizador nativo, efecto de cámara y subtítulo. |

Las órdenes de las tomas se introdujeron por escrito en el intérprete de Capri, el mismo que recibe las transcripciones de voz. **Estas imágenes no documentan una prueba del reconocimiento por micrófono.** Las respuestas de control no se inventaron ni se retocaron. La reproducción de YouTube se confirmó mediante la sesión multimedia; en Spotify se eligió mostrar la pausa con su estado visible. El monitor temporal de LoL se detuvo después de la toma y ambas canciones quedaron en pausa.

Las capturas de servicios se recortaron para excluir pestañas del navegador, controles de cuenta y el panel de amigos de LoL. La playlist pública y los títulos musicales conservan el contenido visible. Las tomas se exportaron como imágenes estáticas y se codificaron a WebP para reducir el peso del repositorio; no contienen audio ni vídeo.

## Recursos históricos

Los PNG y GIF anteriores se conservan para los enlaces y las guías existentes. Se obtuvieron con los renderizadores de Capri y fondos de presentación; no son capturas de la versión actual. `scripts/generar_medios_readme.py` regenera **esos recursos históricos**, no las nuevas composiciones WebP.

### Regenerar los recursos históricos

Desde el repositorio en Windows, con Python 3.12 y las dependencias de `requirements.txt` instaladas:

```powershell
python scripts/generar_medios_readme.py
```

Las fuentes Chakra Petch incluidas en el proyecto se usan tanto en los rótulos como en los controles. El script exporta únicamente Canvas propios y genera las composiciones con Pillow. Los recursos del personaje conservan la procedencia y los derechos descritos en [arte y animación](../../ARTE_ANIMADO.md) y [avisos de terceros](../../../THIRD_PARTY_NOTICES.md).
