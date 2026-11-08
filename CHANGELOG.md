# Cambios

## En desarrollo

### Reacciones a skins

- Función en desarrollo: quedan pendientes reducir la demora, corregir fallos intermitentes de identificación y activar el comentario a partir de una nueva selección real del usuario. La lectura de fichas de Valorant aún requiere validación con el cliente real.
- Ampliado el catálogo a 4292 skins (2880 atuendos de Fortnite y 1412 skins de Valorant), incluido Goku Black. Opiniones genéricas positivas, neutrales o negativas para las que no tienen diálogo propio, fijas por identidad incluso entre idiomas/reinicios; los reencuentros conservan el mismo gusto.
- Corregida también la detección de la ficha cuando Windows separa «A TUENDO»: la lectura ampliada elige el nombre junto a Estilo en lugar de la pestaña de atuendos. Comprobado con Fry en el juego abierto.
- Reconoce «¿qué te parece esta skin?» y prioriza el juego activo. La reacción observa una ficha estable, con intervalos menores y sin repetir continuamente la misma. El probador incluye ejemplos de los tres gustos.
- En Valorant la ficha visible de colección/tienda tiene prioridad sobre otras armas equipadas. La pregunta manual pide aclarar una ficha ambigua y no elige otra arma al azar. OCR local sin controles de juego; lectura de equipamiento como alternativa fuera de partida.
- Corregido «Mirar mi skin ahora» en la selección de atuendos de Fortnite: si el OCR general corta el nombre, vuelve a leer su zona ampliada en color y con contraste, junto al rótulo de atuendo. Compatible con fichas a izquierda/derecha, sin aceptar fragmentos insuficientes. Los errores de foco se muestran con su causa real.
- Capri comenta skins con gustos propios, afinidad por neón/Night City y frases especiales para 18 colecciones de Valorant y 23 personajes de Fortnite. Variantes reconocidas por identificador y diálogos originales en español, con alternativas en inglés, portugués y japonés.
- Ajustes → Reacciones incorpora activación opcional por juego, tres frecuencias y un probador de personalidad. La petición «mira mi skin» comprueba la fuente real; el ejemplo de Ajustes no consulta el juego.
- En Valorant se lee únicamente el equipamiento propio fuera de partida/selección. Fortnite reconoce nombres en fichas de atuendos, con anclas de contexto y tolerancia acotada a errores del OCR. Dos observaciones deben coincidir; comentarios caducables, sin repetir la misma skin continuamente ni interrumpir conversaciones. Observar no restaura ventanas ni cambia equipamiento, compras o colas.
- Catálogo público incluido en el paquete, sin descargas nuevas ni envío de capturas. Preferencias locales y memoria de reencuentros solo durante la sesión. Fortnite comprobado con Fry en el cliente real, incluida la generación automática del evento; Valorant y casos de rechazo comprobados con cliente simulado.

### Fortnite

- Las órdenes recuperan Fortnite desde minimizado: restauración asíncrona y espera de ventana, foco, imagen y controles del lobby. Las lecturas de transición no ejecutan clics ni reinician la búsqueda. Si se dejó abierto el menú de opciones, vuelve primero al lobby.
- Panel propio con Battle Royale/Cero construcción y Solo/Dúo/Trío/Squad. Las preferencias son locales; se puede conservar el modo/equipo del juego. Abrir o configurar no inicia ninguna búsqueda.
- Acciones de aplicar opciones, buscar y cancelar mediante lectura local del lobby con OCR de Windows. Verificación antes de pulsar Jugar; sin reencolado, capturas permanentes ni programas adicionales. No se pulsan clasificatoria/rellenar equipo. Modos y los cuatro tamaños probados en el cliente real sin entrar en cola; confirmación de búsqueda/cancelación comprobada con un cliente simulado.
- Órdenes por texto/voz, selección de Fortnite como juego y detección en primer plano para órdenes de voz en Automático. Guía `FORTNITE.md` incluida en el paquete.

