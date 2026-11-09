# Counter-Strike 2 en Capri

Abre **Ajustes → Juegos → Counter-Strike → Partidas** y pulsa **Configurar Counter-Strike**.
Esta integración está preparada para el ejecutable `cs2.exe` y su menú **Competitivo**.
El panel se muestra dentro de Ajustes. Pulsa **Volver** para regresar a la página anterior; tus cambios quedan guardados.

## Guardar y aplicar mapas

1. Selecciona los mapas que quieras en las tarjetas del panel. El filtro permite encontrarlos por nombre.
2. Si la lista del juego ha cambiado, usa **Leer mapas del juego**. Capri abre el menú de emparejamiento competitivo, lee las tarjetas visibles y vuelve a mostrar su panel con la lista detectada.
3. Usa **Aplicar mapas sin buscar** para comprobar la selección sin iniciar una cola.
4. Cuando quieras jugar, pulsa **Buscar partida** o di **«Capri, busca partida en Counter-Strike»**.

La instalación empieza sin mapas seleccionados. Las preferencias se guardan localmente
en `ajustes.json`; no se distribuyen los mapas personales del desarrollador. La lista
inicial contiene nombres conocidos y no garantiza su disponibilidad en una rotación.
La lectura del juego actualiza la lista sin eliminar tus mapas guardados que ya no
aparezcan. Debes desmarcar esos mapas antes de buscar: Capri no los sustituye por otros.

## Órdenes

- «Busca partida en Counter-Strike», «busca partida en CS2».
- «Aplica mis mapas en CS2».
- «Lee los mapas de CS2».
- «Cancela la cola en CS2».
- «Configura Counter-Strike».

También entiende el nombre coloquial «CS:GO» en estas órdenes, pero el control de esta
versión corresponde a **CS2**. No se anuncia compatibilidad con el cliente antiguo.
Al abrir el panel o dar una orden explícita se guarda Counter-Strike como juego para
las siguientes peticiones cortas de buscar/cancelar. En **Automático**, las órdenes de
voz usan el juego que está en primer plano. Una petición que nombra otro juego conserva
su destino explícito.

## Qué comprueba Capri

Recupera el juego si está minimizado y lo mantiene visible durante la operación.
Si hace falta, pasa de Jugar a Emparejamiento y Competitivo. Verifica las pestañas
activas, los títulos de las tarjetas y las casillas mediante captura y OCR local de
Windows. Activa primero los mapas deseados y después desmarca los demás. Comprueba
cada cambio y la selección completa antes del único clic de búsqueda.

Si no puede leer todas las casillas, falta un mapa, cambia el menú o se pierde el foco,
detiene la operación. Un clic sin confirmación no se repite automáticamente. El juego
debe quedar sin ventanas encima de los controles; las capturas negras de pantalla
completa exclusiva o un cambio del diseño pueden impedir la lectura. En ese caso pide
dejar visible el menú, sin cambiar por su cuenta el modo de pantalla.

**Cancelar búsqueda** solicita la cancelación de una cola reconocible y no vuelve a
buscar. Capri no vigila para reencolar ni acepta partidas automáticamente: la
confirmación de partida corresponde al jugador. No hace el veto de mapas de Premier
ni modifica el modo Prime, el grupo o los ajustes del juego.

La lectura es temporal y local; no instala programas adicionales, escribe archivos
de Counter-Strike, utiliza la consola ni modifica la memoria del juego. Las acciones
usan sus controles normales y solo se ejecutan al pedirlas.

## Comprobación realizada y pruebas pendientes

La lógica se prueba con un menú simulado: mapas exactos, aplicación sin buscar,
búsqueda una sola vez, cancelación, cambios de preferencias, foco y controles ambiguos.
La lectura visual se comprueba con imágenes sintéticas a varias escalas y capturas
públicas de referencia, incluyendo casillas vacías y marcadas. Esto no sustituye una
prueba en el cliente actual.

En el equipo de desarrollo no se encontró una instalación activa ni un proceso de CS2;
solo carpetas residuales. **No se inició ninguna cola real.** Falta verificar el menú y
la selección con tu instalación: primero lee sus mapas, aplica una selección sin
buscar y comprueba que se conserva al reiniciar Capri. La búsqueda real se verifica
cuando ya quieras jugar.

Las rotaciones pueden cambiar. Referencias de Valve:
[noticias oficiales de Counter-Strike](https://www.counter-strike.net/home?l=english),
[regreso de Cache a los modos de juego](https://steamcommunity.com/games/CSGO/announcements/detail/508486359454843046).
