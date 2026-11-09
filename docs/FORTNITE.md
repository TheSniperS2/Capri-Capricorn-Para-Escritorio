# Fortnite en Capri

Abre **Ajustes → Juegos → Fortnite → Partidas** y pulsa **Configurar Fortnite**.
El panel conserva el diseño de Capri y permite elegir:
El panel se muestra dentro de Ajustes. Pulsa **Volver** para regresar a la página anterior; tus cambios quedan guardados.

- Battle Royale, Cero construcción o conservar el modo actual.
- Solo, Dúo, Trío, Squad o conservar el tamaño del equipo actual.
- **Aplicar opciones sin buscar partida**, **Buscar partida** y **Cancelar búsqueda**.

Las preferencias se guardan solamente en `ajustes.json` de tu instalación. El
programa distribuido empieza con «Modo actual» y «Equipo actual»; no incorpora
las elecciones de otra persona. Guardar opciones o abrir el panel no toca el juego.
Capri no pulsa los controles de clasificatoria ni rellenar equipo. Fortnite puede
ajustar su disponibilidad al cambiar el modo o el tamaño del equipo.

## Uso

Puedes dejar Fortnite minimizado, siempre que lo hayas dejado en el lobby.
Al solicitar una acción, Capri restaura automáticamente su ventana, espera a que
el juego vuelva a dibujarse y lee los controles antes de aplicar las preferencias.
El juego aparece en primer plano durante la operación; este método no realiza
clics mientras permanece minimizado. También acepta «busca partida en Fortnite», «cancela la cola en
Fortnite» y «aplica mis opciones en Fortnite». Seleccionando Fortnite como juego
para buscar, basta «busca partida». En Automático, las órdenes de voz genéricas
reconocen Fortnite si es el juego en primer plano.

La acción de búsqueda confirma de nuevo el modo y tamaño elegidos antes de
pulsar Jugar. Si no puede leerlos, los controles cambiaron o hay varias opciones
iguales, se detiene y explica lo que falta. Nunca inicia una nueva búsqueda al
terminar o cancelar una partida. En un grupo se respetan las restricciones que
muestre Fortnite; Capri no cambia el líder ni la composición del grupo.

## Cómo funciona y límites

Esta integración usa capturas temporales del cliente y el reconocimiento de texto
que ya incluye Windows; no necesita instalar otro programa, descargar modelos,
iniciar sesión otra vez ni extraer credenciales de Epic. Las imágenes se procesan
localmente y se eliminan al terminar cada lectura. No se captura nada mientras
no se solicita una acción. No usa inyección, memoria del juego ni un overlay.

Los controles se identifican por texto y posición dentro del lobby, con etiquetas
en español, inglés o portugués. Las opciones disponibles dependen de la experiencia
y de Fortnite. Si una actualización cambia el menú o una opción no es visible,
Capri pide seleccionarla desde el juego; no hace clic en coordenadas supuestas.
Fortnite debe permanecer en primer plano mientras se aplica la acción. Si otra
ventana tapa un control, se detiene. La captura de pantalla completa exclusiva
depende de Windows/controlador: si devuelve una imagen vacía no es posible leer
el lobby con este método. No coloca a Capri encima del juego en ese modo.

**Estado de validación:** comprobados el OCR nativo, la interfaz y las órdenes.
En el cliente real se verifican los cambios de experiencia y tamaño del equipo
mediante **Aplicar opciones sin buscar partida**. Los clics de iniciar/cancelar
cola y su confirmación se prueban con un cliente simulado; no se ha iniciado
ninguna partida durante el desarrollo.
También se comprobó en el cliente real la recuperación desde minimizado y la
confirmación de preferencias, sin entrar en cola.

## Avisos de tienda y de misiones con pavos

En **Ajustes → Juegos → Fortnite → Avisos** puedes activar por separado el aviso de nueva
tienda y las alertas de misiones de **Salvar el Mundo**. Para estas últimas marca
también **Tengo una cuenta de fundador de STW**. Es una declaración local: Capri no
inicia sesión en Epic ni comprueba tu cuenta. Los pavos de estas misiones requieren
ser fundador y tener acceso a la misión; las otras cuentas reciben rayos X.
[Requisitos de Epic](https://www.epicgames.com/help/c-39719500/c-36066936/a13457604).

El panel muestra la rotación, las misiones con zona, nivel y recompensa y su
caducidad en la hora local del equipo. **Comprobar ahora** consulta los datos sin
entrar al juego ni activar los avisos. Todas las opciones empiezan desactivadas.
Con Capri abierta, las opciones activas se comprueban cada cinco minutos; si hay
un fallo se reintenta después de un minuto. Las consultas manuales tienen un
intervalo mínimo de treinta segundos.

La primera consulta de la tienda establece una referencia y no anuncia un cambio
que no haya observado. La siguiente rotación se anuncia una vez, también si Capri
estaba cerrada al cambiar. Las misiones con pavos vigentes pueden anunciarse al
activar la opción. Se conserva qué avisos se han entregado para no repetirlos al
reiniciar. Esperan mientras conversas y caducan al acabar la rotación; no recuperan
el foco del juego.

La tienda procede de [Fortnite-API](https://fortnite-api.com/) y las misiones de
[V-Bucks Daily](https://vbucksdaily.com/) (su fuente indicada es Free the V-Bucks).
Son fuentes comunitarias. Capri exige datos completos de la rotación UTC actual:
un fallo, datos antiguos o incompletos no se interpretan como ausencia de misiones.
El reinicio previsto del panel es orientativo; el aviso espera confirmación del
proveedor. No se necesitan claves, credenciales, extensiones ni instalaciones
adicionales. El estado de entrega vive en `cache/fortnite/avisos.json` local y no
se distribuye.

## Referencias oficiales

- [Opciones de clasificatoria, rellenar equipo y tamaño del equipo](https://www.epicgames.com/help/c-34254770/c-33726977/a19286399)
- [Fortnite Data API: métricas de experiencias](https://dev.epicgames.com/documentation/fortnite/using-fortnite-data-api-in-fortnite?lang=en-US)
- [Reconocimiento de texto de Windows](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine.trycreatefromuserprofilelanguages)
- [Restauración asíncrona de ventanas de Windows](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindowasync)