### Apertura en modo personaje

- El saludo se retira en su posición y el propio sprite aparece y se traslada a su destino, sin dos Capris superpuestas ni líneas de estela. El trayecto dura 1,5 segundos y usa fotogramas preparados durante el saludo.
- La llegada conserva pose, tamaño, dirección y posición del personaje activo. No se reinicia su colocación ni se dispara un glitch al finalizar la intro.

### Panel multimedia

- Cabeceo y movimiento independiente de hombros y cabello en el visor, con cámara fija. Bucle de 72 fotogramas a 30 fps preparado fuera del hilo de la interfaz, cachés acotadas y pausa al desactivar la opción. El rojo del cabello se aproxima al arte habitual sin alterar ojos, piel verde o ropa; estática y barrido se aplican después del movimiento para conservar su definición.
- Pose de escucha revisada con referencias originales de Capri: cara y manos geométricas, cabello rosa amplio y audífonos oscuros. Conserva el mismo procesamiento de cámara, grano, señal animada y cortes de interferencia del visor habitual.
- Nueva ilustración de escucha para el visor: ojo azul y guiño característicos, máscara inclinada y manos sujetando audífonos, solo durante reproducción activa. Reemplaza los audífonos vectoriales anteriores; pausa, parada y ausencia de sesión recuperan el arte habitual, también en las transformaciones.
- Reproductor flotante cyberpunk en Ajustes → Multimedia: miniatura, título grande, progreso con posición seleccionable y controles. Posición independiente guardada en ambos modos; Capri puede sentarse sobre su borde durante sus paseos o al arrastrarla, sin unir ambas ventanas ni añadir audífonos al personaje.
- Play/pausa con respuesta visual inmediata y confirmación posterior; las órdenes se procesan antes de leer carátulas. Compatibilidad con el control alterno de Windows y carátulas WinRT redimensionadas, incluso con imágenes de origen mayores de 1 MB.
- El reproductor conserva su posición, controles y consultas durante los teletransportes y cambios de modo de Capri.
- Sesiones de Spotify y de navegadores mediante Windows, sin cuentas adicionales ni extensiones nuevas. Automático conserva la primera fuente detectada reproduciendo hasta que se pausa, detiene o cierra; Spotify y Navegador permiten elegir sesiones manualmente.
- Las ausencias breves de metadatos conservan la tarjeta y su progreso, con controles desactivados hasta confirmar la sesión. Referencias de imágenes conservadas durante el reemplazo para evitar desapariciones al renovar la caché.
- Controles ligados a la sesión y pista mostradas, comprobación de capacidades y estado pendiente; no se reintentan órdenes con resultado incierto. Datos ausentes y sesiones cerradas desactivan los controles.
- Ayudante persistente solo mientras el reproductor se utiliza, miniaturas acotadas en memoria y presentación adaptada a la apertura y transformaciones. Sprites y tarjetas se reutilizan durante la animación; se mantiene el arte existente de Capri. Los nombres de canciones y artistas conservan su idioma original.

### Monitor del computador

- Diseño unificado del visor, los recursos y la escritura: chasis continuo y misma paleta, sin tres tarjetas separadas. Al desactivar el monitor se conserva el aspecto habitual.

- Monitor opcional, desactivado por defecto: franja de iconos vectoriales entre el visor y la barra de escritura, del ancho del visor, CPU/RAM/GPU con barras y VRAM utilizada. Detalles al pasar el puntero. Integrado en la misma ventana para moverse junto a Capri sin temporizador de seguimiento. Actualización de datos cada dos segundos y pausa al ocultar Capri o cambiar al modo personaje.
- Lectura mediante APIs de Windows, sin programas adicionales. Las métricas de GPU dependen del controlador; los datos ausentes se indican como tales. La GPU muestra el motor más ocupado y las memorias gráficas se suman entre adaptadores.
- Se puede arrastrar junto al visor y activar/desactivar desde Ajustes → Escritorio → Monitor del computador, conservando la preferencia. Se integra en la apertura y en las transformaciones mediante una instantánea del mismo diseño; el panel vivo se restaura al terminar, sin aparición tardía. La despedida conserva su animación propia.

