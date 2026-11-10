# Nombres fáciles para playlists de Spotify

Si el nombre original tiene símbolos, palabras difíciles o Capri no lo reconoce, el usuario puede darle un nombre sencillo dentro de Capri. Por ejemplo, vincular una playlist a **Para jugar** permite pedir **«Capri, pon mi playlist Para jugar»**. No cambia su nombre en Spotify.

El panel muestra el formulario y una biblioteca de guardadas. Cada tarjeta contiene el nombre elegido, la playlist vinculada y, para nuevos guardados, la fecha. Incluye filtro, edición, acceso al enlace de Spotify y retirada del vínculo con confirmación dentro de la tarjeta. Quitar el vínculo no elimina la playlist de Spotify.

**Nombre para Capri** y **Enlace de Spotify** son campos de texto completos: admiten clic, selección y pegado con **Ctrl + V**, además del botón Pegar enlace. Los ejemplos aparecen fuera de las entradas para no interceptar clics. El formulario se compacta en pantallas bajas y las portadas tienen mayor tamaño.

La biblioteca mantiene su buscador y el espacio de listas incluso vacía. El icono y los mensajes están centrados juntos dentro de ese espacio. Si un filtro no encuentra resultados, ofrece **Limpiar búsqueda**; estos estados no tienen desplazamiento.

## Persistencia y compatibilidad

El archivo privado `playlists.json` admite el formato anterior `nombre normalizado → URI` y un formato v2 con registros. Los nuevos registros conservan nombre visible, URI y fecha; el título original se añade si está disponible. Las lecturas no reescriben el formato anterior. Una escritura válida migra conservando los vínculos existentes.

La función `cargar()` sigue entregando el mapa normalizado que esperan las órdenes de reproducción. Las escrituras usan archivo temporal, flush/fsync y reemplazo atómico. Si falla o el documento existente es ilegible, no se reemplaza por una biblioteca vacía. Un cerrojo protege las actualizaciones del formulario y de los metadatos. Una respuesta tardía de Spotify solo enriquece los URI que aún estén guardados; no recrea vínculos retirados ni sobreescribe otro destino.

Los vínculos y la caché permanecen en la instalación del usuario. No se incluyen playlists personales en los paquetes de distribución.

## Vista previa opcional

El título y la miniatura se consultan mediante [oEmbed de Spotify](https://developer.spotify.com/documentation/embeds/tutorials/using-the-oembed-api). La respuesta puede incluir un título y una imagen; su disponibilidad depende del contenido. La [referencia oficial](https://developer.spotify.com/documentation/embeds/reference/oembed) documenta estos campos.

La consulta usa el enlace canónico de Spotify, sin OAuth ni cookies. Si oEmbed omite la imagen, lee los datos JSON del reproductor público y comprueba que pertenecen a la misma playlist; no ejecuta su HTML ni JavaScript. Solo admite miniaturas HTTPS de los CDN de Spotify, limita los datos descargados y conserva una miniatura de 256 px en caché. Cada tarjeta mantiene un enlace al recurso original. Si faltan datos, muestra el vínculo y el nombre elegido con una ilustración alternativa. El guardado y los comandos musicales no dependen de esta consulta.

## Portadas de playlists privadas

Spotify puede denegar la información de una lista privada a la consulta pública. Para conservar su imagen sin cambiar la privacidad:

1. Pulsa **Portada** en su tarjeta. Capri abre la playlist en Spotify, sin iniciar la reproducción.
2. Con la portada visible en tu sesión de Spotify, pulsa **Capturar**.
3. Selecciona la portada con el ratón. **Esc** cancela y recupera las ventanas de Capri.

Esta alternativa requiere seleccionar la imagen; no es una recuperación automática de listas privadas. La captura completa permanece en memoria mientras seleccionas y se descarta al terminar. Solo el recorte elegido se guarda en la caché local, se recupera al reabrir Capri y no lo reemplaza una descarga pública tardía.

Cuando falta la portada, la tarjeta explica que Spotify puede no compartirla en listas privadas y cómo usar **Portada → Capturar** para tomar un pantallazo y seleccionar la imagen. Esa explicación desaparece al disponer de una portada válida, incluida la guardada en una sesión anterior.

El panel y las confirmaciones de ajustes permiten mover las otras ventanas de Capri mientras están abiertos. Una confirmación sigue requiriendo pulsar su botón para aplicar el cambio.

También puedes abrir la biblioteca desde **Más → Playlists de Spotify**. Ambas entradas llevan a la misma ventana, que permanece abierta al cerrar Ajustes. Se prepara su distribución antes de mostrarla y conserva el contenido al cambiar de tamaño. El icono del estado vacío representa un disco, centrado con los mensajes.

## Verificación

Las pruebas cubren migración, recuperación desde otro proceso, nombres y acentos, edición, conflictos, errores de escritura y JSON, resultado tardío y retirada, vista previa opcional, escritura/pegado y biblioteca compacta. La selección de portada se comprueba con una imagen sintética y la apertura de Spotify simulada; falta verificarla con la sesión real del usuario. Las rutas musicales se comprueban con controles simulados; estas pruebas no inician música ni cambian playlists en Spotify.
