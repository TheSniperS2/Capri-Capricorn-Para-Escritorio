"""Diseño común del reproductor compacto para Tk y las animaciones."""
import base64
import io
import math
import time
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageOps,ImageFont
from tema_ui import color
from fuentes import FAMILIA
from idiomas import ui,idioma_actual

ANCHO=440
ALTO=198
ALTO_SENTADA=150

@lru_cache(maxsize=16)
def fuente_raster(tamano,negrita,japones):
    ruta=Path('C:/Windows/Fonts/YuGothB.ttc') if japones else Path(__file__).parent/'assets/fonts'/('ChakraPetch-Bold.ttf' if negrita else 'ChakraPetch-Regular.ttf')
    if not ruta.exists() and not japones:ruta=Path(__file__).parents[1]/'assets/fonts'/ruta.name
    try:return ImageFont.truetype(str(ruta),tamano)
    except OSError:return ImageFont.load_default(size=tamano)

def linea(c,texto,fuente,ancho,s):
    texto=' '.join(str(texto).split())[:2000]
    if hasattr(c,'tk'):
        from tkinter.font import Font
        f=Font(root=c,font=(('Yu Gothic UI',)+fuente[1:]) if idioma_actual()=='ja' else fuente)
        medir=f.measure;limite=ancho*s
    else:
        escala=getattr(c,'s',1)
        f=fuente_raster(max(1,round(fuente[1]*4/3*escala)),'bold' in fuente,idioma_actual()=='ja')
        medir=f.getlength;limite=ancho*escala
    if medir(texto)<=limite:return texto
    while texto and medir(texto+'…')>limite:texto=texto[:-1]
    return texto.rstrip()+'…'

def tiempos(sesion,ahora=None):
    duracion=sesion.get('duracion',0);posicion=sesion.get('posicion',0)
    if sesion.get('estado')=='Playing':posicion+=max(0,(time.monotonic() if ahora is None else ahora)-sesion.get('_fecha',time.monotonic()))*sesion.get('velocidad',1)
    return (min(duracion,max(0,posicion)),duracion) if duracion>0 else (0,0)

def reloj(segundos):
    if not math.isfinite(segundos):return '--:--'
    s=int(max(0,segundos));h,s=divmod(s,3600);m,s=divmod(s,60)
    return f'{h}:{m:02}:{s:02}' if h else f'{m}:{s:02}'