### Valorant

- Protección de la presentación del mapa antes de elegir agente: mapa identificado, selección activa con tiempo restante y jugador incorporado, más seis segundos de seguridad. Revalida antes de seleccionar y confirmar; reinicia la espera al cambiar de mapa o perder la preparación.
- Conexión corregida cuando Riot informa `Idle` con Valorant ejecutándose: comprobación adicional del proceso del juego y cabecera de identificación propia `CapriDesktop` en las peticiones remotas. Verificada la lectura de una sala real sin iniciar cola ni seleccionar agentes.
- Reconocimiento de «tira partida», «inicia la búsqueda», «ponme en cola» y otras variantes dirigidas a Valorant, evitando que se envíen al chat, a búsquedas web o a Spotify. Las órdenes reconocidas informan el resultado del controlador sin depender de visión de pantalla.
- Al mostrar o minimizar Capri se cierran los desplegables temporales para evitar que retengan los clics. Recuperar una ventana visible ya no vuelve a configurar el marco de la ventana principal.
- Selector de juego en el chat y contexto guardado al abrir los paneles: buscar o cancelar en Valorant sin depender de que el juego tenga el foco, por texto y voz.
- Ctrl+Alt+C para recuperar solo el avatar, sin abrir ni enfocar el chat. Ocultar Capri conserva los marcos de sus ventanas y deja chat y paneles ocultos hasta que el usuario los abra; mantiene voz y automatizaciones. El panel de LoL conserva su prioridad de ventana para no quedar detrás del chat.

- Buscador con lupa, indicación interior y limpieza integrada; retirados los avisos de marca de los paneles de juego, con los créditos conservados en la documentación.
- Órdenes de voz genéricas dirigidas a Valorant cuando está en primer plano, conservando los destinos explícitos. La activación por nombre continúa aunque Ajustes esté abierto detrás del juego, sin traer Capri al frente.

- Panel con tres preferencias de agente, retratos incluidos, buscador y guardado automático. Búsqueda y cancelación desde el panel o por órdenes directas, con los ajustes de sala del juego.
- Selección y confirmación opcionales: respeta elecciones manuales y agentes señalados por aliados, pasa a la siguiente preferencia y no elige fuera de la lista. Cancelar la búsqueda no desactiva las preferencias ni inicia otra cola.
- LoL continúa con la siguiente prioridad si la primera confirmación fue rechazada y el cliente confirma después que el campeón ya fue elegido. Pruebas de prioridades agotadas en ambos juegos.

### League of Legends

- Corregida la detección de campeones baneables cuando LoL devuelve solo `[-1]`: consulta de respaldo a sus fichas, sin cambiar los picks ni ignorar campeones deshabilitados, seleccionados, baneados o señalados por aliados.

- Nuevo panel de perfiles por línea con tres picks y tres baneos priorizados, selector con retratos y búsqueda, guardado automático y catálogo local de Data Dragon.
- Búsqueda, cancelación, aceptación y aceptación automática reunidas en el panel. Confirmación opcional de picks y baneos exclusivamente durante el turno local y según la línea asignada, respetando selecciones manuales y hovers aliados. Cancelar no reinicia la cola.

### Presentación e interfaz pública

- Instalación documentada para principiantes: instalador tradicional de Python 3.12, comprobación de versión, extracción del ZIP, comandos separados y actualización desde `main`. Nueva guía para errores de preparación y registros, incluida la redirección de Microsoft Store.

