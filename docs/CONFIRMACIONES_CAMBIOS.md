# Confirmaciones de cambios y recomendaciones del equipo

Por corrección expresa de Franco, la interfaz muestra solo la opción actual, la propuesta, una frase sobre el cambio («más preciso, pero más lento») y un consejo corto para su PC. Se retiraron del diálogo las tarjetas de componentes, las cifras y las explicaciones largas. Conserva el tema cyberpunk y no tiene scroll: parte de 680 píxeles de ancho y ajusta la altura al contenido. Puede ganar ancho si necesita reordenar el texto en una pantalla baja, respetando el área de trabajo y manteniendo los botones visibles.

La evaluación interna sigue consultando CPU, RAM y gráficas para orientar el consejo. Volver a evaluar actualiza la lectura después de cerrar aplicaciones. Los criterios técnicos de abajo documentan la implementación; no se muestran como texto del diálogo. Cancelar, Esc y cerrar conservan la configuración y Aplicar cambio ejecuta la acción una sola vez.

## Cómo se obtiene la información

La lectura ocurre en un trabajador que no toca Tk: registro de Windows para el nombre de la CPU, `os.cpu_count()` para hilos lógicos, `GlobalMemoryStatusEx` para RAM y DXGI para tarjetas y memoria dedicada. DXGI usa `SIZE_T`, evitando el límite de 32 bits de algunas consultas de inventario. No se consultan números de serie, cuentas ni identificadores del equipo, ni se guardan o envían estos datos. No necesita otro programa.

Fuentes: [GlobalMemoryStatusEx](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-globalmemorystatusex), [DXGI_ADAPTER_DESC1](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/ns-dxgi-dxgi_adapter_desc1) e [IDXGIFactory1](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nn-dxgi-idxgifactory1).

## Criterio orientativo de Capri

Este criterio es una heurística de margen para ayudar a decidir, **no requisitos oficiales, memoria medida del modelo ni un benchmark**. Los hilos no describen por sí solos la velocidad real de un procesador.

- La IA utiliza el tamaño local del archivo proporcionado por Ollama, no el nombre del modelo ni una conversión de parámetros a RAM. Se reserva para ejecución en CPU un rango entre `peso + max(1 GiB, 25% del peso)` y `peso + max(2 GiB, 75% del peso)`. La comparación de parámetros solo orienta la explicación de capacidad y no garantiza calidad.
- Se deja un margen adicional de `max(2 GiB, 15% de RAM total)` para el equipo. Si ni la RAM total cubre el extremo inferior más ese margen, aconseja una opción ligera; si la RAM disponible es escasa, distingue un problema actual de carga de una limitación total. Entre ambos extremos aconseja probar con reservas. La sustitución del modelo anterior puede liberar memoria, por lo que la instantánea no predice la disponibilidad final.
- Para reconocimiento en CPU se usan presupuestos internos conservadores de 0,35–0,7 GiB para Vosk, 0,8–1,5 GiB para Base y 1,5–3 GiB para Small. No se muestran como consumos medidos ni requisitos oficiales. Con hasta cuatro hilos se matiza la espera de Whisper; si no se pudo leer la CPU, se explicita esa incertidumbre. Vosk se ofrece como la opción más ligera disponible incluso si el equipo sigue teniendo poca memoria.
- Preparar IA local usa un presupuesto inicial general de 3–5 GiB para orientar el modelo ligero inicial. No confirma que cualquier modelo funcione.

Capri ejecuta actualmente faster-whisper en **CPU/int8 con cuatro hilos**. Por tanto, una GPU potente no convierte Small en una opción más rápida dentro de esta configuración. La implementación permite menor consumo con int8, pero su rendimiento real depende del equipo y del audio; ver [faster-whisper y sus mediciones publicadas](https://github.com/SYSTRAN/faster-whisper).

Detectar una GPU y su capacidad no demuestra que Ollama la use ni cuánta VRAM quede libre. El consejo de IA parte de una evaluación conservadora de CPU/RAM. Si esa evaluación es limitada y una sola gráfica supera el extremo alto del presupuesto orientativo, se cambia a precaución y se explica la posibilidad de usar GPU, exigiendo verificar compatibilidad y VRAM libre; no se da por recomendada ni se afirma aceleración. El contexto, la cuantización y el motor cambian el consumo, como explica la [documentación de Ollama](https://docs.ollama.com/faq).

## Fallos y verificación

Si falta hardware o tamaño fiable, la interfaz informa que los datos son incompletos. El análisis tiene un límite de espera y permite decidir con lo conocido. Cancelar o destruir la ventana cancela el temporizador; una lectura tardía no puede aplicar el cambio ni modificar otro diálogo.

Pruebas de recomendaciones con equipos amplios, ocupados, limitados y desconocidos; memoria dedicada superior a 4 GiB en la interfaz, varias tarjetas sin sumar; revisión del tamaño compacto, idiomas, botones y cancelación. La recomendación no reemplaza probar la precisión con tu micrófono ni medir la latencia de tu modelo en tu equipo.
