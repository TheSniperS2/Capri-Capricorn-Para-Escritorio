# Capri

**Ctrl+Alt+C** recupera solo el avatar de Capri, sin abrir el chat, o la oculta si ya la tienes al frente. También puedes ocultarla con el botón **—** del chat o de los paneles de juego, y recuperarla con ese atajo. La voz y las automatizaciones continúan mientras está oculta. Abre el chat o los paneles desde el menú de Capri cuando los necesites. En el chat, elige **Valorant** en **Juego para buscar** para escribir «busca partida» aunque el juego esté en segundo plano; abrir su panel también guarda ese destino.

En **Más → Valorant** puedes buscar o cancelar partidas y configurar tres preferencias de agente. Si un aliado ocupa la primera, se prueba la segunda y después la tercera; si no queda ninguna válida, no se selecciona otro agente. La selección automática es opcional y viene apagada. Consulta la [guía de Valorant](VALORANT.md).

En **Más → Fortnite** puedes elegir Battle Royale o Cero construcción y Solo, Dúo, Trío o Squad. También puedes conservar las opciones del juego, aplicarlas sin buscar, iniciar la búsqueda y cancelarla. Deja el lobby preparado: Capri usa reconocimiento de texto local de Windows y controles normales del juego, sin programas adicionales. La cancelación nunca inicia otra búsqueda. Consulta la [guía de Fortnite](FORTNITE.md).

Puedes dar las órdenes de Fortnite aunque lo tengas minimizado. Capri lo restaura automáticamente y espera a que el lobby esté listo antes de actuar; el juego aparece en primer plano durante la operación.

En **Ajustes → Reacciones**, activa **Reaccionar a las skins** y el juego que quieras. Elige una skin y deja su ficha con el nombre visible: Capri puede comentarla automáticamente. También detecta cambios de equipamiento propio en Valorant fuera de partida. Incluye Goku Black y miles de skins; las que no tienen diálogo propio reciben una opinión genérica positiva, neutral o negativa que se mantiene incluso al reiniciar. Acepta **«mira mi skin en Fortnite/Valorant»** y **«¿qué te parece esta skin?»**. Las reacciones esperan mientras conversas con Capri y no cambian el foco del juego. Esta función sigue en desarrollo: puede tardar y fallar al identificar algunos nombres; detectar una nueva selección real sigue pendiente. Consulta la [guía de reacciones](REACCIONES_SKINS.md).

Para LoL, abre **Más → League of Legends** en el menú radial para entrar directamente al panel, o pulsa el botón de LoL en **Ajustes → IA y servicios**. En un mismo panel puedes buscar, aceptar y cancelar partidas, activar la aceptación automática y guardar tres picks y tres baneos por cada línea. La confirmación automática de campeones se activa por separado y viene apagada. Consulta la [guía de LoL](LEAGUE_OF_LEGENDS.md).