- README renovado con la intro actual, controles reales de YouTube y Spotify, vigilancia de partidas de LoL, galería de aspectos y despedida con efecto de cámara. Medios WebP y procedencia de las capturas documentada.
- Retirados de los menús y ajustes los controles de simulación de llamadas y asomos, la vista previa del apagado y las pruebas de voz y grabación. Las interacciones automáticas y sus preferencias siguen disponibles.
- El micrófono conserva la selección de entrada y la sensibilidad automática o manual en un panel dedicado, sin controles de grabación o reproducción de prueba. Guías y traducciones actualizadas.

### Corregido

- Restaurada la voz habitual de Capri al cerrar, con «Cuídate mucho, choom» y sin el tratamiento grave de grabación ni sustitución del nombre.
- Despedida con cuatro gestos: mirada suave, sonrisa, boca al hablar y sonrisa final conservada antes de la mano. Asomo con pelo en bloques grandes, ojos asimétricos y núcleos blancos sin pupilas añadidas.

- Despedida con fondo de cielo nocturno y siluetas oscuras, más detalle, colores lavados y grano de cámara animado. «Cuídate mucho» admite nombre opcional en Ajustes → Escritorio.
- Interpretación de despedida más baja y pausada, con caída del remate y tratamiento de grabación ya incluido en la caché; conserva las pausas del nombre sin alterar la voz normal.

- Capri viaja al centro con su descarga y teselas antes de la despedida; la voz espera hasta llegar. El plano se presenta como reproducción de cámara 4:3 y después forma la mano.
- Nuevas ilustraciones de asomo tierno y despedida basadas en fotogramas de la serie: cara inferior negra, franja verde, cabello asimétrico y boca fina sin dientes. Interpretación temporal más suave con la base sintética de Roman.

- El rostro inicial de despedida recupera la opacidad de la ventana desde su primer fotograma; antes quedaba transparente hasta empezar la mano.

- El cuadro de subtítulos de las llamadas crece con las líneas que se van pronunciando, sin reservar al inicio el espacio del guion completo.

- Despedida con retrato de Capri sonriente y ojos cerrados, frase localizada antes de la mano y la estrella y ritmo suavizado sin cambiar preferencias.
- Asomo recortado y pegado a un lateral o abajo; permanece al hacer clic y se desprende al arrastrar, con ojos transformados según el borde.
- Subtítulos invitados dentro del aviso telefónico, sin atribuir su diálogo al personaje de Capri. Perfiles invitados independientes de la opción de voz natural y sin sustitución silenciosa por Windows.
- Comentario de Capri preparado desde el aviso entrante para reducir la espera al colgar.