def portada(sesion):
    try:
        datos=sesion.get('caratula','')
        if not datos or len(datos)>1400000:return None
        with Image.open(io.BytesIO(base64.b64decode(datos,validate=True))) as im:
            if im.width*im.height>8000000:return None
            im=im.convert('RGBA')
            if sesion.get('proveedor')=='Spotify' and im.width==im.height and im.width>=64:
                # Windows recibe de Spotify una tarjeta con portada centrada y firma debajo.
                # Detectar ese marco evita recortar portadas cuadradas que ya llegan limpias.
                w=im.width;m=round(w*7/64);lado=w-2*m
                bandas=list(im.crop((0,0,max(1,m//2),lado)).getdata())+list(im.crop((w-max(1,m//2),0,w,lado)).getdata())
                pie=list(im.crop((0,lado,w,w)).getdata())
                oscuro=lambda p:max(p[:3])<24
                if (sum(map(oscuro,bandas))>len(bandas)*.97 and sum(map(oscuro,pie))>len(pie)*.55
                        and sum(min(p[:3])>220 for p in pie)>len(pie)*.025):
                    im=im.crop((m,0,w-m,lado))
            return ImageOps.fit(im,(168,168),method=Image.Resampling.LANCZOS)
    except (ValueError,OSError,Image.DecompressionBombError):return None

def dibujar_multimedia(c,sesion=None,escala_fuente=1,ocupado=False,error='',cantidad=0):
    d=sesion or {};s=escala_fuente
    def fuente(n,*estilo):return (FAMILIA,max(6,round(n*s)),*estilo)
    borde=color('#713b9d');acento=color('#ff9eaf');suave=color('#bb929f')
    c.create_polygon(2,13,13,2,425,2,438,15,438,185,427,196,2,196,
                     fill=color('#09131f'),outline=borde,width=1)
    c.create_line(14,5,92,5,fill=acento,width=2)
    c.create_line(435,21,435,61,fill=acento,width=2)
    for y in range(10,194,4):c.create_line(5,y,434,y,fill=color('#101a29'))
    c.create_text(24,23,text='REPRODUCIENDO' if d.get('estado')=='Playing' else 'MÚSICA / CAPRI',anchor='w',fill=acento,font=fuente(7,'bold'))
    pos,dur=tiempos(d)
    c.create_text(24,43,text=(reloj(pos)+' / '+reloj(dur)) if dur else '--:-- / --:--',anchor='w',fill=suave,font=fuente(8))
    c.create_text(335,21,text=d.get('proveedor','').upper() if d else 'SIN SESIÓN',anchor='e',fill=acento,font=fuente(7,'bold'))
    if cantidad>1:c.create_polygon(342,17,347,21,342,25,fill=acento,outline='')
    c.create_rectangle(354,18,416,80,fill=color('#111b2b'),outline=borde)
    if not d.get('caratula'):
        for i,h in enumerate((12,24,32,20,14)):c.create_rectangle(368+i*7,49-h/2,371+i*7,49+h/2,fill=acento,outline='')
    c.create_line(420,11,426,17,fill=suave,width=1.3);c.create_line(420,17,426,11,fill=suave,width=1.3)
    c.create_text(24,100,text=linea(c,d.get('titulo') or ui('Nada en reproducción'),fuente(16,'bold'),390,s),anchor='w',fill=color('#eff9ff'),font=fuente(16,'bold'),traducir=False)
    subtitulo=ui(error) if error else (d.get('artista') or ui('Reproducción en el navegador' if d else 'Abre Spotify o un vídeo en tu navegador.'))
    c.create_text(24,125,text=linea(c,subtitulo,fuente(9),390,s),anchor='w',fill=acento,font=fuente(9),traducir=False)
    c.create_line(24,147,416,147,fill=color('#294759'),width=2)
    px=24+392*pos/dur if dur else 24
    if dur:c.create_line(24,147,px,147,fill=acento,width=2)
    c.create_oval(px-5,142,px+5,152,fill=color('#eff9ff'),outline=acento)
    for accion,x in (('anterior',182),('pausa' if d.get('estado')=='Playing' else 'reanudar',222),('siguiente',262)):
        habilitado=bool(d.get('controles',{}).get(accion)) or bool(d.get('_pendiente') and accion in ('pausa','reanudar'))
        tinta=acento if habilitado else color('#526070')
        if accion in ('pausa','reanudar'):c.create_oval(x-16,158,x+16,190,fill=tinta if habilitado else color('#172334'),outline=borde)
        simbolo=color('#09131f') if accion in ('pausa','reanudar') and habilitado else tinta
        if accion=='pausa':
            for dx in (-4,2):c.create_rectangle(x+dx,169,x+dx+2,180,fill=simbolo,outline='')
        elif accion=='reanudar':c.create_polygon(x-3,168,x+5,174,x-3,181,fill=simbolo,outline='')
        else:
            signo=-1 if accion=='anterior' else 1
            c.create_polygon(x-4*signo,168,x+4*signo,174,x-4*signo,181,fill=simbolo,outline='')
            c.create_line(x+7*signo,168,x+7*signo,181,fill=simbolo,width=2)
    if cantidad>1:
        for y in (169,174,179):c.create_line(26,y,40,y,fill=suave,width=1)
    c.create_text(414,174,text='ESCUCHANDO' if d.get('estado')=='Playing' else 'EN PAUSA',anchor='e',fill=suave,font=fuente(7))
