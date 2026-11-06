# League of Legends: cola, picks y baneos

Abre el cliente de LoL, prepara la sala y elige el modo y los roles allí. Capri utiliza esa selección; no crea una sala ni cambia el tipo de partida.

En el menú radial, abre **Más → League of Legends**. También puedes escribir o decir:

## Panel y perfiles por línea

Abre **Más → League of Legends** para entrar directamente al panel, o pulsa **Configurar League of Legends** en **Ajustes → IA y servicios**. El panel reúne búsqueda, búsqueda con aceptación, aceptación de la partida actual, cancelación y vigilancia automática.

Elige **Top, Jungla, Medio, ADC o Soporte** para configurar tres **picks** y tres **baneos**, ordenados por prioridad. Pulsa una tarjeta para buscar un campeón por nombre y elegirlo con su retrato. **Quitar campeón** deja libre ese lugar. Los cambios se guardan automáticamente; cambiar de pestaña edita ese perfil y no cambia tu posición en el cliente de LoL.

Los interruptores **Confirmar picks automáticamente** y **Confirmar baneos automáticamente** son independientes y vienen apagados. Al activarlos, Capri utiliza la línea que te asigne LoL y confirma la primera opción disponible **solo durante tu turno**. Si la primera está seleccionada, baneada o no está disponible para tu cuenta, prueba la siguiente. En baneos respeta también los campeones que tus aliados estén señalando. No cambia una elección que ya estés señalando manualmente: continúa desde LoL en ese caso.

Si no hay línea asignada, no queda ninguna opción válida o el cliente rechaza la acción, el panel lo indica y debes continuar en LoL. No selecciona un campeón ajeno a tu lista. No configura modos sin asignación de línea, como ARAM. Desactivar los interruptores o cerrar Capri detiene la automatización; una confirmación que LoL ya haya recibido no se puede deshacer desde Capri.

En algunos clientes la lista de campeones baneables devuelve únicamente `-1` (la opción de no banear), incluso durante un turno válido. En ese caso Capri consulta la ficha actual de cada campeón configurado: exige que esté habilitado, sin banear ni seleccionado y respeta las intenciones de tus aliados. Revalida el turno antes de confirmar. Este respaldo solo se aplica al baneo; los picks conservan su lista de disponibilidad habitual.

Cancelar desde LoL o Capri **no vuelve a iniciar la búsqueda**. El monitor de picks y baneos no toca la cola ni acepta partidas. La aceptación automática se configura por separado.

