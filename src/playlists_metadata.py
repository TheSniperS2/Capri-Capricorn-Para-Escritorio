"""Vista previa opcional de Spotify; guardar y reproducir no dependen de ella."""
import hashlib
import io
import json
import os
import re
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
from playlists import uri_playlist

_cerrojo=threading.RLock()


def enlace_web(uri):return 'https://open.spotify.com/playlist/'+uri_playlist(uri).rsplit(':',1)[1]


def archivo_portada(uri,carpeta):
    identidad=hashlib.sha256(uri_playlist(uri).encode()).hexdigest()[:32]
    return Path(carpeta)/'cache'/'playlists'/(identidad+'.png')


def guardar_portada(imagen,uri,carpeta,solo_si_falta=False):
    ruta=archivo_portada(uri,carpeta)
    mini=ImageOps.fit(imagen.convert('RGB'),(256,256),method=Image.Resampling.LANCZOS)
    with _cerrojo:
        if solo_si_falta and ruta.is_file():return ruta
        ruta.parent.mkdir(parents=True,exist_ok=True)
        fd,temporal=tempfile.mkstemp(prefix='.portada-',suffix='.png',dir=ruta.parent);os.close(fd)
        try:mini.save(temporal,'PNG');os.replace(temporal,ruta)
        finally:Path(temporal).unlink(missing_ok=True)
    return ruta


def imagen_embed(uri):
    """Spotify a veces publica la imagen solo en los datos de su reproductor."""
    url='https://open.spotify.com/embed/playlist/'+uri_playlist(uri).rsplit(':',1)[1]
    with urlopen(Request(url,headers={'User-Agent':'Capri/1.0','Accept':'text/html'}),timeout=3) as respuesta:
        contenido=respuesta.read(2*1024*1024+1)
    if len(contenido)>2*1024*1024:return ''
    m=re.search(r'<script\b[^>]*\bid="__NEXT_DATA__"[^>]*>(.*?)</script>',contenido.decode('utf-8'),re.S)
    if not m:return ''
    entidad=json.loads(m[1]).get('props',{}).get('pageProps',{}).get('state',{}).get('data',{}).get('entity',{})
    if entidad.get('uri')!=uri_playlist(uri):return ''
    imagenes=entidad.get('visualIdentity',{}).get('image',[])
    candidatas=[i for i in imagenes if isinstance(i,dict) and isinstance(i.get('maxWidth'),int) and 0<i['maxWidth']<=4096]
    return str(max(candidatas,key=lambda i:i['maxWidth']).get('url') or '') if candidatas else ''


def consultar(uri,carpeta):
    """oEmbed público: sin OAuth/cookies. Las listas privadas pueden no dar título."""
    url='https://open.spotify.com/oembed?'+urlencode({'url':enlace_web(uri)})
    with urlopen(Request(url,headers={'User-Agent':'Capri/1.0','Accept':'application/json'}),timeout=3) as respuesta:
        datos=respuesta.read(64*1024+1)
        if len(datos)>64*1024:raise ValueError('Respuesta demasiado grande.')
        meta=json.loads(datos)
        if not isinstance(meta,dict):raise ValueError('Vista previa inválida.')
    titulo=' '.join(str(meta.get('title') or '').split())[:200]
    imagen=str(meta.get('thumbnail_url') or '');ruta=archivo_portada(uri,carpeta)
    if not imagen and not ruta.is_file():
        try:imagen=imagen_embed(uri)
        except (OSError,ValueError,AttributeError,TypeError):pass
    p=urlsplit(imagen)
    permitido=p.hostname and (p.hostname.endswith('.scdn.co') or p.hostname.endswith('.spotifycdn.com'))
    if not ruta.is_file() and p.scheme=='https' and permitido and not p.username and not p.password and p.port in (None,443):
        try:
            with urlopen(Request(imagen,headers={'User-Agent':'Capri/1.0'}),timeout=3) as respuesta:contenido=respuesta.read(2*1024*1024+1)
            if len(contenido)<=2*1024*1024:
                with Image.open(io.BytesIO(contenido)) as original:
                    if max(original.size)<=4096:
                        guardar_portada(original,uri,carpeta,solo_si_falta=True)
        except (OSError,ValueError,Image.DecompressionBombError):pass
    return titulo
