# Capri y las skins

**Ajustes → Juegos → Fortnite/Valorant → Skins** reúne la activación y frecuencia propias de ese juego y un
probador de personalidad. El probador permite escuchar comentarios sin abrir el
juego ni modificar el equipamiento. Las reacciones automáticas son opcionales;
una instalación nueva empieza con ellas desactivadas.

## Estado actual

La detección ahora compara selecciones: toma la primera ficha como referencia y
comenta cuando cambia el nombre reconocido o el equipamiento, tras dos lecturas
coincidentes. Si primero observa el menú sin ficha, puede comentar la primera
selección posterior. No registra clics globales ni deduce una selección solo por
el movimiento del ratón. Un comentario pendiente se descarta si la selección cambia.

El motor OCR local se mantiene preparado y reutiliza lecturas de una interfaz sin
cambios. Las ampliaciones se reconocen juntas y conservan el contexto de la ficha;
también se admite el rótulo y el nombre en una misma línea. En una captura guardada
del casillero con Fry se verificó el reconocimiento, con unos 1,1 segundos en frío
y 0,05 segundos al repetirla sin cambios en el equipo de desarrollo. No son tiempos
garantizados de voz o de partida. La selección real de Fortnite y Valorant requiere
comprobarse en los clientes; no se iniciaron partidas para estas pruebas.

## Personalidad y catálogo

Capri tiene afinidad por el neón y la tecnología: RGX, Glitchpop, Protocol, Origen
y personajes relacionados con Night City. También tiene comentarios propios para
Kuronami, Oni, Reaver, Prime, Gaia, Elderflame, Evori y otras colecciones. En
Fortnite puede comentar personajes como V, Johnny Silverhand, Lucyna Kushinada,
Fry, Leela, Bender, Banano, Midas o Cuervo. El catálogo incluido contiene 4292 skins
(1412 de Valorant y 2880 atuendos de Fortnite), incluido Goku Black. Las que no
tienen un diálogo propio reciben comentarios genéricos: le gusta, le resulta
indiferente o no es de sus favoritas. Son gustos ficticios del personaje,
asignados de forma estable por identidad; no una evaluación visual ni una
clasificación de calidad. Las variantes y nombres en otros idiomas conservan
el mismo gusto, también después de reiniciar. Las frases propias ya existentes
conservan su aprobación. Los diálogos son originales y no
afirman que una skin mejore la puntería o dé ventajas.

## Cuándo reacciona

- **Valorant:** fuera de partida y selección de agentes, da prioridad al nombre
  visible de la ficha que inspeccionas en colección/tienda. Si no estás en una
  ficha, consulta el equipamiento propio y comenta cambios de identificador,
  nivel o variante. Una pregunta manual ambigua con varias armas equipadas pide
  abrir la ficha, en lugar de elegir otra al azar. No afirma que estés sosteniendo
  el arma en ese instante. La observación automática requiere Valorant activo.
- **Fortnite:** reconoce el nombre visible de un atuendo en su ficha del casillero
  o la tienda. Requiere indicaciones de atuendo y de equipar/estilos/vista previa.
  Una cuadrícula ambigua con varias skins se descarta. No adivina la identidad por
  la silueta del personaje ni ve skins que no muestran su nombre.

Para activarlo, abre **Ajustes → Juegos → Fortnite/Valorant → Skins**, activa **Reaccionar a las skins** para ese juego. Luego selecciona otra skin y deja visible su ficha con el
nombre: no hace falta pulsar el botón ni pedirlo por voz. En Valorant
también puede detectar el cambio al equiparla. Solo navegar por miniaturas sin
nombre legible no basta.

Dos observaciones consecutivas deben coincidir antes de una reacción automática.
El trabajador comprueba aproximadamente cada cuarto de segundo; el OCR puede
tardar más según el equipo. La frecuencia establece una separación mínima de
8, 3 o 1,5 segundos (Discreta, Equilibrada, Entusiasta), para no hablar mientras
pasas rápidamente por varias skins. Ya no hay una espera de minutos por skin.
La misma selección continua no se repite. Se alternan las frases y los
reencuentros mantienen el mismo gusto, también si no le gustaba esa skin.

Capri espera para comentar mientras habla, escucha, responde, estás escribiendo o
tienes Ajustes abiertos. Puede seguir observando durante su narración para descartar
comentarios pendientes de una selección anterior. Los comentarios caducan; una reacción atrasada no se narra tras
cambiar de juego. La observación no restaura ventanas ni roba el foco. Los
comentarios van por el diálogo y la voz habituales de Capri.

También puedes pedir **«mira mi skin en Valorant»**, **«mira mi skin en Fortnite»**
o **«¿qué te parece esta skin?»**. Si omites el juego, prioriza el que tengas
activo sobre el juego guardado para buscar partidas. Deja visible la ficha con
el nombre. La petición manual puede recuperar su ventana y cierra Ajustes si
estaba abierto para que no tape la ficha; no selecciona ni equipa otro atuendo.
Si la tipografía inclinada o el modelo del personaje dificultan leer el nombre,
Capri realiza una segunda lectura ampliada de la zona de la ficha, en color y
con contraste. El rótulo de atuendo y el nombre deben seguir siendo reconocibles;
un fragmento como «PHILIP Z» no basta para atribuirle una skin. También admite
que el OCR separe el rótulo como «A TUENDO», sin confundirlo con la pestaña.
En Valorant se puede leer el equipamiento con el cliente abierto. Si no se
identifica una skin del catálogo, Capri explica qué falta en vez de inventarla.

## Datos y funcionamiento

Las preferencias se guardan en `ajustes.json` local. El gusto se calcula siempre
igual por identidad y no necesita guardar historial. Solo la memoria breve de lo
observado vive en RAM y se reinicia al cerrar Capri. No se escriben
capturas, credenciales, historial de equipamiento ni identificadores de cuenta en
el repositorio. La lectura de pantalla utiliza el OCR local de Windows
y archivos temporales eliminados al terminar cada captura; ninguna imagen se
envía a un servicio. No hay modelos ni programas adicionales que instalar.

Las fichas visibles de Valorant se leen antes de consultar el equipamiento para
evitar esperas de red cuando el nombre ya está en pantalla. Si hace falta consultar
el equipamiento, reutiliza el transporte de lectura del cliente ya integrado, con un
acceso GET limitado al equipamiento del jugador autenticado. No cambia skins,
agentes, colas, saldo ni compras. La vigilancia utiliza un transporte independiente
para no bloquear las órdenes de partida con el mismo candado.

Los nombres e identificadores del catálogo público se incluyen en el paquete:
no se consulta a esos proveedores durante el uso normal. No se les envían cuentas
ni sesiones de los jugadores. Los perfiles de preferencias personales no forman
parte del paquete distribuido.

Fuentes técnicas y catálogo:

- [Valorant-API: datos públicos de armas y skins](https://valorant-api.com/)
- [Fortnite-API: catálogo público de cosméticos](https://dash.fortnite-api.com/endpoints/cosmetics)
- [Documentación comunitaria del equipamiento de Valorant](https://valapidocs.techchrism.me/endpoint/player-loadout)
