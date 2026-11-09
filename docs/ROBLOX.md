# Roblox con Capri

Abre **Ajustes → Juegos → Roblox → Partidas** y pulsa **Configurar Roblox**.
El panel tiene tres vistas: **Experiencias**, **Avatar** y **Acompañamiento**.
El panel se muestra dentro de Ajustes. Pulsa **Volver** para regresar a la página anterior; tus cambios quedan guardados.
Los recordatorios tienen su propio panel en **Más → Recordatorios**.

## Experiencias: accesos rápidos y personalidad automática

Pulsa **Agregar experiencia** y pega la dirección oficial de un juego o su ID.
El nombre personalizado es opcional: si lo dejas vacío, Capri consulta el nombre
público del juego. Un nombre que escribas tú se conserva como alias para la voz.
Seleccionar o guardar un favorito no inicia Roblox.

**Abrir experiencia** abre su enlace oficial. También puedes decir **«Capri, abre
DOORS en Roblox»**, usando el nombre guardado. Es un acceso rápido; abrir el enlace
no demuestra que una partida haya cargado. Se admiten enlaces oficiales compartidos
y privados, sin pedir cookies ni contraseñas. Para consultar descripción y categorías
se necesita un ID o un enlace a la página del juego; algunos enlaces compartidos no lo exponen.

La tarjeta muestra la imagen, el creador, la categoría y la descripción pública.
Los iconos y los datos públicos se guardan en la caché local de Capri. Cambiar de
favorito o reabrir el panel recupera lo guardado inmediatamente; una descarga que
termina mientras miras otro juego también queda disponible. Los datos se renuevan
en segundo plano cuando corresponde, y **Actualizar** fuerza una consulta nueva.
La primera descarga necesita conexión. Los iconos existentes siguen disponibles
si falla la red; una respuesta temporal sin imagen no borra el icono guardado.
Capri deduce un perfil de esa información: Terror, Aventura, Estilo, Discreta o
Capri clásica. No tienes que elegir el perfil ni escribirle instrucciones de personalidad.
Es una clasificación local de texto, sin una petición al modelo por cada consulta;
descripciones vagas o categorías incorrectas pueden producir un perfil menos preciso.
**Actualizar** permite consultar de nuevo la información.

Terror reduce el volumen de sus respuestas al 75 % del volumen configurado y
Discreta al 60 %, solo mientras Roblox esté al frente. No cambia tu volumen guardado.
Su contexto distingue entre un favorito seleccionado y la última experiencia
identificada en el cliente; no trata una descripción como prueba de sucesos de la partida.

La rueda del ratón desplaza la zona sobre la que estás: biblioteca o detalle.
La barra aparece solo si hace falta. No hay un desplazamiento global que mueva ambos paneles.
Si el contenido cabe completo, permanece arriba y la rueda no deja huecos. El campo
**Buscar en mis favoritos** filtra por nombre al escribir; la cruz limpia la búsqueda.

Las notas y la elección manual de perfiles dejaron de formar parte de la interfaz.
Las notas anteriores se conservan en los ajustes de ese equipo; no se borran al actualizar.

## Avatar: opiniones sobre piezas concretas

Guarda tu nombre de usuario real o ID en **Avatar** y pulsa **Mirar mi avatar**,
o pregunta **«¿Qué te parece mi avatar de Roblox?»**. El nombre visible puede
coincidir con el de otras personas; usa el identificador de tu cuenta.

Capri consulta la lista pública de prendas/accesorios y la miniatura oficial.
Los comentarios mencionan hasta tres piezas por su nombre y ubicación conocida,
priorizando accesorios de hombro, espalda y rostro. Puede opinar a favor o en contra
de una pieza y mantiene ese gusto al cambiar otras prendas. Por ejemplo, reconoce
que un `ShoulderAccessory` va en el hombro porque Roblox lo identifica así, aunque
su nombre no contenga la palabra «hombro».

