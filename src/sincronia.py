"""Posición del texto según el reloj de reproducción y marcas de voz."""
import html
import re

PASO_BOCA=.02


def actividad_boca(archivo):
    """Actividad de la voz por ventanas de 20 ms, sin modificar el audio."""
    import av
    import numpy as np
    conversor=av.AudioResampler(format='s16',layout='mono',rate=16000)
    trozos=[]
    with av.open(str(archivo)) as entrada:
        for frame in entrada.decode(audio=0):
            for mono in conversor.resample(frame):trozos.append(mono.to_ndarray().reshape(-1))
        for mono in conversor.resample(None):trozos.append(mono.to_ndarray().reshape(-1))
    if not trozos:return ()
    muestras=np.concatenate(trozos).astype(np.float64)/32768.
    n=round(PASO_BOCA*16000)
    muestras=np.pad(muestras,(0,(-len(muestras))%n))
    rms=np.sqrt(np.mean(muestras.reshape(-1,n)**2,axis=1))
    umbral=max(.0015,float(rms.max())*.06)
    return tuple(bool(nivel>umbral) for nivel in rms)


def boca_en_posicion(actividad,segundos):
    indice=int(segundos/PASO_BOCA)
    return 0<=segundos and 0<=indice<len(actividad) and actividad[indice]

def alinear_marcas(texto,eventos):
    marcas=[];cursor=0
    for evento in eventos:
        palabra=html.unescape(evento.get('text',''))
        if not palabra:continue
        m=re.search(re.escape(palabra),texto[cursor:],flags=re.IGNORECASE)
        if not m:continue
        inicio=cursor+m.start();fin=cursor+m.end()
        marcas.append((evento['offset']/10_000_000,max(.01,evento.get('duration',0)/10_000_000),inicio,fin))
        cursor=fin
    return marcas

def avance_texto(texto,posicion,duracion,marcas=()):
    if marcas:
        previo=0
        for offset,largo,inicio,fin in marcas:
            if posicion<offset:return previo
            if posicion<offset+largo:
                return min(len(texto),inicio+int((fin-inicio)*max(0,(posicion-offset)/largo)))
            previo=fin
        return len(texto)
    if duracion>0:return min(len(texto),max(0,int(len(texto)*posicion/duracion)))
    return 0
