# Valorant: búsqueda y preferencias de agente

Abre **Más → Valorant** para entrar directamente al panel. También está disponible en **Ajustes → IA y servicios → Configurar Valorant**.

## Tres preferencias

1. Pulsa una de las tarjetas de **Prioridad 1, 2 o 3**.
2. Busca el agente por nombre o pulsa su retrato para asignarlo a esa prioridad.
3. Repite con tus alternativas. **Quitar agente** deja libre la tarjeta activa. Los cambios se guardan al instante.

Si un aliado ya eligió o está señalando tu primera opción, Capri busca la segunda; si tampoco está disponible, la tercera. También comprueba los agentes desbloqueados en tu cuenta y los agentes base. **Si no queda ninguna preferencia válida, no selecciona ni confirma otro agente fuera de tu lista.** Se respeta una selección que hayas realizado manualmente en el juego.

**Confirmar agente automáticamente** viene desactivado. Al activarlo, Capri espera a detectar un mapa, la fase de selección activa con tiempo restante y al jugador local incorporado. Aplica un margen de seguridad de **seis segundos** desde esa detección para no adelantarse a la presentación del mapa. Este margen no mide visualmente cuándo termina la animación. Después elige según tus preferencias y vuelve a consultar el equipo y la partida antes de seleccionar y confirmar. Si cambia el mapa o se pierde la preparación, reinicia la espera. También aplica esta protección al botón de confirmación manual. Si otro jugador toma un agente entre esas consultas, no lo confirma y puede continuar con la siguiente prioridad. No repite indefinidamente un intento rechazado para el mismo agente y partida.

También puedes dejar el interruptor apagado y usar **Confirmar agente en partida**. Ese botón realiza un intento con tus preferencias durante la selección actual. Elegir un retrato en el panel solo guarda la preferencia; no inicia una búsqueda ni envía una selección al juego.

La selección automática se conserva al reiniciar Capri y continúa disponible después de cancelar y volver a buscar manualmente. Cerrar el panel no la desactiva; apagar el interruptor o cerrar Capri detiene su vigilancia. Una confirmación ya recibida por Valorant no se puede deshacer desde Capri.

## Buscar y cancelar

Abre Valorant, inicia sesión y prepara la sala, el modo y los servidores desde el juego. Capri utiliza esa configuración y no crea grupos ni cambia modos.

Puedes decir «Capri, busca partida en Valorant», «tira partida en Valorant» o «ponme en cola en Valorant». Para parar: «cancela la búsqueda en Valorant». Estas órdenes utilizan el controlador del cliente; no necesitan ver la pantalla. Si no hay conexión, Capri debe informar ese error, sin inventar una explicación sobre visión o confirmar una acción que no se haya realizado.

Si Riot indica `Idle` aunque el juego siga abierto, Capri comprueba además el proceso de Valorant antes de descartar la sesión. Las peticiones remotas identifican la aplicación como `CapriDesktop`. Se ha verificado la lectura de una sala real; la confirmación de búsqueda y selección reales continúa pendiente de validación.

| Control u orden | Resultado |
| --- | --- |
| **Buscar partida** / «Busca partida en Valorant» | Inicia la búsqueda en tu sala si eres el líder y el cliente no indica una restricción. |
| **Cancelar búsqueda** / «Cancela la cola en Valorant» | Pide cancelar una búsqueda activa. No vuelve a iniciarla. |
| **Confirmar agente en partida** / «Confirma mi agente en Valorant» | Selecciona y confirma la primera preferencia disponible durante la selección actual. |

Las órdenes directas también tienen variantes en inglés, portugués y japonés; no necesitan una decisión del modelo de conversación.

### Órdenes desde el juego a pantalla completa

Con la activación por voz encendida puedes decir **«Capri, busca partida»** sin volver al escritorio. Si el ejecutable de Valorant está en primer plano, las órdenes de voz genéricas para buscar o cancelar se dirigen a Valorant; una orden que mencione expresamente LoL conserva ese destino. También sigue disponible la tecla global para hablar, F8 por defecto.

### Usar Capri con Valorant detrás

En el chat, el selector **Juego para buscar** permite elegir **Valorant**, **League of Legends** o **Automático**. Al elegir Valorant, «busca partida» y «cancela la cola» funcionan por texto o voz aunque Capri tenga el foco y Valorant esté en segundo plano. Abrir **Más → Valorant** también selecciona ese destino y lo guarda para la siguiente sesión. Las órdenes que mencionan expresamente el juego se dirigen a él y actualizan esa elección para las siguientes órdenes.