La ubicación procede del tipo oficial, no de adivinarla por una imagen. No identifica
el hombro izquierdo/derecho, colores, materiales o detalles visuales que esos datos
no confirmen. La opinión es parte de su personalidad ficticia, no una puntuación de Roblox.
El personaje que un juego impone dentro de su partida puede diferir del avatar de la cuenta.

**Comentar cambios de mi avatar** comprueba cambios aproximadamente cada minuto,
solo con Roblox al frente y Capri disponible. La primera lectura establece una referencia;
después comenta un conjunto distinto sin repetir continuamente la misma opinión.

## Acompañamiento durante la partida

Activa **Acompañamiento automático** para que Capri intente reconocer avisos
de victoria, derrota o muerte. No hay botones para contarle cada resultado ni
campos de palabras que tengas que rellenar.

La integración incluye avisos habituales en varios idiomas, confirma el texto en dos
lecturas y deja una pausa entre reacciones. Si aparece un final ambiguo, como
`Game over`, pregunta qué ocurrió en vez de celebrar o lamentarlo sin saberlo.
Puedes responder «gané», «perdí» o «me morí». La pregunta usa tu modo de escucha
existente: **Después de una pregunta** permite contestar sin volver a decir «Capri».

Mientras Roblox está al frente, también intenta obtener el ID de la última experiencia
desde el registro reciente del cliente local. Solo extrae el identificador del ingreso:
no guarda ni envía el registro. Consulta con ese ID la descripción y categoría públicas.
Si no puede identificar la partida, conserva el favorito elegido como referencia y
no afirma que haya confirmado el juego actual.

El reconocimiento de resultados usa capturas temporales de una zona central de la
ventana de Roblox y el OCR local de Windows. No se capturan otras aplicaciones,
no se suben imágenes y una ventana que cambia durante la lectura invalida el resultado.
La zona central ayuda a excluir el chat y avisos laterales; no significa que el usuario
tenga que escribir las palabras que aparecen allí.

**Alcance:** hay juegos con textos, idiomas o finales que todavía no reconoce.
No es detección universal de todas las muertes ni lectura del estado interno del juego.
Un aviso continuo no dispara reacciones repetidas. La integración no mueve al personaje,
pulsa botones, canjea recompensas, compra objetos ni cambia el foco de tus ventanas.

## Recordatorios generales

Abre **Más → Recordatorios** o di **«Capri, abre mis recordatorios»**.
Puedes crear o cancelar avisos sin abrir Roblox:

- «Recuérdame en 20 minutos hacer una pausa».
- «Avísame dentro de 2 horas revisar el horno».
- «Cancela mis recordatorios».

Se conservan la hora y el texto al cerrar Capri. Los vencidos se retoman una sola vez
al volver a abrirla, esperando si está ocupada. No se ejecutan avisos mientras Capri
está cerrada. El panel admite cancelaciones individuales; las órdenes también funcionan
en los cuatro idiomas de la interfaz. Los avisos antiguos de Roblox se trasladan
automáticamente a esta agenda sin cambiar su fecha.

## Validación y fuentes

Se comprobaron consultas públicas reales de experiencia, icono, avatar y miniatura,
la interfaz en tamaños grande/compacto y casos simulados de resultados y seguimiento
de preguntas. Falta validar el reconocimiento de resultados durante partidas reales
de las experiencias del usuario. No se iniciaron partidas para realizar estas pruebas.
Esta integración no añade una superposición sobre pantalla completa exclusiva.

Información oficial consultada:
[experiencias y descripción](https://create.roblox.com/docs/cloud/reference/features/universes),
[avatares](https://create.roblox.com/docs/cloud/reference/features/avatars),
[tipos y ubicaciones de accesorios](https://create.roblox.com/docs/reference/engine/enums/AvatarAssetType),
[miniaturas](https://create.roblox.com/docs/cloud/reference/features/thumbnails),
[enlaces compartidos](https://create.roblox.com/docs/production/promotion/share-links) y
[política de aplicaciones de terceros](https://en.help.roblox.com/hc/en-us/articles/37924211313044-Creator-Third-Party-App-Policy).