El catálogo y los retratos oficiales de Data Dragon se incluyen con Capri (versión indicada en el panel). El buscador no necesita Internet. Se actualizan con la aplicación; no son estadísticas del parche ni recomendaciones de composición. La referencia funcional es organizar tu repertorio por línea, inspirada en el [Champion Pool Builder de iTero](https://www.itero.gg/champion-pool-builder); Capri no incorpora su motor de recomendaciones.

## Órdenes y aceptación

| Petición | Resultado |
| --- | --- |
| «Busca partida en LoL» / “Find a match in LoL” | Inicia la búsqueda en la sala preparada. |
| «Busca partida en LoL y acepta por mí» | Busca y acepta automáticamente los ready-checks de esa búsqueda. |
| «Activa la aceptación automática del LoL» | Vigila las colas actuales y futuras, aunque las inicies directamente en LoL. La preferencia se guarda. |
| «Acepta la partida» / “Accept the match” | Acepta el ready-check actual, si existe. |
| «Cancela la cola» / “Cancel the queue” | Cancela una búsqueda que siga en curso. |
| «No aceptes más partidas» / “Disable auto accept in LoL” | Detiene toda aceptación automática y guarda la opción desactivada. |

Portugués: «busque uma partida no LoL», «aceite a partida», «cancele a fila». Japonés: 「マッチを検索して」「マッチを承諾して」「マッチングをキャンセルして」。 Los resultados se muestran en el idioma seleccionado en Capri, sin necesitar una traducción del modelo.

Activa **Aceptar partidas automáticamente, también desde LoL** en el panel **Más → League of Legends**, o la misma casilla en **Ajustes → IA y servicios**. Basta hacerlo una vez: la elección se guarda y se recupera al abrir Capri. A partir de entonces, busca desde LoL o desde Capri; puede aceptar también una cola que ya estuviera en marcha cuando activas la vigilancia. La opción viene desactivada inicialmente. Activarla no inicia una búsqueda.

El estado de conexión y vigilancia aparece debajo de la casilla. Durante la búsqueda se consulta el cliente cada 250 ms; la aceptación se envía desde un trabajador independiente, sin esperar a una orden de voz ni al modelo. Es un intervalo de consulta, no una garantía de latencia: depende de la respuesta del cliente.

Puedes ir al baño mientras espera: si llega el ready-check, Capri lo acepta. Si otra persona no acepta y el cliente vuelve a buscar, sigue pendiente del siguiente. Durante selección de campeón y partida no actúa y conserva la vigilancia para la próxima cola. Si LoL se cierra o pierde la conexión, vuelve a intentar conectarse; también puedes abrir LoL después de Capri.

Desactivar la casilla o cerrar Capri detiene la vigilancia. Cerrar Capri no cancela la cola de LoL. Una partida ya encontrada se rechaza desde el propio cliente. Si pides cancelar cuando ya hay ready-check, Capri omite esa aceptación; la vigilancia guardada continúa disponible para una nueva búsqueda.

«Busca partida en LoL y acepta por mí» sigue disponible para una sola búsqueda: si no activaste la vigilancia permanente, se detiene al llegar a selección de campeón, salir de la cola o perder la conexión.

## Conexión y límites

Capri se comunica únicamente con la API local del cliente en `https://127.0.0.1`. Descubre el puerto y el token temporal del proceso de LoL o de su `lockfile`; no pide tu contraseña de Riot, no guarda el token y no lo envía a Ollama. No usa proxies ni sigue redirecciones. El certificado autofirmado se admite exclusivamente para ese origen local fijo.

Si el cliente no aparece, ábrelo con los mismos permisos de Windows que Capri. Si hay varios clientes, deja uno solo. Si LoL rechaza una búsqueda, revisa los roles, el líder del grupo y los avisos del cliente. Capri distingue una solicitud enviada de un resultado confirmado; no informa una aceptación exitosa solo por haber enviado la petición.

Esta integración no controla al personaje durante la partida. Los picks y baneos requieren activar sus opciones explícitamente. La [League Client API no tiene soporte oficial para aplicaciones de terceros](https://developer.riotgames.com/docs/lol#league-client-api) y puede cambiar entre versiones. Las pruebas de desarrollo usan un cliente simulado: no inician colas, aceptan partidas ni confirman selecciones reales. La nueva selección por línea todavía debe comprobarse en una sesión real del cliente.

## Desarrollo

`src/league.py` limita métodos y rutas a estas operaciones:

- `GET /lol-gameflow/v1/gameflow-phase`
- `GET /lol-lobby/v2/lobby`
- `POST` y `DELETE /lol-lobby/v2/lobby/matchmaking/search`
- `GET /lol-matchmaking/v1/ready-check`
- `POST /lol-matchmaking/v1/ready-check/accept`
- `GET /lol-champ-select/v1/session`
- `GET /lol-champ-select/v1/pickable-champion-ids`
- `GET /lol-champ-select/v1/bannable-champion-ids`
- `GET /lol-champ-select/v1/grid-champions/{championId}` solo con identificador numérico positivo, para comprobar los baneos configurados cuando la lista anterior no contiene campeones.
- `PATCH /lol-champ-select/v1/session/actions/{id}` únicamente con un ID numérico, `championId` positivo y `completed: true`.

`src/lol_seleccion.py` separa la vigilancia de selección de la aceptación de partidas. Revalida fase, turno local, rol, selección manual, disponibilidad y preferencias antes de confirmar. Solo realiza un intento por acción para evitar repetir confirmaciones rechazadas o de resultado incierto. `src/lol_ui.py` mantiene las consultas fuera de Tk y usa imágenes locales.

La interpretación exige una petición completa. El modelo de conversación no recibe acceso genérico a endpoints. El seguimiento usa un trabajador cancelable, y los avisos vuelven a Tk a través de la cola de eventos.

Riot solicita [registrar las aplicaciones que utilizan el cliente local](https://developer.riotgames.com/docs/lol#league-client-api) en su portal. Este repositorio no afirma contar con aprobación ni registro de Riot; el responsable de una distribución debe realizar ese trámite con su propia cuenta.

Capri is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
