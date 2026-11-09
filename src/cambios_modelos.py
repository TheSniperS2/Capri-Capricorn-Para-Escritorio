"""Comparaciones para confirmar cambios antes de alterar las preferencias."""
import re
from idiomas import ui

TEXTOS=(
 'El modelo elegido tiene más parámetros. Puede necesitar más memoria y tardar más al responder.',
 'El modelo elegido tiene menos parámetros. Puede consumir menos y responder antes, pero perder detalle en algunas respuestas.',
 'El consumo y la rapidez dependen del tamaño del modelo y de tu equipo. Cambiar de familia no garantiza una mejora.',
 'La calidad de las respuestas puede variar. La primera respuesta puede tardar más mientras se carga el modelo.',
 'Whisper Small suele reconocer mejor frases y nombres difíciles, pero necesita más memoria y tiempo que Base.',
 'Whisper Base consume menos memoria y suele responder antes que Small, pero puede perder precisión con frases o nombres difíciles.',
 'Vosk usa menos recursos y responde rápido. Puede reconocer peor los nombres en inglés y las frases difíciles.',
 'Whisper suele reconocer mejor frases y nombres en inglés que Vosk, pero utiliza más recursos y puede tardar más.',
 'Este cambio afecta a cómo se entiende tu voz; no cambia la voz con la que responde Capri.',
)


def parametros(modelo):
    detalle=modelo.get('details',{}) if isinstance(modelo,dict) else {}
    if not isinstance(detalle,dict):return None
    m=re.fullmatch(r'\s*(\d+(?:[.,]\d+)?)\s*([BM])\s*',str(detalle.get('parameter_size','')),re.I)
    if m:return float(m[1].replace(',','.'))*(1e9 if m[2].upper()=='B' else 1e6)


def comparar_modelos(actual,nuevo,modelos):
    a=parametros(modelos.get(actual,{}));b=parametros(modelos.get(nuevo,{}))
    if a and b and b>a*1.15:texto=TEXTOS[0]
    elif a and b and b<a*.85:texto=TEXTOS[1]
    else:texto=TEXTOS[2]
    return ui(texto)+'\n\n'+ui(TEXTOS[3])


def comparar_reconocimiento(actual_motor,actual_modelo,nuevo_motor,nuevo_modelo):
    if nuevo_motor=='rapido':texto=TEXTOS[6]
    elif actual_motor=='rapido':
        texto=TEXTOS[7]
        if nuevo_modelo=='small':return ui(texto)+'\n\n'+ui(TEXTOS[4])
    elif nuevo_modelo=='small':texto=TEXTOS[4]
    else:texto=TEXTOS[5]
    return ui(texto)+'\n\n'+ui(TEXTOS[8])