¿Todavía no tienes el lanzador o falla la preparación? Consulta la [instalación paso a paso](../README.md#empieza-a-usarla) y los [errores frecuentes](INSTALACION.md).

Para cambiar entre pantalla y personaje, usa clic derecho → **Transformar en personaje/pantalla**. El control ampliado de archivos, aplicaciones y ventanas se activa por separado en Ajustes y está apagado por defecto. Consulta la [guía de personaje, permisos y confirmaciones](PERSONAJE_Y_CONTROL.md).

Abre **Abrir Capri.pyw**. La primera apertura instala sus dependencias en una carpeta propia, descarga Whisper base multilingüe (148 MB), el reconocimiento rápido de respaldo y las referencias de Capri. Verás el avance; necesita internet para esa preparación. Al actualizar conserva tu micrófono y los modelos de conversación ya descargados.

Después aparece una ventana flotante con la imagen del personaje. Arrástrala para moverla. Haz clic para abrir el chat. Pulsa **F8** o **Hablar** para dictar una frase; haz una pausa para que responda. Pulsa **Esc** para detener la voz. El menú del botón derecho permite salir. Se crea un acceso directo **Capri** en el escritorio; también puedes abrir otra vez el lanzador de esa versión. Para actualizar, genera uno nuevo desde el código actual; volver a abrir un lanzador antiguo no descarga las últimas novedades.

También puedes decir **«Capri»** y dar la orden, o decir **«Capri, busca memes de Cyberpunk»** en una misma frase, sin esperar un aviso. Se conserva la misma captura desde el nombre hasta terminar la orden, aunque el reconocedor la divida en varios segmentos. Si dices solo «Capri», espera hasta seis segundos de silencio por la instrucción sin cerrar ni volver a abrir el micrófono. Después de la orden espera aproximadamente 0,85 segundos de silencio antes de transcribir. La activación está habilitada al abrir normalmente la aplicación; usa el micrófono seleccionado y el modelo Vosk local ya instalado. Whisper transcribe el audio completo al terminar si elegiste Mixto. La escucha mantiene solo un fragmento temporal en memoria, sin archivos ni envío de audio. Se pausa mientras Capri habla y al configurar los Ajustes, y se reanuda automáticamente. Si Valorant está en primer plano, la activación por nombre puede continuar aunque Ajustes quede abierto detrás del juego. Durante su voz, usa Hablar o F8 para interrumpir. Puedes desactivar **Ajustes → Activar al decir «Capri»**. La detección depende del ruido y de la pronunciación; no es una garantía de reconocimiento en cualquier ambiente.

En **Ajustes → Micrófono** puedes elegir la entrada de audio que quieres usar. La selección se guarda para las próximas aperturas. Si conectas otro micrófono, pulsa **Actualizar**. La lista oculta las repeticiones de un dispositivo que Windows ofrece mediante varias interfaces de audio. «Predeterminado de Windows» es una opción automática, no un micrófono adicional. Si el elegido se desconecta, Capri avisa en lugar de cambiar automáticamente al micrófono de los audífonos.

La captura se inicializa en un hilo de audio propio de Windows. Evita WDM-KS y, si una interfaz falla, intenta otras variantes inequívocas del mismo micrófono. Si no logra abrirlo, `diagnostico-microfono.json` contiene los intentos y los errores del controlador, sin grabaciones ni texto reconocido.

**Ajustes → Reconocimiento de voz** permite elegir **Whisper · español y nombres en inglés** o **Rápido · Vosk español**. Whisper usa el modelo multilingüe instalado con español fijado para evitar que frases breves se interpreten como italiano u otro idioma. Conserva nombres de aplicaciones y canciones en inglés y aporta Spotify, YouTube y Opera GX para favorecer su reconocimiento sin traducirlos. Este perfil está pensado para hablar en español. Al abrir aplicaciones también acepta variantes de pronunciación como «espotifai». Whisper hace una pausa breve al detectar el final de la frase y después la transcribe. Si el resultado es dudoso, aparece en el cuadro de texto para revisarlo antes de enviarlo. La precisión real depende del ruido y del micrófono. Su primera carga tarda más; el modelo queda en memoria para las siguientes frases.

Algunas órdenes: «abre una pestaña en Opera GX», «puedes abrirme una pestaña», «me gustaría que abrieras una pestaña del Opera GX», «abre una pestaña y busca recetas de pasta», «abre la calculadora», «abre Spotify», «habla más rápido» o «qué hora es».

Las búsquedas admiten, por ejemplo, «búscame memes de Cyberpunk», «puedes buscarme memes de Cyberpunk», «quiero que busques memes de Cyberpunk» y «haz una búsqueda de memes de Cyberpunk». Abren la consulta en Opera GX. También puedes pedir «abre mis archivos», «abre Descargas», «abre Documentos», «abre Imágenes» o «abre el Escritorio»; las carpetas respetan las ubicaciones configuradas en Windows.

Para Spotify: **«reproduce la música»**, **«reanuda la canción»** y **«pon la música»** reanudan la sesión actual, sin buscar otra canción ni cambiar la cola. **«Salta la canción»**, **«pon la siguiente canción de la playlist»** y **«podrías poner la música siguiente»** pasan a la siguiente pista de la cola actual; **«pon la canción anterior»** vuelve a la anterior. **«Pausa Spotify»** pausa esa sesión. **«Qué canción está sonando»** consulta el título y estado que comunica Spotify. Estos controles usan la sesión multimedia de Windows de Spotify, sin abrir páginas ni buscar canciones. Si Spotify no comunica una sesión o rechaza una orden, Capri lo indica. El modelo de charla no afirma qué está sonando basándose en sus propias respuestas.

Para elegir otra canción: «busca Never Fade Away en Spotify» o «reproduce Never Fade Away en Spotify». La búsqueda usa la aplicación instalada. Para reproducir un título concreto, Capri intenta invocar un control accesible cuyo nombre coincida con la búsqueda. Necesita una sesión iniciada y controles accesibles en Spotify. No pulsa coordenadas ni envía teclas a otra ventana. Si no puede confirmar el control, mantiene abierta la búsqueda y lo informa.

Para playlists: **«pon mi playlist Cyberpunk»** intenta encontrarla en **Tu biblioteca**, sin buscarla entre playlists públicas. Si Spotify no expone la biblioteca mediante controles accesibles, usa **Ajustes → Vincular playlist de Spotify**: introduce el nombre y pega su enlace. Puede seguir siendo privada; debe ser accesible desde tu cuenta iniciada. Se guarda solo el nombre y el identificador de playlist en `playlists.json`, sin contraseña ni tokens. Una vez vinculada, también admite «pon Cyberpunk». No hace públicas listas ni cambia permisos. Si abre una playlist pero no puede confirmar su reproducción, lo informa. La reproducción real y el acceso a la biblioteca no han podido verificarse desde el entorno restringido de desarrollo.

El nombre del navegador se detecta automáticamente, con preferencia por Opera GX. Las búsquedas se abren como una pestaña de Google; la aplicación no lee ni resume sus resultados. Solo abre las aplicaciones que tiene registradas.

Las órdenes reconocidas de pestañas, páginas y aplicaciones van al ejecutor del programa, sin pedir al modelo que las describa. Una pestaña nueva sin destino usa una página en blanco. Las acciones de computador que todavía no estén implementadas muestran un aviso. Las preguntas sobre cómo hacer algo siguen siendo conversación.

Las aperturas toleran errores pequeños de transcripción en el comienzo de la petición, como «Podríes avrir Spotify»: corrigen una letra omitida, cambiada o intercambiada si el destino es una aplicación conocida. La corrección no cambia el texto de búsquedas ni convierte frases negadas o explicaciones en órdenes. La conversación conoce las capacidades reales del ejecutor y corrige negativas globales falsas sobre abrir Spotify o aplicaciones; no presenta una acción como realizada si no pasó por el ejecutor. Esto mejora la interpretación de la frase recibida, sin garantizar que el reconocimiento de voz transcriba todas las palabras correctamente.

Para conversación libre: **Ajustes → Activar IA local → Descargar y activar**. Se descargan Ollama y llama3.2:3b (aprox. 2 GB de modelo, más el instalador). Después conversa sin pago por uso. Si ya tienes Ollama con un modelo, se usa automáticamente. No se ejecuta código propuesto por la IA.

Con la IA local activada, las peticiones que no se reconocen directamente pasan a un intérprete de intención. Puedes decir «¿podrías dejar la música en pausa un ratito?», «detenla un momento», «pon otra» o «prefiero la de antes». Tras pausar Spotify, «ahora sigue» usa ese contexto para reanudar. Si no hay un referente claro, Capri pregunta a qué te refieres. Los agradecimientos conservan el tema; una conversación sobre otro asunto lo cambia. El intérprete conserva hasta cuatro turnos durante tres minutos, solo en memoria, con el resultado real del ejecutor. No supone que una acción fallida se completó. Al cerrar la aplicación ese contexto desaparece.

El modelo interpreta una acción por turno entre las capacidades existentes; no genera ni ejecuta comandos de consola. La interpretación local puede tardar más durante la primera carga. Esto amplía la comprensión de peticiones y referencias, sin garantizar que cualquier frase o transcripción de voz sea entendida correctamente.

El micrófono se reconoce localmente. El audio permanece en memoria y no se graba en archivos. La voz natural de respuesta usa Microsoft Edge TTS y requiere internet: se envía el texto a sintetizar. Se puede desactivar en Ajustes para usar la voz de Windows. El perfil Capri usa una voz sintética femenina en español latino con ritmo y tono más enérgicos; no reproduce el timbre exacto de la actriz. La memoria del chat dura solo mientras la aplicación está abierta.

La velocidad inicial es **1×**, normal, tanto en la voz natural como en la voz de Windows. Para una lectura más fluida, el texto hablado omite marcas de formato y reduce las pausas de comas, dos puntos y punto y coma; conserva puntos y preguntas. La velocidad se cambia en **Ajustes → Velocidad de voz**, o con «habla más rápido», «lee más lento» y «habla a velocidad normal». La elección se guarda.

La identidad se fija como **Capri** en cada petición y las presentaciones sencillas responden directamente. El texto aparece mientras se genera; la respuesta se narra completa en una sola lectura para evitar esperas entre audios separados de cada frase. **Hablar o F8 interrumpen la voz y la respuesta pendiente antes de activar el micrófono**, incluso si todavía estaba preparando el audio. Se mantiene el modelo local cargado durante 15 minutos y se limita la longitud normal de las respuestas para reducir la espera. La primera carga del modelo, el uso de la GPU por otros programas y la conexión de la voz natural influyen en la demora.

Los archivos instalados quedan en **%LOCALAPPDATA%\Capri**. Allí están ajustes.json (sin claves), modelos/ y assets/. Capri no se añade al inicio automático de Windows. No requiere permisos de administrador.

El icono de las ventanas y del acceso directo del escritorio usa la referencia de Capri incluida en la aplicación, convertida a un icono de Windows con varios tamaños. No se modifica su rostro. Windows puede conservar temporalmente en caché el icono anterior de un acceso anclado a la barra de tareas; desanclar ese acceso antiguo y anclar de nuevo el acceso Capri actual permite actualizarlo.

## Elegir dónde reproducir y qué resultado abrir

El servicio que nombras tiene prioridad sobre el tema anterior de la conversación:

- **«Reproduce High Forever en Spotify»** busca y reproduce la canción en Spotify.
- **«Reproduce High Forever en YouTube»** abre sus resultados en YouTube. Después puedes decir **«reproduce el primer video»**, **«pon el segundo resultado»** o **«reproduce el video número 3»**, hasta el décimo. El [puente con Opera](CONECTAR_OPERA.md) 1.0.4 permite seleccionarlos sin reproductor cargado: usa la búsqueda seleccionada o la única abierta. No inicia otra búsqueda ni pulsa coordenadas. Sin conexión con la extensión intenta los enlaces accesibles de la página seleccionada como respaldo.
- **«Reproduce High Forever en mi playlist Capri»** busca exclusivamente dentro de esa playlist. Si dices solo **«en mi playlist»**, reutiliza una lista nombrada recientemente; si no conoce ninguna, pregunta su nombre. Responder **«Capri»**, **«de la playlist Capri»** o **«se llama Capri»** completa esa misma petición y conserva la canción pendiente.
- **«Reproduce esta canción en mi playlist Capri»** consulta el título comunicado por la sesión de Spotify y lo busca dentro de esa lista. Si Spotify no comunica el título, pide que lo indiques.

Si la canción no aparece dentro de la playlist o no se puede confirmar el control, Capri lo informa y conserva el alcance de la lista. No convierte esa petición en una búsqueda general de Spotify.

**Escribir** abre el campo sin volver a mostrar el globo de una conversación anterior. Si cambias de idea, pulsa otra vez Escribir o deja el campo: se cierra ese modo sin enviar nada y conserva el borrador. Las conversaciones anteriores siguen disponibles en Chat.

## Apagado, Discord y voz

### Apagado con secuencia visual

Activa Control ampliado en Permisos y pide «apaga el computador». La orden directa no necesita interpretar la intención con un modelo. Después de **«sí, confirmo»**, se reproduce una secuencia de unos 6,6 segundos: interferencia, avisos narrativos cyberpunk, FLATLINE y compresión de la imagen hasta una línea. **Esc** durante esa secuencia cancela el efecto y no envía ninguna orden de apagado a Windows. Al terminar, se solicita `shutdown.exe /s /t 0`, sin `/f`: Windows conserva su gestión de programas con trabajo pendiente y su pantalla real de apagado. Una vez que Windows inicia esa fase, Esc ya no es la cancelación de Capri.

El apagado confirmado muestra una animación a pantalla completa. Puedes cancelarlo con Esc o la cruz antes de que termine. Si la animación falla, se cancela el apagado y se informa del error. Cerrar Capri normalmente conserva su despedida de la mano y la estrella.

### Discord

La integración usa Discord de escritorio con la cuenta que ya tengas iniciada. No inicia sesión, no pide tokens y no necesita un bot. «Silénciame» cambia tu micrófono; «ensordéceme» cambia la escucha de Discord y puede silenciar también el micrófono según el comportamiento propio de Discord. La función comprueba las etiquetas del control antes y después; no pulsa un conmutador a ciegas ni repite clics si el cambio no se confirma.

Ejemplos: «abre Discord», «puedes mutearme en Discord», «desmutéame en Discord», «ensordéceme en Discord», «desensordéceme en Discord». Después de una acción explícita en Discord, admite el contexto reciente para «silénciame» o «desmutéame». Para unirte: «únete al canal de voz General del servidor Amigos en Discord». Si ya tienes abierto el servidor, basta con el nombre del canal. Necesita que Discord publique el canal como canal de voz y que haya una coincidencia inequívoca; no opera canales de texto ni otros usuarios.

Las actualizaciones de Discord, el idioma de su interfaz, una ventana cerrada o sus controles de accesibilidad pueden impedir la acción. No se garantiza control con Discord oculto o minimizado. Los controles de silencio/ensordecimiento están preparados para etiquetas españolas, inglesas y algunas portuguesas. El ejecutor solo confirma un cambio de estado cuando lo puede leer; al entrar en un canal informa que envió la solicitud.

### Idioma, perfil y voz/acento

**Idioma de Capri** cambia la interfaz y el idioma del contenido escrito/hablado. **Voz y acento independientes** elige el timbre/origen de quien lee ese mismo contenido. Elegir portugués aquí no traduce una respuesta española. Puedes cambiar después el idioma a inglés o japonés y se conserva la voz elegida. Para volver al comportamiento anterior, selecciona **Seguir el idioma de Capri**; en español se recupera el perfil español que tenías seleccionado.

Thalita y Emma son voces multilingües. Si la síntesis de Thalita falla, se intenta Francisca de Brasil sin traducir el texto ni cambiar tu selección guardada. El tiempo de espera se adapta al texto y una voz fija no queda bloqueada por el fallo de una petición anterior. Las otras voces pueden pronunciar idiomas ajenos de forma menos natural; la elección no garantiza un acento regional exacto. La voz natural necesita conexión y transmite el texto de respuesta a Microsoft. Si se usa el respaldo de Windows, debe existir una voz instalada de la cultura elegida. La selección no modifica el micrófono, el reconocedor ni el modelo de IA.

## Elegir modelos

En Ajustes puedes seleccionar el modelo de conversación instalado en Ollama. Se utiliza tanto para conversar como para interpretar peticiones con contexto. El selector muestra únicamente modelos locales instalados; cambiarlo no borra los anteriores. La primera carga del modelo seleccionado puede tardar más. «Activar IA local» conserva el modelo que hayas elegido.

Debajo del modo de reconocimiento puedes elegir **Whisper base** o **Whisper small** si están instalados. Elegir un modelo en ese selector activa también el perfil Whisper; no queda activo Rápido/Vosk por una selección anterior. Small es más pesado y puede aumentar la espera, especialmente en CPU; Base permite volver a una respuesta más rápida. El cambio se aplica a las siguientes capturas. Si falta el modelo seleccionado, se usa uno instalado; Vosk se conserva como respaldo. La primera instalación sigue descargando Base, y los pesos no se incluyen en el ZIP.

Para preparar Small desde el código fuente: `python src/preparar_whisper.py RUTA_DE_MODELOS small`. Se descarga a una carpeta independiente, sin sustituir Base. Este paso necesita internet; después el reconocimiento funciona localmente.

## Apariencia y procedencia

La aplicación muestra las referencias publicadas de Capri y conserva sus rasgos. Anima la flotación, las partículas y el cambio de imagen al hablar. Esta primera versión no tiene un cuerpo 3D ni animación labial del anime.

Referencias del personaje: https://mudae.net/character/3127100/Capri%20%7BCP%7D

Capri y las imágenes de la serie pertenecen a sus respectivos titulares. Aplicación de aficionado para uso personal, no oficial. El avatar usa una imagen base de la galería indicada en ARTE_ANIMADO.md y las referencias adicionales se descargan desde esa galería; no se incluyen episodios ni se modifican archivos del juego.

Vosk y modelos: https://alphacephei.com/vosk/models

Whisper base: https://huggingface.co/Systran/faster-whisper-base

Faster Whisper: https://github.com/SYSTRAN/faster-whisper

Ollama: https://ollama.com/

Edge TTS: https://github.com/rany2/edge-tts

## Estado de verificación

El dictado usa búsqueda de cinco candidatos y contexto de órdenes musicales, conservando los nombres ingleses. Las transcripciones «revoluces la canción» y «ciente canción» se interpretan como reanudar y siguiente únicamente cuando forman una orden completa; no se sustituyen palabras dentro de búsquedas, títulos o negaciones. Esto mejora la interpretación de esos errores conocidos y no garantiza una transcripción perfecta.

El nombre con que vinculas una playlist puede ser un alias. Para reproducirla, Capri busca el botón con el título real dentro de la página de esa playlist, aunque el título use emojis. La confirmación requiere el botón de pausa de esa misma playlist; el botón de pausa general no sirve como prueba. Si Spotify no expone esos controles, Capri informa que no pudo confirmar la reproducción.

Para una canción dentro de una playlist: **«reproduce High Forever de mi playlist Capri»**. Usa el nombre real de la playlist. Capri abre esa lista desde Tu biblioteca y filtra su tabla de canciones; no sustituye la petición por una búsqueda general ni trae Spotify al frente. Exige una única fila con ese título y su control de reproducción accesible. Si hay duplicados o Spotify no expone esos controles, lo informa sin reproducir otro resultado.

En **Ajustes → Volumen de Capri** puedes elegir de 0 a 100%. Se guarda para las siguientes respuestas, tanto con voz natural como con la voz de Windows; 0% la silencia. El control no modifica el volumen de Spotify ni el volumen general del equipo.

Puedes decir «Capri abre Spotify» seguido, sin esperar una señal. El aviso de escucha aparece en cuanto el reconocedor libre detecta el nombre, sin esperar a terminar la frase. Ese aviso todavía no autoriza ejecutar nada: en modo Whisper, el dictado del audio original debe confirmar «Capri» al principio antes de enviar la orden. Vosk puede proponer la confusión «Capriles» para esa comprobación, pero esa palabra nunca autoriza una orden por sí sola. Si Whisper no confirma «Capri», la frase se descarta. En modo Rápido, sin esa comprobación independiente, se exige el nombre exacto en el resultado final de Vosk. Se conserva una única captura y un margen breve de audio para no perder el principio de una orden rápida. F8 y Hablar son activación manual y no requieren decir el nombre. La precisión con voz real depende del micrófono y del ambiente.

La activación aplica una ganancia limitada al audio de voz bajo antes de enviarlo a Vosk y usa un umbral más bajo para captar frases suaves. No cambia el volumen del micrófono en Windows. La ganancia no amplifica el silencio, está limitada a tres veces y evita saturar los picos; la captura original se conserva para Whisper. La detección del nombre todavía depende del micrófono, el ruido y la pronunciación.

Al activar por nombre, la barra muestra el nivel del micrófono durante la captura. El detector de voz local incluido con Whisper distingue habla de ruido continuo para cerrar tras aproximadamente un segundo sin voz; si no está disponible, se usa el umbral de volumen de respaldo. Decir solo «Capri» conserva una ventana para dar la orden. Al cerrar el micrófono, el estado cambia a «Reconociendo la frase» mientras se transcribe. El nombre de activación se quita del dictado antes de enviarlo al chat, también si se dijo usando F8; escribirlo manualmente conserva el texto escrito.

Una pausa sin voz finaliza la hipótesis pendiente de Vosk sin esperar varios segundos a su cierre interno. Una nueva frase descarta el audio de conversación anterior con un margen breve para conservar el comienzo del nombre. Todas las repeticiones consecutivas de «Capri» se quitan del dictado.

## Sensibilidad del micrófono

En **Ajustes → Micrófono** puedes elegir la entrada de audio y ajustar su sensibilidad. Los cambios se guardan automáticamente.

El **umbral automático** está recomendado. Para ajustar manualmente, desmárcalo y mueve el control: **izquierda = capta voz más baja; derecha = exige hablar más fuerte**. El filtro se aplica al reconocimiento por nombre y al dictado F8; no cambia el volumen del micrófono de Windows.

## Diálogos junto al personaje

La conversación usa un panel pequeño con la última pregunta y la respuesta. Se coloca encima del personaje si hay espacio y, si no, a un lado. La entrada para escribir está siempre debajo de la imagen de Capri; un clic en el personaje la enfoca. Enter o la flecha envían el texto. No hay botones permanentes Hablar/F8/Escribir ni controles Historial/Detener dentro del diálogo. F8 activa el dictado y Escape lo interrumpe. El menú contextual, con clic derecho, permite abrir Ajustes, consultar Historial o cerrar Capri. Hablar no abre automáticamente el historial grande. El historial dura solo mientras Capri está abierta; el panel pequeño muestra el tramo reciente de respuestas extensas. Los dictados dudosos se revisan en la entrada debajo de la imagen.

El glitch añade un cursor y pequeños trazos transitorios durante la escritura; nunca modifica el texto confirmado, el historial ni la entrada enviada al modelo. Puedes desactivar **Interferencias breves de imagen y texto**. Escape oculta el diálogo e interrumpe la respuesta. La opción **Mostrar diálogos progresivos junto a Capri** controla su aparición automática; la entrada permanece disponible debajo de Capri. El fondo exterior a las esquinas del diálogo es transparente en Windows.

El avatar conserva la ilustración base: las tres variantes solo cambian una pequeña región de la boca (normal, abierta completamente blanca y sonrisa). El pelo, cuerpo y pose son idénticos. La vista aplica un recorte de cámara, suavizado, grano animado, barrido y una viñeta tenue. Las interferencias fragmentan bandas durante unos 0,22–0,42 segundos y después vuelven a la señal normal. El personaje también muestra fragmentos desplazados y separación violeta/verde, con fondo transparente. Son menos frecuentes en reposo y algo más frecuentes al hablar. **Interferencias breves de imagen y texto** permite desactivar las ráfagas y el grano animado. Al desactivar las animaciones se mantiene la imagen normal fija, con textura estática de pantalla.

Con voz activada y volumen mayor que cero, el texto visible espera a que empiece la reproducción. La voz natural usa las marcas de palabra y el reloj del reproductor para revelar el texto; la boca descansa entre marcas de habla. La voz de Windows se sintetiza primero a un WAV temporal y usa el mismo reproductor, con avance aproximado según la duración porque no aporta esas marcas. No se fragmenta la lectura en peticiones separadas. La preparación puede tardar: el panel muestra **Preparando voz** durante esa espera. Sin voz o con volumen cero, se conserva la escritura progresiva independiente. Estos tiempos siguen al reproductor, no prometen alineación fonética exacta ni compensan toda latencia del dispositivo de salida.

## Preparación al iniciar

La cabecera muestra **Conectando** mientras el detector se prepara. La entrada se abre antes de cargar Vosk y el detector de voz, y conserva el audio inicial en una cola acotada durante esa preparación. El estado pasa a **Enlace activo** cuando la entrada y los detectores están preparados. La precarga del modelo de conversación empieza después de esa preparación para dar prioridad al micrófono. Durante reconocimiento o reproducción puede haber otros estados; no significan que la activación esté lista. Esto evita perder por diseño toda la primera frase mientras se carga el detector, pero no garantiza precisión perfecta ni una latencia constante con cualquier voz y ruido.

La cabecera resume los estados como Conectando, Enlace activo, Escucha, Recibiendo o Voz. La señal del micrófono aparece integrada a la izquierda de la entrada, sin una fila de controles adicional. El perfil inicial es **Whisper base · español y nombres en inglés**. Vosk sigue detectando la palabra de activación, y Whisper transcribe la petición completa. La selección de otro perfil en Ajustes se conserva si decides cambiarla.

## Tamaño, tipografía e intro

Usa **Ctrl + rueda** sobre Capri, **clic derecho → Tamaño de Capri**, o el control en Ajustes para cambiar entre 75% y 160%. El tamaño se guarda; las imágenes se recalculan solo al cambiarlo. La fuente Chakra Petch se incluye con su licencia OFL y se carga de forma privada dentro del proceso de Capri, sin instalarla para otros programas.

Al abrir se reproduce una intro visual con Capri sujetando la pantalla y el saludo «¡Hola! / Capricorn Desktop». Después se transforma en el visor del escritorio. Escape, F8, enviar una petición o detectar el nombre la interrumpen. Puedes desactivarla en **Intro visual al abrir Capri**. El saludo es mudo.

## Actualización de expresiones e interfaz

La boca normal se retira antes de aplicar la expresión de habla o sonrisa. Los emojis permanecen en el chat, pero no se envían a la voz. El diálogo compacto muestra hasta seis líneas recientes de respuesta y una línea de pregunta; el historial conserva el texto completo.


En **Ajustes → Voz** puedes elegir el perfil, el volumen y la velocidad de la voz de Capri. La selección se conserva al actualizar. Las voces naturales son sintéticas y requieren internet.


Ajustes se organiza en Escritorio, Micrófono, Voz, IA y servicios, y Permisos. Las opciones se guardan al cambiarlas. Aspecto abre una galería para elegir la apariencia de Capri.

Con los viajes activados, Capri se teletransporta a distintas posiciones del escritorio y puede preferir el borde de una ventana cercana. Si queda en el aire, cae lentamente y a veces clava un anclaje temporal para sujetarse. El anclaje desaparece al viajar. Arrastrarla permite elegir el punto inicial sin bloquear sus viajes posteriores. Pausar viajes detiene tambien la caida y las sujeciones nuevas.


Diseño rojo y controles: Ajustes, Aspectos y Conversación usan marcos angulares propios y permanecen por encima de las ventanas normales. Arrastra su barra superior para moverlos y la marca inferior derecha para ajustar el tamaño. Las tarjetas de Aspectos muestran la vista seleccionada. El panel y la entrada indican DI CAPRI; la activación por nombre se puede desactivar en Micrófono. En Ajustes > Voz > Tecla para hablar, pulsa CAMBIAR y presiona la tecla o combinación deseada (por ejemplo, Ctrl+Espacio); Esc cancela. F8 es el valor predeterminado. El cambio se aplica sin reiniciar. Si otra aplicación ocupa la tecla se informa para elegir otra. El menú Voz conserva Hablar y Activar/Silenciar.

La rueda desplaza la sección de ajustes incluso sobre selectores o deslizadores, sin modificar sus valores. Los selectores se abren con un clic y las barras de desplazamiento solo aparecen cuando el contenido no cabe. Permisos reúne la información y su interruptor al principio de la sección. Ambos modos de Capri comparten el menú radial al hacer clic derecho. Las transformaciones mantienen la paleta roja del panel.

En **Ajustes > Voz > Idioma de Capri** puedes elegir español, inglés, portugués de Brasil o japonés. Se aplica a menús, ajustes, ayudas, estados, campos y a las siguientes respuestas escritas y habladas. La interfaz se traduce con un catálogo incluido, sin esperar una petición al modelo. No traduce retroactivamente los mensajes del historial ni cambia el modelo, micrófono o reconocimiento de voz. Las voces naturales son Aria para inglés, Francisca para portugués y Nanami para japonés; al volver al español recuperas tu perfil guardado. Sin voz natural se necesita una voz de Windows instalada en ese idioma.

Las conversaciones y la traducción de resultados detallados utilizan Ollama local. Los saludos y avisos comunes tienen traducciones incluidas. Si la IA no puede traducir un resultado, Capri lo indica en el idioma elegido y conserva el resultado original para no ocultar un fallo ni inventar una ejecución. Las rutas, URL y títulos entre comillas se conservan literalmente, incluyendo las frases exactas de confirmación de operaciones.

El chat muestra el historial y la entrada en marcos de transmisión, con tipografía de lectura y soporte para japonés. Las ventanas auxiliares dejan un margen inicial de 32 píxeles respecto del área de trabajo; puedes seguir moviéndolas con su barra superior.

Los selectores muestran todas las opciones de las listas cortas, empezando por la primera aunque esté seleccionada otra. Sus filas se pueden elegir con el ratón o las flechas y Enter; Esc cierra sin cambiar. La rueda sobre el selector cerrado desplaza la sección, sin alterar la selección. El umbral automático oculta el deslizador manual; al desactivarlo aparece el control en la misma tarjeta. La entrada del chat indica «Escribe un mensaje…» cuando está vacía: esa indicación no forma parte del texto enviado.

Los indicadores de escucha, procesamiento y voz también siguen el idioma elegido. Los marcadores internos del traductor se validan antes de mostrar o narrar el resultado. El campo y su título respetan el ancho disponible, y el globo del personaje reserva espacio debajo de la última línea. Al sujetarse, Capri levanta el brazo hacia una estaca: se ve la inserción, el impacto, los dedos sobre el mango y el balanceo del cuerpo. El anclaje desaparece al trasladarse o al arrastrarla.

El campo del historial mantiene corchetes laterales tanto vacío como al escribir; enfocarlo no dibuja un rectángulo completo. Las etiquetas del menú se ajustan a su sector según el idioma. Mientras se prepara la voz, el globo muestra puntos de espera y actualiza sus indicadores al cambiar de idioma.

La caida empieza al soltar al personaje, con gravedad de 900 px/s2 y velocidad maxima700 px/s a escala1. Una estaca puede clavarse con un golpe visible, fijar un punto de agarre y dejar el cuerpo balanceandose unos segundos. Al teletransportarse o arrastrarlo se retira. La sombra elegida acompana la formacion y los saltos.

Al soltar a Capri, una entrada oculta no mantiene la física en pausa: no hace falta hacer clic después en el escritorio. La escritura sí pausa el movimiento mientras su campo está visible y tiene el foco.

La conversación refuerza el idioma seleccionado aunque el historial esté en otro idioma. Si detecta una respuesta claramente desviada, la corrige antes de mostrarla o narrarla; esto puede añadir espera. El cambio de voz y el idioma del contenido se comprueban por separado. Los nombres de canciones, programas y archivos conservan su escritura.

El guardado de una opcion no sustituye las otras claves del archivo de preferencias. Las actualizaciones conservan el microfono, LLM, motor y modelo Whisper seleccionados. Se mantienen los valores predeterminados para opciones no elegidas; Whisper Base se indica para priorizar velocidad, Small para precision. Emma multilingue se ofrece como voz alternativa que puede leer espanol, sin sustituir la actual y sin presentarla como la voz original de Capri.

## Panel multimedia

Activa **Ajustes → Multimedia → Mostrar panel multimedia**. Es opcional y está desactivado por defecto.

- **Modo pantalla:** reproductor flotante independiente. Arrástralo por el fondo para colocarlo donde prefieras; su posición queda guardada. Durante la reproducción, Capri sujeta los audífonos con ambas manos y muestra su guiño característico dentro del visor. Al pausar, detener o cerrar la sesión vuelve a su imagen habitual sin audífonos. Mientras habla o te escucha también usa su expresión habitual.
- **Modo personaje:** Capri y el reproductor son ventanas separadas. Puedes arrastrar a Capri cerca del borde superior para que se siente; al moverla fuera vuelve a ser independiente. Con el paseo activado también puede subirse sola. Permanece en el borde y sigue al panel si lo mueves. Durante la reproducción se balancea suavemente y aparecen notas musicales, sin audífonos; al pausar se queda quieta.

Puedes desactivar **Animar a Capri mientras escucha música** o las animaciones generales. En el visor cabecea, acompaña con los hombros y el pelo se mueve con un ligero retraso. El cabeceo y las barras son una animación visual asociada a la reproducción, sin análisis del audio ni cálculo de BPM.

La pose de escucha del visor conserva el grano, el barrido y las interferencias de la cámara habitual. La cámara queda fija mientras se mueve Capri, para que el barrido y la estática mantengan su definición. El tono rosa del cabello se ajusta al rojo de la ilustración habitual. Los cortes de señal respetan **Efecto glitch** y las animaciones generales. El bucle corporal se prepara en segundo plano y se presenta a 30 fotogramas por segundo; durante la preparación inicial se mantiene la pose quieta.

La tarjeta muestra miniatura o carátula, título grande, artista/canal, progreso y controles anterior/pausa/reanudar/siguiente. Play/pausa cambia de aspecto al pulsarlo y confirma después el resultado con Windows; si el control falla, recupera el estado real. Pulsar la barra de progreso cambia de posición si el reproductor lo permite. Los títulos y artistas conservan su idioma original. La cruz cierra el reproductor y desactiva la opción.

En **Fuente preferida** elige Automático, Spotify o Navegador. **Automático** prioriza lo que está reproduciéndose: si empieza otra fuente mientras la primera sigue sonando, conserva la primera. Al pausarla, detenerla o cerrarla pasa a la otra que esté sonando. El orden se registra mientras Capri está consultando las sesiones; si ambas ya sonaban antes de abrirla, Windows no informa cuál empezó primero y se mantiene la primera detectada. Esto elige qué muestra y controla el panel, sin iniciar ni detener música por sí solo.

Con Spotify o Navegador puedes pulsar el nombre de la aplicación o el botón inferior izquierdo para cambiar entre sesiones compatibles; en Automático esa selección está disponible cuando ninguna está reproduciéndose. Una lectura ausente se tolera brevemente para evitar que desaparezcan los datos durante un cambio de pista; mientras no se confirma la sesión, sus controles quedan desactivados. Los botones actúan sobre la sesión y pista mostradas; si cambia justo al pulsar, actualiza la información y vuelve a intentarlo.

Inicia una canción en Spotify o un vídeo en el navegador para que aparezca su sesión; después puede permanecer pausado. YouTube se identifica con el nombre del navegador. Cada reproductor decide qué información y botones comparte con Windows: algunas sesiones no ofrecen carátula, duración o saltos. Requiere Windows 10 versión 1809 o posterior, sin herramientas adicionales. Los datos y las imágenes se mantienen en memoria. Ocultar Capri pausa las consultas; la apertura y las transformaciones conservan la presentación correspondiente a cada modo.

## Monitor del computador

El monitor es opcional y viene **desactivado por defecto**. Actívalo en **Ajustes → Escritorio → Monitor del computador**, con el interruptor **Mostrar recursos del computador**. La elección queda guardada; puedes desactivarlo desde ese mismo interruptor.

En modo pantalla aparece una franja de iconos entre el visor y la barra donde se escribe, del ancho del visor e integrada en la misma ventana de Capri: CPU, RAM, GPU y VRAM utilizada. El visor, los recursos y la barra de escritura comparten un chasis continuo, con bordes, fondo y colores coordinados. Al mover Capri, los iconos se desplazan con ella. Al desactivar el monitor se recupera el diseño habitual del visor y la entrada. Las barras indican la carga de CPU/RAM/GPU; al dejar el puntero sobre un icono aparecen los detalles, incluida la RAM usada/total y la memoria gráfica compartida, separada de la VRAM dedicada. La lectura de GPU corresponde al motor más ocupado y la memoria gráfica se suma entre adaptadores.

Los datos se actualizan cada dos segundos, sin instalar herramientas adicionales. La primera lectura de CPU/GPU necesita un intervalo de muestreo; los datos ausentes se muestran con una raya. La apertura y las transformaciones entre pantalla y personaje incluyen el monitor dentro del mismo panel animado cuando está activado. Durante el viaje se utiliza una instantánea de las métricas; al terminar se recupera el panel completo sin esperar otra actualización. Ocultar Capri o usar el modo personaje pausa las consultas; al preparar el regreso al modo pantalla se reanudan en segundo plano.
