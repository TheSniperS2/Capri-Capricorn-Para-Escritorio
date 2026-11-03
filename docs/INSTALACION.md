# Instalación y actualización de Capri

Para instalar la versión actual, sigue los [pasos del README](../README.md#empieza-a-usarla). Usa Windows 10/11 y el instalador tradicional de **Python 3.12 de 64 bits**, con el lanzador, `pip` y Tcl/Tk. Los comandos se ejecutan en PowerShell.

## Qué descarga tienes

- **ZIP del código de `main`:** debes extraerlo y ejecutar `py -3.12 empaquetar.py` desde la carpeta donde está ese archivo. Después ejecuta `py -3.12 ".\dist\Abrir Capri.pyw"` como un comando separado.
- **Lanzador de una Release:** se llama `Abrir Capri.pyw` o `Abrir.Capri.pyw`. Ya contiene el paquete de esa Release; no necesita empaquetarse, pero puede ser anterior a las imágenes del README.
- **Acceso directo Capri:** abre la aplicación ya instalada. No descarga una actualización por sí solo.

## No aparece Abrir Capri

En el ZIP del código, el lanzador se genera dentro de **dist** al ejecutar `empaquetar.py`. Ese archivo puede aparecer como **empaquetar** si Windows oculta las extensiones; está junto a las carpetas `assets`, `docs` y `src`.

Primero pulsa **Extraer todo**. No ejecutes los comandos dentro del ZIP. Entra en la carpeta extraída hasta ver `empaquetar.py`, escribe `powershell` en la barra de dirección del Explorador y pulsa Enter.

## py no se reconoce o no encuentra Python 3.12

Son dos problemas distintos:

| Mensaje | Qué comprobar |
| --- | --- |
| «El término py no se reconoce» | El lanzador no está disponible en esa terminal. Instala Python 3.12 con el lanzador activado y vuelve a abrir PowerShell. No demuestra por sí solo que no tengas ningún Python instalado. |
| «No suitable Python runtime found» | El lanzador existe, pero no encuentra Python 3.12. Completa su instalación; tener otra versión no sustituye este paso. |
| «SyntaxError» y aparece `>>>` | Pegaste el comando dentro de Python. Cierra esa ventana y abre PowerShell con Windows + R → `powershell`. |
| No puede abrir `empaquetar.py` | Comprueba que PowerShell está en la carpeta extraída donde aparece ese archivo. |

Comprueba la instalación con **un solo comando**:

```powershell
py -3.12 --version
```

Debe responder `Python 3.12.x`. Ejecuta cada comando de la guía por separado; espera a que termine uno antes de pegar el siguiente.

## No se pudo completar la preparación

Es un aviso general: puede fallar la creación del entorno, la instalación de dependencias, una descarga o el arranque. El mensaje por sí solo no permite atribuirlo a la RAM ni a la conexión.

1. Guarda una captura de la ventana completa, incluido el detalle que aparece debajo del aviso.
2. Pulsa **Windows + R**, pega la siguiente ruta y pulsa Enter. **Esta ruta no se pega como comando en PowerShell.**

   ```text
   %LOCALAPPDATA%\Capri
   ```

3. Busca **instalacion.log**, que puede aparecer como **instalacion**, y ábrelo con el Bloc de notas. Envía el primer error y las últimas líneas del intento más reciente. Si el detalle menciona **arranque.log**, revisa también ese archivo.

AppData está oculta normalmente. Windows + R abre la ubicación sin necesidad de mostrar las carpetas ocultas. Si el Bloc de notas ofrece crear un archivo que no existe, cancela: necesitamos el registro que escribió el instalador.

### Si utilizabas Python 3.12 de Microsoft Store

Su [redirección de carpetas está documentada por Python](https://docs.python.org/3.12/using/windows.html#known-issues). El registro puede estar dentro de la carpeta privada del paquete. Prueba esta ruta en **Windows + R**:

```text
%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\Local\Capri
```

Esta ubicación es específica del paquete de Store; que no exista en otro equipo no significa que Capri esté dañada.

Si prefieres abrir esa misma ubicación desde **PowerShell**, el comando completo es:

```powershell
explorer "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\Local\Capri"
```

### No pyvenv.cfg file

Este error indica que Python no encuentra la configuración de su entorno virtual. Se ha recibido un registro en el que aparece después de una redirección de la instalación de Store; ese caso no demuestra que todas las instalaciones de Store fallen ni que todo error de preparación tenga la misma causa.

Cierra el preparador, instala Python 3.12 con el **Windows installer (64-bit)** de la [página oficial de Python 3.12.10](https://www.python.org/downloads/release/python-31210/) y vuelve a abrir PowerShell. Comprueba `py -3.12 --version` y ejecuta el lanzador actualizado con `py -3.12`, como indica el README.

Si vuelve a fallar, comparte el registro del nuevo intento. El instalador actual puede reutilizar un entorno incompleto si ya existe su ejecutable; reintentar no garantiza repararlo. No borres toda la carpeta Capri como primer paso: puede contener tus preferencias y modelos.

## Abre una versión antigua

El lanzador contiene una versión concreta de Capri. Abrir un lanzador antiguo no descarga automáticamente el código de `main` y puede volver a instalar esa versión anterior.

Para actualizar, cierra Capri y sigue los pasos del README con un ZIP nuevo de `main`. Genera y abre **el nuevo archivo de dist**. No vuelvas a ejecutar el lanzador viejo de Descargas. Las preferencias se conservan al actualizar sobre la misma instalación; una instalación realizada con otro Python puede haber quedado en una ubicación diferente.
