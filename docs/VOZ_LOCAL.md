# Voces de Capri

El idioma se cambia en **Ajustes → Escritorio → Idioma de Capri**. La voz española
original se conserva: Dalia con el ajuste clásico de Capri. Portugués y japonés
también mantienen sus voces habituales. Las versiones personales V1 y V2 se usan
únicamente en inglés. Las voces invitadas mantienen su función.

## Inglés: Capri V1 y Capri V2

En **Ajustes → Voz**, al elegir inglés, aparecen dos versiones con una indicación breve de su espera. La interfaz omite los mensajes adicionales sobre versiones y voces de otros idiomas. Este documento conserva los detalles de funcionamiento:

- **Capri V1 · Conversación ágil:** la opción rápida actual. Microsoft Edge TTS
  genera la base inglesa Aria y OpenVoice aplica en el equipo el timbre preparado
  con las muestras V2. Envía a Microsoft el texto de la respuesta, no las muestras.
  En una prueba con motor preparado, el primer fragmento nuevo tardó unos 2–3
  segundos; no incluye reconocimiento, IA ni carga inicial.
- **Capri V2 · Voz de referencia:** el generador Qwen y el perfil V2 aprobados.
  Genera el audio en este PC sin enviar el texto a un servicio de voz. Una frase
  nueva puede tardar alrededor de un minuto en el equipo probado. La IA de
  conversación conserva su configuración independiente.

V1 y V2 difieren en timbre y entonación. V1 no garantiza sonar idéntica a V2.
Cambiar la versión inglesa no cambia la voz española; se recuerda la versión
para la próxima vez que uses inglés.

## Volumen y reproducción

El volumen es el control de silencio: **0% silencia a Capri**. Ya no hay un
interruptor separado «Responder en voz alta». Silenciar desde el menú Voz también
pone el volumen en cero; reactivarlo recupera el volumen anterior. Las preferencias
antiguas de voz apagada se mantienen como volumen cero.

La velocidad se ajusta conservando el tono. Puedes cancelar durante la generación
o reproducción; el seguimiento de voz espera al último fragmento. Las frases
guardadas se reutilizan desde una caché local. V1 precarga el conversor cuando
usas inglés y tienes volumen; silenciar o cerrar libera el motor. Al cambiar de
versión se cancela la respuesta anterior y se cierra su proceso.

Los errores de las versiones personales se informan sin cambiar su identidad a
otra voz. Español y los otros idiomas conservan su motor habitual y su respaldo
de Windows cuando corresponde.

## Recursos preparados por instalación

El paquete contiene el cliente y los motores ligeros, sin modelos, perfiles,
muestras, caché ni ajustes personales. No descarga modelos ni instala PyTorch al
abrir Capri. Sin el perfil preparado se conserva la voz habitual del idioma; la
interfaz lo indica.

La configuración privada **voz-ingles-local.json** apunta al Python separado,
modelo y perfil Qwen, caché y un bloque **rapida** con las rutas del conversor.
No borres archivos referenciados: ambos conjuntos de recursos se conservan.
Las dependencias pesadas permanecen fuera del entorno principal.

El diagnóstico del trabajador se guarda en **motor.log**, dentro de la caché.
[OpenVoice](https://github.com/myshell-ai/OpenVoice) y
[Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS).
