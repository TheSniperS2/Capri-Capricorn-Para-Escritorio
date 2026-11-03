<p align="center">
  <img src="docs/media/readme/capri-intro.webp" width="100%" alt="Capri aparece sujetando la pantalla y saluda: ¡Hola! Capricorn Desktop.">
</p>

<p align="center">
  <a href="https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/actions/workflows/tests.yml"><img src="https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/actions/workflows/tests.yml/badge.svg" alt="Pruebas Windows"></a>
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-1679C5?style=flat-square" alt="Windows 10 y 11">
  <img src="https://img.shields.io/badge/Python-3.12-FFD34E?style=flat-square" alt="Python 3.12">
  <img src="https://img.shields.io/badge/IA%20local-Ollama-62DCC2?style=flat-square" alt="IA local con Ollama">
  <a href="LICENSE"><img src="https://img.shields.io/badge/C%C3%B3digo-MIT-FF365E?style=flat-square" alt="Código original bajo licencia MIT"></a>
</p>

<h1 align="center">Capri, de Cyberpunk a tu escritorio.</h1>

<p align="center">
  <b>Habla con ella. Pon tu música. Que no se te pase la partida.</b><br>
  Voz, conversación con IA local y una compañera de escritorio con la estética de <i>Cyberpunk: Edgerunners</i>.
</p>

<p align="center">
  <a href="#empieza-a-usarla"><b>Instalar Capri</b></a> ·
  <a href="#capri-en-acción">Verla en acción</a> ·
  <a href="#componentes-mínimos-y-recomendados">Requisitos</a> ·
  <a href="docs/README.md">Documentación</a> ·
  <a href="https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/releases">Releases</a>
</p>

---

## Capri en acción

### Tu música, con tu voz

**«Capri, reanuda YouTube».** Controla el vídeo que tienes abierto o elige un resultado de búsqueda. El [puente de Opera y Opera GX](docs/CONECTAR_OPERA.md) conecta Capri con el reproductor y los resultados de YouTube.

<p align="center">
  <a href="docs/media/readme/capri-youtube.webp"><img src="docs/media/readme/capri-youtube.webp" width="100%" alt="YouTube con un vídeo musical abierto y la respuesta real de Capri: Reanudé el vídeo de YouTube."></a>
</p>

