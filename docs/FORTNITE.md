# Fortnite en Capri

Abre **Más → Fortnite** o **Ajustes → IA y servicios → Configurar Fortnite**.
El panel conserva el diseño de Capri y permite elegir:

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

Referencias oficiales:

- [Opciones de clasificatoria, rellenar equipo y tamaño del equipo](https://www.epicgames.com/help/c-34254770/c-33726977/a19286399)
- [Fortnite Data API: métricas de experiencias](https://dev.epicgames.com/documentation/fortnite/using-fortnite-data-api-in-fortnite?lang=en-US)
- [Reconocimiento de texto de Windows](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine.trycreatefromuserprofilelanguages)
- [Restauración asíncrona de ventanas de Windows](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindowasync)