- Se invierte la pose sentada tras la corrección visual del usuario: original en el borde derecho y espejo en el izquierdo, incluida la llegada por traslado.
- Avisos y globos de llamada con estilo Windows sin activación; las llamadas se aplazan durante juegos o pantalla completa para evitar sacar el primer plano.
- Teléfono entrante centrado con sus ondas y módulo CALL con biseles superiores simétricos y trazos interiores dentro del borde.
- La pose sentada mira hacia fuera en cada esquina, también al llegar por traslado y al apoyarse durante la caída.
- Las llamadas pausan saltos pendientes, el regreso de los asomos y los saltos para seguir ventanas; su mensaje ya no reaparece al terminar un traslado en modo personaje.
- Al terminar una llamada se oculta también su mensaje y se cancela su temporizador, sin ocultar respuestas posteriores.
- La llamada se cierra al recibir el fin de reproducción de su voz, sin esperar doce segundos. Colgar también cancela la síntesis o reproducción pendiente y evita mensajes tardíos.
- Bordes de llamada sin el acento inferior izquierdo suelto, recorte izquierdo en el módulo CALL y arista inferior del globo alineada con sus biseles.
- Variantes equivalentes como «Capri mutéame el Discord», «mutéame del Discord» y «me puedes mutear en Discord» reconocen el mismo control propio, sin ampliar la orden a otras personas o aplicaciones.
- El apagado dibuja directamente en Canvas, sin ampliar un bitmap a pantalla completa en cada fotograma. Limita la frecuencia y cede tiempo a Escape y a Windows.
- Discord admite el patrón de conmutador de sus botones de silencio/ensordecimiento y verifica el estado aunque la etiqueta no cambie.
- Vista previa del apagado en ventana sobre Ajustes, con imagen ligada al lienzo correcto, cierre y reinicio; los fallos de render cancelan el apagado.
- Voz brasileña con espera adaptada y respaldo brasileño de síntesis; no queda bloqueada durante 45 segundos tras un fallo aislado.
- El puente de Opera 1.0.4 selecciona resultados de YouTube sin necesitar un vídeo ya cargado. La orden por número deja de depender exclusivamente de accesibilidad de Windows.
- Aclaraciones como «de la playlist Capri» extraen «Capri» y conservan la canción pendiente, en lugar de buscar una lista con toda la frase como nombre.
- Destinos explícitos Spotify/YouTube prioritarios, selección de resultados de YouTube por número y alcance de playlist conservado aunque falte su nombre.
- Escribir deja de recuperar el globo anterior; abandonar el campo cancela la composición sin perder el borrador ni ocultar respuestas nuevas.
- La aceptación automática puede vigilar también colas iniciadas directamente en LoL. La opción guardada se recupera al iniciar Capri, se reconecta al cliente y sigue disponible entre partidas, con estado visible en ajustes.
- El globo sigue cada movimiento de Capri sin esperar al temporizador de texto. Escribir alterna su apertura y cierre; el borde inferior encaja en el marco.
- Separación medida entre iconos y etiquetas del menú radial, también en portugués y japonés.
- El foco de un campo oculto ya no mantiene al personaje suspendido al soltarlo. Escribir en un campo visible con foco sigue pausando el movimiento.
- Las respuestas que se desvían claramente del idioma elegido se corrigen antes de narrarlas. Los mensajes extranjeros en el historial no cambian la selección actual.

### Mejorado

- Roman pasa a una base latina juvenil y D a una voz mexicana; King conserva su voz. Las reacciones se sintetizan mientras habla el invitado y se reutilizan al cortar, evitando otra espera de red en el remate.
- Capri puede sentarse sobre sus propias ventanas de Ajustes, Aspectos y Conversación, mediante un registro de superficies independiente del idioma.
- Glitch durante el arrastre manual de pantalla o personaje, respetando las opciones de animación e interferencias.
- Paleta carmesí para la llamada entrante, sin botón crema ni tonos dorados, y vibración breve del auricular sin mover los botones.
- Llamadas con 24 bromas completas y absurdas en lugar de preguntas o propuestas de descanso; asomos y minimizaciones también tienen remates propios. Seis bromas incluyen voz temporal de ardilla, villana o robot, con sincronía ajustada a la duración del efecto y sin modificar preferencias.
- Llamada con tres esquinas recortadas, auricular diagonal y colores diferenciados: nombre blanco, aviso ámbar y conexión verde suave, con módulo de señal animado al contestar.
- Glitch del personaje con seis variantes de franjas desplazadas, cortes y separación violeta/verde, también al sentarse o sujetarse. Modo pantalla con suavidad de cámara, grano animado, barrido y viñeta.
- Apagado sin retrato, con circuitos, interferencia y cierre CRT a pantalla completa; conserva Esc para salir antes de enviar la orden a Windows.
- Llamada arriba a la izquierda, marco simétrico, auricular nuevo y estado conectado compacto inspirado en el indicador CALL.
- Más simplificado: se retiran Escribir, Repetir intro y Pausar viajes de ese submenú.
- Entrada con revelado progresivo, indicadores en la paleta roja y rostro despejado durante la secuencia.

### Añadido

