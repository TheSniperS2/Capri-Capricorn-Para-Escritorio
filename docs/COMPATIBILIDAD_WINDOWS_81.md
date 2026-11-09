# Estudio de compatibilidad con Windows 8.1

Fecha: **8 de noviembre de 2026**. Código revisado: `91af754`.

**Estado: archivado.** Tras revisar las limitaciones, el usuario descartó la compatibilidad con Windows 8.1 el 8 de noviembre de 2026. Los posibles cambios y pruebas descritos aquí son parte del estudio histórico; no quedan como tareas pendientes ni autorizan desarrollar una edición reducida.

**Conclusión:** una edición reducida de Capri para **Windows 8.1 de 64 bits** parece técnicamente viable. Es una inferencia de la revisión del código y los requisitos oficiales, **no una compatibilidad comprobada**. El instalador y las dependencias actuales no constituyen una distribución compatible con 8.1. Las funciones completas continúan orientadas a Windows 10/11.

Este estudio no instala programas, no modifica preferencias y no cambia los requisitos de la versión distribuida. No se dispuso de una máquina o VM con Windows 8.1 para arrancar Capri y probar sus bibliotecas nativas.

## Qué podría conservarse y qué quedaría limitado

| Parte de Capri | Evaluación para Windows 8.1 | Motivo y alcance |
| --- | --- | --- |
| Personaje, visor, menús, escritura y animaciones | Candidato a conservarse; falta prueba real | Usan Tkinter, Pillow y llamadas Win32 clásicas. No se encontró aquí una dependencia directa de las APIs multimedia/OCR de Windows 10. Hay que validar Pillow, transparencias, fuentes, escalado y rendimiento. |
| Abrir aplicaciones, carpetas y sitios; controles de ventanas | Candidato a conservarse | Las acciones directas no necesitan un modelo generativo. Dependen de permisos y aplicaciones realmente instaladas. La automatización de cada aplicación debe comprobarse por separado. |
| Voz de Windows | Candidata, con un ajuste de PowerShell | Usa `System.Speech` y reproducción MCI. Depende de las voces instaladas. La despedida utiliza una sintaxis posterior a PowerShell 4.0 y necesita adaptación. |
| Voz natural mediante `edge-tts` | Posible, sin confirmar | [El cliente](https://github.com/rany2/edge-tts) usa un servicio en línea y no requiere instalar Microsoft Edge. Hay que comprobar HTTPS, dependencias, síntesis y reproducción en 8.1. No confundir esto con tener una voz local sin internet. |
| Reconocimiento Vosk y escucha activa | Candidatos, sin confirmar | [Vosk](https://alphacephei.com/vosk/install) publica soporte para Windows x86-64, pero eso no certifica todas las DLL en 8.1. Capri ya dispone de detección de energía cuando no puede usar su VAD de Whisper. Hay que validar PortAudio, CFFI, Vosk y el micrófono real. |
| Whisper con la pila actual | Sin soporte para 8.1 en su conjunto | Sus dependencias incluyen [ONNX Runtime moderno](https://onnxruntime.ai/docs/build/inferencing.html), que exige Windows 10. Requiere otra selección de dependencias o sustituir el motor; no basta con cambiar una opción de Capri. |
| Conversación e interpretación con Ollama local | Fuera del soporte oficial | [Ollama requiere Windows 10 22H2 o posterior](https://docs.ollama.com/windows). Habría que investigar otro motor compatible o un servidor en otro equipo y adaptar la conexión. No hay una alternativa implementada. |
| Monitor de CPU y RAM | Candidato a conservarse | Se leen con `GetSystemTimes` y `GlobalMemoryStatusEx`. Hay que comprobar los resultados reales. |
| Monitor de GPU y VRAM | No disponible por el método actual | Los contadores usados corresponden a la infraestructura moderna de GPU de Windows, [con requisito WDDM 2.0](https://devblogs.microsoft.com/directx/gpus-in-the-task-manager/). En una edición reducida habría que ocultar esos datos o indicar que no están disponibles, sin mostrar valores inventados. |
| Panel multimedia, carátula, progreso y controles de sesión | No funciona con el backend actual | [GlobalSystemMediaTransportControlsSessionManager](https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionmanager) aparece en Windows 10 1809. Necesita otro backend para 8.1. |
| Fortnite por OCR y lectura de fichas de skins | No funciona con el OCR actual | [OcrEngine](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine) se introduce en Windows 10. Además, Fortnite actual exige un sistema más reciente. |
| LoL, Valorant y Fortnite actuales | Sin integración local soportada en 8.1 | Los requisitos de [LoL](https://support.riotgames.com/en-us/league-of-legends/performance/minimum-and-recommended-system-requirements-league-of-legends/), [Valorant](https://support.riotgames.com/en-us/valorant/support-tools/minimum-recommended-pc-specs) y [Fortnite](https://www.epicgames.com/help/c-34254770/c-38015632/fortnite-a16548002) excluyen Windows 8.1. Adaptar Capri no cambia los requisitos de sus clientes ni de sus sistemas antitrampas. |
| Spotify de escritorio actual | Fuera de los requisitos de Spotify | [Spotify documenta Windows 10 de 64 bits o posterior](https://support.spotify.com/us/article/supported-devices-for-spotify/). Las versiones antiguas no son una base comprobada para esta adaptación. |
| Puente de Opera/YouTube | Necesita adaptación y prueba | [Opera 95](https://blogs.opera.com/desktop/2023/02/opera-95-stable/) es la última versión oficial para 8.1. La extensión actual usa ejecución `MAIN` desde el manifiesto; hay diferencias con Chromium 109 y debe revisarse ese flujo y el reproductor actual de YouTube. Abrir una web y controlarla son capacidades distintas. |

Las filas «candidato» señalan una posibilidad de adaptación, no resultados obtenidos en Windows 8.1.

## Evidencia en el proyecto

- `requirements.txt` instala las dependencias de voz junto a las de interfaz; no existe un perfil reducido de instalación.
- `installer/plantilla.py`, método `trabajar`: instala todos los requisitos, comprueba `import faster_whisper` y prepara el modelo Whisper antes de completar la instalación. Aunque se eligiera Vosk después, el preparador seguiría intentando esos pasos.
- `src/reconocimiento.py`, `DetectorVoz`: puede sustituir el VAD por energía si falla la biblioteca. Eso ayuda a un perfil Vosk, pero no adapta por sí solo el instalador ni prueba las DLL.
- `src/activar_ia.py`, método `trabajar`: descarga el instalador oficial de Ollama. `src/core.py` y `src/intenciones.py` se conectan a `127.0.0.1:11434`; un servidor remoto o un motor diferente requerirían cambios explícitos.
- `src/reproduccion_pc.py` y `src/multimedia.py`: utilizan las sesiones multimedia de Windows 10.
- `src/fortnite_vision.py`, `OCR`: usa `Windows.Media.Ocr.OcrEngine`. La lectura visual de skins también depende de esa infraestructura.
- `src/monitor_pc.py`, `LecturaWindows`: consulta `GPU Engine` y `GPU Adapter Memory`. Ya admite datos ausentes; debe comprobarse la presentación correspondiente en el sistema antiguo.
- `src/voz.py`, método `_hablar`: la pausa de la despedida construye `PromptBuilder` con `::new()`. [Windows 8.1 incluía PowerShell 4.0](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle) y [esa construcción se añadió en 5.0](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_object_creation). Se puede estudiar sustituirla por `New-Object`, evitando exigir una actualización adicional solo para esta frase.
- `integraciones/opera-capri/manifest.json` y `page.js`: el control de volumen accede a las funciones JavaScript del reproductor en el mundo principal de la página. No basta con que el navegador acepte Manifest V3 para dar ese comportamiento por compatible.

En el esquema oficial de [Chromium 109](https://chromium.googlesource.com/chromium/src/+/109.0.5414.119/extensions/common/api/content_scripts.idl), el campo `world` de los scripts del manifiesto figura como no destinado a utilizarse, con ejecución aislada. El esquema de [Chromium 111](https://chromium.googlesource.com/chromium/src/+/111.0.5563.64/extensions/common/api/content_scripts.idl) cambia esa descripción y [la documentación de ExecutionWorld](https://developer.chrome.com/docs/extensions/reference/api/extensionTypes#type-ExecutionWorld) marca Chrome 111+. Esto justifica revisar el puente, sin afirmar que se haya probado Opera 95 con la extensión de Capri.

## Dependencias que requieren atención

[Python 3.12 sí documenta soporte para Windows 8.1](https://docs.python.org/3.12/using/windows.html), usando el instalador tradicional. La edición de Microsoft Store requiere Windows 10. Python no es por sí solo el impedimento.

En la instalación inspeccionada se encontraron, entre otras, estas versiones:

| Componente | Versión instalada observada | Observación |
| --- | --- | --- |
| Pillow | 12.3.0 | No probado en 8.1 en esta revisión. Su [lista de plataformas probadas](https://pillow.readthedocs.io/en/stable/installation/platform-support.html) no certifica esta combinación. |
| sounddevice / Vosk | 0.5.6 / 0.3.45 | Candidatos para una entrada de voz reducida; faltan pruebas de sus binarios y del dispositivo. |
| edge-tts | 7.3.1 | La voz usa un servicio remoto; falta comprobar la pila de red y audio en 8.1. |
| faster-whisper | 1.2.1 | Declara CTranslate2, ONNX Runtime, PyAV y otras dependencias. |
| CTranslate2 | 4.8.4 | [Publica ruedas Windows x86-64 y necesita runtime de Visual C++](https://opennmt.net/CTranslate2/installation.html); no se encontró una certificación específica de 8.1 para esta combinación. |
| ONNX Runtime | 1.31.1 | La documentación actual exige Windows 10. El proyecto [anunció la retirada de 8.1 desde 1.15](https://github.com/microsoft/onnxruntime/discussions/16088). |
| NumPy / PyAV | 2.5.4 / 19.0.2 | Binarios transitivos que también deben verificarse; no se consideran compatibles por tener etiqueta `win_amd64`. |
| pywin32 / Send2Trash | 312 / 2.1.0 | Hay que validar las operaciones Win32 y papelera en el sistema objetivo. |

Estos números describen la copia inspeccionada, no una lista de versiones que deban instalarse en 8.1 ni una resolución futura de `pip`.

Tampoco basta con fijar ONNX Runtime 1.14.1: la [lista de archivos de PyPI para Windows](https://pypi.org/project/onnxruntime/1.14.1/#files) llega a CPython 3.10 y **no incluye una rueda para CPython 3.12**. Cambiar de Python, compilar bibliotecas o congelar dependencias antiguas exige verificar el conjunto completo. No se eligió una combinación sin probarla.

Como comprobación estática se analizaron los archivos Python de `src` e `installer` solicitando gramáticas 3.10, 3.11 y 3.12, sin errores de sintaxis. Esto no ejecuta esas versiones de Python ni comprueba sus APIs, dependencias o comportamiento en 8.1.

## Alcance propuesto para un primer prototipo

Una primera edición experimental podría centrarse en personaje/visor, menús, órdenes directas por texto, CPU/RAM y voz de Windows. Después se comprobarían Vosk, escucha activa y voz natural por separado.

Para construirla haría falta:

1. Añadir detección de versión/capacidades y seleccionar un perfil de instalación reducido de 64 bits. Evitar que la ausencia de una función opcional impida abrir la interfaz.
2. Separar las dependencias de interfaz, reconocimiento y conversación. No obligar a instalar/importar Whisper ni descargar sus modelos en el perfil reducido.
3. Ocultar o explicar las capacidades ausentes: sesiones multimedia, OCR de Windows 10, contadores de GPU y activación de Ollama. Conservar la configuración de la edición normal.
4. Adaptar la construcción de PowerShell de la despedida y comprobar las demás funciones con el PowerShell disponible.
5. Resolver y fijar un conjunto de ruedas compatible, registrar sus versiones y probar imports, arranque y funciones reales en Windows 8.1 actualizado. Para Vosk y audio, incluir pruebas en hardware real.
6. Mantener una instalación de prueba independiente y repetir los controles de Windows 10/11 antes de distribuir cambios compartidos.

La compatibilidad de 32 bits queda fuera de esta propuesta. Las alternativas a Ollama, al panel multimedia y al OCR serían trabajos posteriores, no partes resueltas por este estudio.

## Cómo se comprobaría

| Comprobación | Evidencia necesaria |
| --- | --- |
| Instalación limpia | Completar el preparador reducido sin importar funciones excluidas, conservar registros y versiones instaladas. |
| Interfaz | Abrir visor/personaje, moverlos, alternar modos, escribir, abrir ajustes y cerrar sin fallos de DLL o transparencia. |
| Controles básicos | Abrir una aplicación y una carpeta elegidas, sin activar automatizaciones de juegos. |
| Voz | Probar síntesis de Windows, voz natural por separado, interrupción, volumen y despedida. |
| Micrófono | Comprobar dispositivos, captura, Vosk, palabra de activación y respuesta sin nombre con ruido y silencio. |
| Monitor | Comparar CPU/RAM; comprobar que los datos de GPU ausentes se muestran como no disponibles. |
| Funciones excluidas | Verificar que no se intentan iniciar Ollama, sesiones multimedia ni OCR incompatibles. |
| Regresión | Mantener las pruebas de la edición normal de Windows 10/11. |

Una VM permite parte de la comprobación visual y de instalación; no certifica micrófonos, GPU ni juegos. No se han ejecutado estas pruebas en 8.1.

[Windows 8.1 terminó su soporte de Microsoft en enero de 2023](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-8-1-end-support-january-2023). Una edición para ese sistema supondría mantener y probar una combinación antigua de dependencias; no equivaldría a recibir soporte actual de los proveedores.