**«Pausa Spotify». «Siguiente canción». «Pon mi playlist Cyberpunk».** Usa Spotify desde Capri y [vincula tus playlists](docs/USO.md#elegir-dónde-reproducir-y-qué-resultado-abrir) para pedirlas por su nombre.

<p align="center">
  <a href="docs/media/readme/capri-spotify.webp"><img src="docs/media/readme/capri-spotify.webp" width="100%" alt="Playlist abierta en Spotify y respuesta real de Capri a la orden Pausa Spotify."></a>
</p>

### Sale partida. Capri la acepta.

Activa la **aceptación automática de LoL** y busca desde Capri o desde el propio cliente. Vigila las próximas colas mientras esté abierta; puedes desactivarla cuando quieras. También admite buscar, aceptar y cancelar por voz. [Cómo configurarlo](docs/LEAGUE_OF_LEGENDS.md).

<p align="center">
  <a href="docs/media/readme/capri-lol.webp"><img src="docs/media/readme/capri-lol.webp" width="100%" alt="Cliente de League of Legends abierto y Capri confirmando la activación de la vigilancia de partidas."></a>
  <br><sub>Vigilancia activada en el cliente real. La captura no muestra una partida aceptada. Capri no juega ni selecciona campeones.</sub>
</p>

### Una compañera con su propio estilo

Elige **pantalla flotante o personaje de escritorio** desde el clic derecho. Personaliza el aspecto, el tamaño y los colores. En modo personaje puede moverse, caer y sujetarse a ventanas compatibles; también se asoma por los bordes y tiene llamadas con bromas e invitados. Las interacciones y las travesuras se configuran por separado en **Ajustes → Escritorio**.

<p align="center">
  <img src="docs/media/readme/visor-actual.webp" width="43%" alt="Interfaz actual de Capri en modo pantalla, con su entrada de voz y texto.">
  <img src="docs/media/readme/aspectos-actuales.webp" width="49%" alt="Galería de aspectos de Capri disponible desde los ajustes.">
</p>

La intro aparece sujetando la pantalla y se transforma en el visor. Al cerrar, la despedida llena la pantalla con su efecto de cámara, sincroniza la boca con la voz y da paso a la mano y la estrella. Puedes desactivar las animaciones desde Ajustes.

<p align="center">
  <img src="docs/media/readme/capri-despedida.webp" width="100%" alt="Capri se despide con cielo nocturno, efecto de cámara y el subtítulo Cuídate mucho, choom.">
</p>

<p align="center"><sub>Composiciones con capturas de la aplicación y de los servicios abiertos. <a href="docs/media/readme/README.md">Procedencia y alcance de las imágenes</a>.</sub></p>

## También puedes…

| | Con Capri |
| :--- | :--- |
| **Conversar** | Usa texto o voz y elige un modelo de **Ollama local**. Las órdenes directas funcionan también sin IA. |
| **Hablar en cuatro idiomas** | Español, inglés, portugués de Brasil y japonés. El idioma y la voz se eligen por separado. |
| **Controlar Discord** | Silencia tu micrófono o pide entrar en un canal de voz del servidor abierto. |
| **Moverte por el escritorio** | Abre aplicaciones y sitios, controla ventanas y gestiona archivos con los permisos correspondientes. |
| **Elegir sus límites** | El control ampliado es opcional; las acciones sensibles piden confirmación. Las bromas de ventanas vienen desactivadas. |

## Empieza a usarla

Necesitas **Windows 10/11 y Python 3.12 de 64 bits**. La primera preparación requiere internet. **Para obtener la versión que muestran las capturas, usa el ZIP de `main` y genera su lanzador con los pasos siguientes.** Un lanzador descargado anteriormente contiene la versión de cuando se publicó; volver a abrirlo no descarga el código nuevo.

### 1. Instala Python 3.12

Abre la [página oficial de Python 3.12.10](https://www.python.org/downloads/release/python-31210/) y, en **Files**, elige **Windows installer (64-bit)**. Es el instalador tradicional que utiliza esta guía; evita elegir otra versión o el paquete de Microsoft Store. Hemos recibido un fallo de creación del entorno con la versión de Store y su redirección de carpetas.

Ejecuta el instalador, marca **Add python.exe to PATH** y deja activados el lanzador de Python, `pip` y Tcl/Tk. No basta con descargar el archivo: hay que completar la instalación.

Cierra las terminales que tengas abiertas. Pulsa **Windows + R**, escribe `powershell` y pulsa Enter. En esa ventana pega:

```powershell
py -3.12 --version
```

Debe responder **Python 3.12.x**. Si dice que `py` no se reconoce o **No suitable Python runtime found**, revisa la [ayuda de instalación](docs/INSTALACION.md) antes de continuar. Los comandos van en PowerShell, donde aparece `PS C:\...>`; si ves `>>>`, estás dentro de Python: cierra esa ventana.

### 2. Descarga y extrae Capri

[Descarga el ZIP actualizado de `main`](https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/archive/refs/heads/main.zip). En el Explorador, pulsa **Extraer todo** y abre la carpeta extraída. Entra hasta ver **`empaquetar.py`**, junto a `assets`, `docs` y `src`. Si Windows oculta las extensiones, el archivo aparece como **empaquetar**.

Haz clic en la **barra de dirección del Explorador**, escribe `powershell` y pulsa Enter. Así abres la terminal en la carpeta correcta. Si todavía ves **Herramientas de carpeta comprimida**, vuelve a la carpeta extraída.

### 3. Genera el lanzador

Pega **solo este comando** y espera a que termine:

```powershell
py -3.12 empaquetar.py
```

Se creará la carpeta **`dist`** con **`Abrir Capri.pyw`**. Es normal que ese lanzador no aparezca antes de ejecutar el comando. Si hay un error, detente y consulta la [guía de solución de problemas](docs/INSTALACION.md).

### 4. Instala y abre Capri

En la misma ventana de PowerShell, ejecuta ahora este otro comando:

```powershell
py -3.12 ".\dist\Abrir Capri.pyw"
```

Espera la preparación inicial: instala las dependencias y descarga los modelos de reconocimiento. Después crea el acceso directo **Capri** en el escritorio. No requiere administrador ni se añade automáticamente al inicio de Windows.

En **Ajustes → Micrófono**, selecciona tu entrada y ajusta la sensibilidad. Di **«Capri, abre la calculadora»** o pulsa **F8** para hablar. Para conversar, activa Ollama desde **Ajustes → IA y servicios**.

**Para actualizar:** cierra Capri, descarga y extrae de nuevo el ZIP de `main` y repite los pasos 3 y 4 desde esa carpeta nueva. Usa el lanzador recién generado en `dist`, no el antiguo de Descargas. Al actualizar sobre la misma instalación conserva las preferencias.

<details>
<summary><b>¿Prefieres una Release ya empaquetada?</b></summary>

Las [Releases](https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/releases) pueden ir por detrás de `main`. Comprueba la fecha y sus notas: las capturas de esta página corresponden a `main`.

Con Python 3.12 ya instalado, descarga **Abrir Capri.pyw** de la Release elegida; GitHub puede llamarlo `Abrir.Capri.pyw`. Abre PowerShell en la carpeta donde lo descargaste y ejecuta `py -3.12 "Abrir.Capri.pyw"`, usando el nombre exacto del archivo. No necesitas `empaquetar.py` para esa descarga. Ese lanzador instala la versión de esa Release y también requiere internet para la primera preparación.

</details>

¿Aparece **«No se pudo completar la preparación»**? Consulta [errores frecuentes y cómo abrir el registro](docs/INSTALACION.md#no-se-pudo-completar-la-preparación).

## Componentes mínimos y recomendados

**Puedes usar Capri sin una tarjeta gráfica dedicada.** La carga adicional depende sobre todo de si activas IA local, del tamaño del modelo y del reconocimiento de voz elegido.

| Componente | Punto de partida · personaje y órdenes | Recomendado · voz + IA local pequeña | Más margen · juegos + IA local |
| :--- | :--- | :--- | :--- |
| **Procesador** | CPU x64, 2 núcleos / 4 hilos | 4 núcleos / 8 hilos; AVX2 recomendado | 6 núcleos / 12 hilos o superior |
| **RAM del equipo** | 8 GB | 16 GB para Whisper base y un modelo de unos 3B cuantizado | 32 GB para juegos o modelos de 7B–8B |
| **Gráficos** | Integrados | GPU opcional; la IA también funciona por CPU, con más espera | GPU compatible con Ollama; unos 8 GB de VRAM o más dan margen según el modelo |
| **Espacio libre** | Reserva unos 4 GB para entorno y reconocimiento | SSD y unos 12 GB, incluyendo Ollama y un modelo pequeño | SSD y 20 GB o más para varios modelos |
| **Pantalla** | 1280 × 720 | 1920 × 1080 | Según tu escritorio |
| **Audio** | Salida de audio; micrófono para hablarle | Micrófono con poco ruido | Igual que el recomendado |

Estas cifras son una **guía orientativa, no mínimos de rendimiento certificados**. No se garantiza una latencia concreta: influyen el modelo, la memoria disponible y los otros programas abiertos. Para empezar con IA, una combinación equilibrada es **16 GB de RAM, SSD, Whisper base y un modelo de unos 3B**. El instalador propone `llama3.2:3b` si todavía no elegiste otro.

Ollama requiere **Windows 10 22H2 o posterior**, al menos 4 GB para su instalación y espacio adicional para los modelos. Comprueba sus [requisitos de Windows](https://docs.ollama.com/windows) y [GPU compatibles](https://docs.ollama.com/gpu). El reconocimiento de Capri usa Whisper por **CPU/int8**; una GPU para Ollama no acelera automáticamente ese reconocimiento. Base es más ligero que Small; consulta también las [mediciones de faster-whisper](https://github.com/SYSTRAN/faster-whisper#benchmark).

## Prueba estas frases

Di «Capri» y la petición en una misma frase, o utiliza la tecla para hablar. **F8** es la tecla inicial y puedes cambiarla en Ajustes. **Esc** detiene la respuesta o cancela una animación compatible.

| Para… | Puedes decir… |
| :--- | :--- |
| Abrir una aplicación | «Capri, abre la calculadora». |
| Ir a un sitio | «Abre YouTube» o «abre Netflix». |
| Controlar música | «Pausa Spotify» o «siguiente canción». |
| Elegir un vídeo | «Reproduce el segundo resultado en YouTube». |
| Silenciarte en Discord | «Mutéame el Discord» o «desmutéame en Discord». |
| Entrar en un canal de voz | «Únete al canal de voz General del servidor Amigos en Discord». |
| Vigilar partidas de LoL | «Activa la aceptación automática del LoL». |
| Usar la cola de LoL | «Busca partida en LoL» o «acepta partida en LoL». |
| Conversar | «Cuéntame algo» — con IA local activada. |
| Apagar el equipo | «Apaga el computador» — con control ampliado y confirmación. |

Las órdenes dependen de la aplicación y de sus controles disponibles. Capri informa cuando no puede confirmar una acción. No opera cualquier programa de cualquier manera.

## Configúrala a tu manera

**Idioma y voz son independientes.** Puedes mantener el texto en español y elegir una voz brasileña, por ejemplo. La elección de voz se conserva al cambiar el idioma; **Seguir el idioma de Capri** devuelve la selección automática. La pronunciación entre idiomas depende de la voz elegida.

| Integración | Qué necesitas | Guía |
| :--- | :--- | :--- |
| **IA local** | Ollama y un modelo instalado. Puedes elegir otro desde Ajustes. | [Modelos y reconocimiento](docs/COMPARACION_MODELOS.md) |
| **Micrófono** | Entrada seleccionada, permiso de Windows y modelo de reconocimiento. | [Voz y primeros pasos](docs/USO.md) |
| **Spotify** | Aplicación de escritorio y sesión iniciada. | [Uso y reproducción](docs/USO.md#elegir-dónde-reproducir-y-qué-resultado-abrir) |
| **YouTube** | Opera/Opera GX; el puente amplía los controles del reproductor y de resultados. | [Conectar Opera](docs/CONECTAR_OPERA.md) |
| **Discord** | Cliente de escritorio y sesión iniciada. Sus controles deben ser accesibles; para unirte, deja abierto el servidor. | [Discord](docs/USO.md#discord) |
| **League of Legends** | Cliente abierto y una sala preparada. La aceptación automática es opcional. No juega ni elige campeones. | [Colas y aceptación](docs/LEAGUE_OF_LEGENDS.md) |

## Tus datos y tus permisos

| Función | Dónde se procesa |
| :--- | :--- |
| Conversación con un modelo instalado | En tu equipo, mediante Ollama local. |
| Reconocimiento del micrófono | En tu equipo, con los modelos descargados. |
| Voz natural | Microsoft recibe el texto que Capri va a leer. Requiere conexión. |
| Voz de Windows | En tu equipo, si tienes instalada una voz compatible con el idioma/acento. |
| Búsquedas y reproducción online | En los servicios que abras o controles. |

El **control ampliado viene desactivado**. Al habilitarlo, las operaciones sensibles requieren confirmar el objetivo; los borrados compatibles van a la Papelera. El modelo decide entre acciones definidas: sus respuestas no se ejecutan como código de consola. Discord usa la sesión ya abierta y no pide tu contraseña ni un token de cuenta.

Los ajustes, playlists vinculadas, diagnósticos y modelos descargados se guardan localmente y quedan fuera de Git. El historial del chat dura durante la sesión. Más detalles en la [guía de uso](docs/USO.md).

## Preguntas rápidas

<details>
<summary><b>¿Funciona sin Ollama?</b></summary>

Sí. El personaje y las órdenes directas no requieren conversación con un modelo. Ollama añade conversación e interpretación con contexto.

</details>

<details>
<summary><b>¿Funciona sin internet?</b></summary>

Después de descargar las dependencias y modelos, el reconocimiento y la conversación local pueden funcionar sin conexión. La voz natural, las descargas y los servicios web necesitan internet. Puedes usar una voz de Windows instalada para lectura local.

</details>

<details>
<summary><b>¿Las voces son las del anime?</b></summary>

Son voces sintéticas configuradas para la aplicación, no grabaciones ni reproducciones exactas de los intérpretes. La despedida usa la voz habitual que hayas elegido para Capri. [Perfiles invitados](docs/VOCES_INVITADAS.md).

</details>

<details>
<summary><b>¿Puedo apagar las llamadas o las travesuras?</b></summary>

Sí. En Ajustes → Escritorio puedes controlar los asomos, las llamadas y las bromas de ventanas por separado. Las bromas que minimizan ventanas están desactivadas inicialmente. La despedida animada se omite si desactivas las animaciones.

</details>

## Construyamos la siguiente versión

¿Tienes una idea para Capri o encontraste una frase que no entiende? Abre una [propuesta o reporte](https://github.com/TheSniperS2/Capri-Capricorn-Para-Escritorio/issues/new/choose) con los pasos, lo que esperabas y lo que ocurrió. Si te gusta el proyecto, una estrella ayuda a que más chooms lo encuentren.

**[Guía de contribución](CONTRIBUTING.md) · [Mapa del proyecto](docs/ARQUITECTURA.md) · [Cambios](CHANGELOG.md) · [Documentación completa](docs/README.md)**

<details>
<summary><b>Preparar el entorno de desarrollo</b></summary>

En Windows con Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe empaquetar.py
.\.venv\Scripts\python.exe scripts/ejecutar_pruebas.py
```

Modifica los módulos de `src/`; `dist/` es una salida generada y no se versiona. Las pruebas automatizadas no sustituyen las comprobaciones de micrófono e integraciones reales. La [procedencia de los medios](docs/media/readme/README.md) distingue las capturas actuales de los recursos históricos generados por script.

</details>

---

<p align="center"><b>«Cuídate mucho, choom.»</b></p>

Proyecto de aficionado, independiente y **no oficial**. El código original está bajo [licencia MIT](LICENSE). Los personajes, marcas e imágenes de terceros conservan sus propios derechos; consulta [créditos y avisos](THIRD_PARTY_NOTICES.md) y las [referencias visuales](docs/REFERENCIAS.md). Las ilustraciones derivadas y sus prompts se documentan en [arte y animación](docs/ARTE_ANIMADO.md).