- Simular asomo en Escritorio, Más y Juegos, sin cambiar el modo guardado.
- Despedida hablada «Nos vemos, choom» con la mano formada; el viaje a la estrella espera al fin de la voz y conserva su dibujo original.
- Llamadas ficticias de King, D, Roman y Talia, con perfiles de voz sintéticos, nombres propios, ocho guiones y una reacción contextual de Capri al terminar.
- Nueva forma curiosa de asomo automático en ambos modos, con seguimiento del cursor y parpadeo; conserva la forma y configuración anteriores. Se retira el botón Probar asomo.
- Tono breve de desconexión al colgar una llamada contestada, respetando volumen y silencio; no altera el estado de narración ni su generación.
- Voz telefónica durante llamadas, breve sonido de conexión y cuatro saludos localizados. El filtro es temporal y conserva la voz/acento elegidos. Las ondas siguen el audio reproducido, con posición real del reproductor y reposo en los silencios; el aviso espera durante la preparación y reproducción.
- Llamadas espontáneas con 24 diálogos seleccionados sin repeticiones hasta agotar la lista, respuesta hablada al contestar y simulación desde Ajustes → Escritorio → Monitor del computador. Intervalo inicial de 15 minutos con variación aleatoria y configurable.
- Botón Probar asomo desde Escritorio o Juegos; muestra el movimiento sin activar el juego automático.
- Asomos automáticos y bromas de minimización activables por separado. La ventana se puede restaurar desde la llamada y se recupera al terminar el aviso. Se retiran Atrápame y las aperturas aleatorias de pestañas/Documentos.
- Apagado confirmado con secuencia roja de interferencia y cierre CRT, cancelación con Esc y vista previa sin apagar.
- Apertura y controles propios de Discord de escritorio: micrófono, ensordecimiento y solicitud de entrada a canal de voz.
- Voz/acento independiente del idioma, conservado entre cambios de idioma; opciones multilingües Thalita y Emma.
- Tabla de componentes orientativos mínimos/recomendados y dependencias de rendimiento en el README.
- Búsqueda, cancelación y aceptación de cola en el cliente local de LoL. Menú y órdenes en cuatro idiomas; aceptación automática opcional para las búsquedas iniciadas con Capri.
- Se conserva la despedida anterior: mano roja, traslado eléctrico hacia la estrella y apagado gradual.
- README con instalación, ejemplos, idiomas y límites de las integraciones; índice de documentación, mapa de módulos y plantillas para reportes y propuestas.

### Incorporado desde 0.1.0

- Modo personaje, anclajes, menú radial y ajustes con marcos propios.
- Interfaz, respuestas y voces en español, inglés, portugués de Brasil y japonés.
- Selector de modelos y micrófonos, tecla para hablar configurable y controles del reproductor.
- Recursos de mayor resolución y nuevas transiciones.

## 0.1.0

Primera versión preparada para distribución general en Windows.

- Chat con Ollama y reconocimiento local Whisper/Vosk.
- Activación por nombre, F8 y botón Hablar, con captura continua de la orden.
- Interrupción de voz y respuestas pendientes.
- Pestañas y búsquedas en Opera, aplicaciones registradas y carpetas de Windows.
- Controles de la sesión actual de Spotify y vinculación de playlists.
- Interfaz flotante e icono de Capri.
- Valores predeterminados genéricos, sin nombre personal del interlocutor.
- Código, pruebas, instalador y documentación en carpetas separadas.
- Pruebas automatizadas en Windows y empaquetado de versiones mediante GitHub Actions.

### Limitaciones

- Requiere Python 3.12; no es un ejecutable autónomo.
- La exactitud del reconocimiento depende del micrófono, el ruido y el equipo.
- La voz natural usa un servicio externo y no reproduce la voz exacta de la actriz.
- La activación por nombre se pausa mientras la aplicación habla.
- Las integraciones de Spotify dependen de la sesión y los controles que exponga la aplicación; no se garantiza toda versión o estado de interfaz.
- Aquella versión no incluía el modo personaje ni las expresiones de boca incorporadas después en desarrollo.