En **Automático** se conserva la detección de Valorant en primer plano para las órdenes de voz. Si quieres usar los comandos genéricos desde el escritorio sin depender del foco, selecciona Valorant. Los botones del panel siempre indican el juego explícitamente y tampoco necesitan que Valorant esté en primer plano.

### Mostrar y minimizar Capri

- **Ctrl+Alt+C** recupera solo el avatar, sin abrir ni enfocar el chat. Si ya estás usando una ventana de Capri, la misma combinación la oculta.
- El botón **—** del chat y de los paneles de LoL/Valorant, o **Más → Minimizar Capri**, minimiza sus ventanas.
- Puedes recuperarla con **Ctrl+Alt+C**. El chat y los paneles permanecen cerrados visualmente hasta que los abras desde el menú de Capri.
- Minimizar no cierra Capri ni cancela la cola. La voz y la selección automática de agentes continúan; los avisos visuales y las interacciones espontáneas quedan ocultos mientras esté minimizada.

El atajo ya no solicita activar el chat ni utiliza SetForegroundWindow. No se cambia el modo de pantalla de Valorant ni se instala un overlay en el juego. El sistema actual de ventanas de Capri no permite garantizar la superposición sobre Valorant en pantalla completa exclusiva. Esa función no está implementada; el atajo no resuelve esa limitación. Microsoft documenta las [restricciones para activar ventanas](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).

Al recuperar Capri se cierran los desplegables temporales; puedes volver a abrirlos normalmente sin que una lista oculta conserve los clics.

Dejar Ajustes abierto detrás de Valorant ya no pausa la activación por nombre mientras el juego está en primer plano. La escucha continúa pausándose al hablar Capri y mientras editas los ajustes fuera del juego. Estas órdenes se ejecutan mediante los servicios del cliente, sin activar ventanas, abrir el chat ni minimizar el juego. La ruta se verifica con pruebas que simulan el contexto de primer plano; falta comprobar el reconocimiento y la acción real durante una sesión de Valorant a pantalla completa.

**Cancelar desde Capri o desde el juego significa dejar de buscar.** Capri no interpreta una salida de la cola como permiso para volver a entrar. Si el propio Valorant continúa buscando tras una selección interrumpida, la vigilancia de agentes permanece disponible para la siguiente selección. Si vuelve a la sala y no se conoce de forma fiable el motivo, espera una nueva petición. El reintento automático iniciado por Capri ante cancelaciones externas queda pendiente de disponer de señales verificadas que lo distingan de una cancelación manual; esta versión no lo inventa a partir de una transición de estado.

## Conexión y privacidad

Capri consulta la sesión activa del cliente de Riot en este equipo. No pide tu contraseña ni realiza un inicio de sesión alternativo. Obtiene los tokens temporales en memoria y los envía solo a los servicios de Riot necesarios para la sala, la selección y los agentes desbloqueados. No los guarda en archivos, no los muestra y no los envía a Ollama ni al proveedor del catálogo.

La API local usa exclusivamente `https://127.0.0.1` y admite allí el certificado autofirmado. Las llamadas remotas utilizan los hosts de Riot `glz-{región}-1.{shard}.a.pvp.net` y `pd.{shard}.a.pvp.net`, con certificado HTTPS verificado, sin proxies ni redirecciones. Las rutas y métodos están limitados; no se permite enviar URLs o comandos arbitrarios mediante el modelo.

Los retratos y nombres se incluyen con Capri y no se descargan al abrir el panel. El catálogo procede de [Valorant-API](https://valorant-api.com/), un servicio comunitario de datos del juego; los recursos pertenecen a Riot Games. No es un catálogo de recomendaciones ni estadísticas de jugadores.

## Validación y límites

La integración utiliza servicios del cliente que no forman parte de la [API pública oficial de Valorant](https://developer.riotgames.com/docs/valorant#valorant-official-apis). Pueden cambiar con las actualizaciones. El panel, los controles, la conexión y la selección están probados con respuestas simuladas; **la búsqueda y la confirmación de agentes todavía requieren validación con el cliente real**. Las pruebas no entran en colas, confirman agentes ni abandonan partidas reales.

No se utiliza información del equipo enemigo ni se controla al personaje dentro de una partida. La integración no evita las restricciones o penalizaciones del juego. Si una petición se envía sin poder comprobar su resultado, Capri lo indica y no afirma que se haya completado.

Referencias técnicas: [formatos y endpoints del cliente](https://github.com/techchrism/valorant-api-docs) y [documentación de Riot para Valorant](https://developer.riotgames.com/docs/valorant).

Capri is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
