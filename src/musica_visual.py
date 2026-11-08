"""Pose de escucha del visor y balanceo suave del arte de Capri."""
import math
import threading
import time
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageOps,ImageChops,ImageFilter

FOTOGRAMAS_ESCUCHA=72
FPS_ESCUCHA=30


@lru_cache(maxsize=1)
def arte_escucha():
    base=Path(__file__).resolve().parent
    for ruta in (base/'assets/capri-escuchando-musica-v3.png',base.parent/'assets/capri-escuchando-musica-v3.png'):
        try:
            with Image.open(ruta) as im:
                arte=im.convert('RGBA')
            # El pelo de esta ilustración llega 12 grados más magenta que el original.
            # Corregir solo el rosa saturado: ojos, verdes, negros y motas se conservan.
            hsv=arte.convert('RGB').convert('HSV');h,s,v=hsv.split()
            rosa=h.point(lambda n:255 if 232<=n<=247 else 0)
            mascara=ImageChops.multiply(rosa,s.point(lambda n:255 if n>150 else 0))
            mascara=ImageChops.multiply(mascara,v.point(lambda n:255 if n>100 else 0))
            corregida=Image.merge('HSV',(h.point(lambda n:(n+9)%256),s.point(lambda n:min(255,n+3)),v)).convert('RGBA')
            return Image.composite(corregida,arte,mascara)
        except OSError:continue
    return None


@lru_cache(maxsize=4)
def _base_escucha(tamano):
    arte=arte_escucha()
    if arte is None:return None
    return ImageOps.fit(arte,tamano,method=Image.Resampling.LANCZOS)


@lru_cache(maxsize=4)
def _escena_escucha(tamano):
    im=_base_escucha(tamano)
    if im is None:return None
    w,h=tamano
    # Pesos suaves del personaje, separados del fondo gris azulado.
    r,g,b=im.convert('RGB').split();maximo=ImageChops.lighter(ImageChops.lighter(r,g),b)
    saturacion=im.convert('RGB').convert('HSV').split()[1]
    figura=ImageChops.lighter(saturacion.point(lambda n:255 if n>125 else 0),maximo.point(lambda n:255 if n<28 else 0))
    figura=figura.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(max(2,w/80)))
    pelo=ImageChops.multiply(r.point(lambda n:255 if n>120 else 0),g.point(lambda n:255 if n<100 else 0))
    pelo=pelo.filter(ImageFilter.GaussianBlur(max(2,w/70)))
    paso=max(8,round(w/24));xs=list(range(0,w,paso))+[w];ys=list(range(0,h,paso))+[h]
    puntos={}
    for y in ys:
        for x in xs:
            px=min(w-1,x);py=min(h-1,y)
            puntos[x,y]=(figura.getpixel((px,py))/255,pelo.getpixel((px,py))/255)
    return im,xs,ys,puntos


def _mover_escucha(escena,fase):
    im,xs,ys,puntos=escena;w,h=im.size
    t=(fase%FOTOGRAMAS_ESCUCHA)/FOTOGRAMAS_ESCUCHA*math.tau
    angulo=math.radians(2.2*math.sin(t)+.55*math.sin(4*t))
    coseno=math.cos(angulo);seno=math.sin(angulo);sx=w/320;sy=h/210
    mapeo={}
    for (x,y),(figura,pelo) in puntos.items():
        nx=x/w;ny=y/h
        mezcla=max(0,min(1,(.88-ny)/.3));cabeza=mezcla*mezcla*(3-2*mezcla)
        ax=x-w*.54;ay=y-h*.64
        dx=(ax*(coseno-1)-ay*seno)*cabeza
        dy=(ax*seno+ay*(coseno-1)+1.8*sy*math.sin(4*t))*cabeza
        # Hombros en contratiempo y pelo con retraso respecto a la cabeza.
        dx+=sx*1.25*math.sin(t+.65)*(1-cabeza)
        dy+=sy*.8*math.sin(2*t+.4)*(1-cabeza)
        dx+=sx*1.5*math.sin(t-.7)*pelo*min(1,abs(nx-.54)*3)
        dy+=sy*.7*math.sin(t-.5)*pelo
        borde=min(1,nx/.04,(1-nx)/.04,ny/.04,(1-ny)/.04)
        peso=max(0,borde)*figura
        mapeo[x,y]=(x-dx*peso,y-dy*peso)
    malla=[]
    for y0,y1 in zip(ys,ys[1:]):
        for x0,x1 in zip(xs,xs[1:]):
            quad=(*mapeo[x0,y0],*mapeo[x0,y1],*mapeo[x1,y1],*mapeo[x1,y0])
            malla.append(((x0,y0,x1,y1),quad))
    salida=im.transform(im.size,Image.Transform.MESH,malla,Image.Resampling.BICUBIC)
    # Los centros de píxel del interpolador no deben hacer vibrar el límite del visor.
    for caja in ((0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)):
        salida.paste(im.crop(caja),caja[:2])
    return salida


@lru_cache(maxsize=8)
def vista_escucha(tamano=(320,210),fase=0,movimiento=None):
    if movimiento is None:im=_base_escucha(tamano)
    else:
        escena=_escena_escucha(tamano)
        im=_mover_escucha(escena,movimiento) if escena is not None else None
    if im is None:return None
    from avatar import efecto_camara
    # La cámara es fija: grano y barrido se aplican DESPUÉS del movimiento corporal.
    return efecto_camara(im,tamano,fase)


class AnimacionEscucha:
    """Prepara un único bucle fuera de Tk; la interfaz solo presenta sus fotogramas."""
    def __init__(self,renderizar=vista_escucha):
        self.renderizar=renderizar;self.firma=None;self.cuadros=();self.inicio=0.;self.version=0

    def preparar(self,tamano,senal=True):
        firma=(tamano,bool(senal))
        if self.firma==firma:return
        self.version+=1;version=self.version
        self.firma=firma;self.cuadros=();self.inicio=0.
        def trabajar():
            cuadros=[]
            try:
                for i in range(FOTOGRAMAS_ESCUCHA):
                    if self.version!=version:return
                    im=self.renderizar(tamano,(i//4)%3 if senal else 0,i)
                    if im is None:return
                    cuadros.append(im)
                if self.version==version:
                    self.inicio=time.monotonic();self.cuadros=tuple(cuadros)
            except (OSError,ValueError):return
        threading.Thread(target=trabajar,daemon=True,name='Capri-pose-musical').start()

    def fase(self,ahora=None):
        if not self.cuadros:return None
        return int(max(0,(time.monotonic() if ahora is None else ahora)-self.inicio)*FPS_ESCUCHA)%FOTOGRAMAS_ESCUCHA

    def cancelar(self):
        if self.firma is None and not self.cuadros:return
        self.version+=1;self.firma=None;self.cuadros=();self.inicio=0.


def balancear(imagen,fase,sentada=False):
    pulso=math.sin(fase*math.tau)
    if sentada:
        ancla=(imagen.width*100/210,imagen.height*148/240)
        im=imagen.rotate(pulso*.9,Image.Resampling.BICUBIC,center=ancla)
        im.putalpha(im.getchannel('A').point(lambda a:255 if a>=100 else 0))
        return im
    # Un pequeño cambio de encuadre conserva los bordes llenos del visor.
    w,h=imagen.size;grande=ImageOps.fit(imagen,(w+8,h+8),method=Image.Resampling.BILINEAR)
    x=4+round(pulso*1.5);y=4+round(math.sin(fase*math.tau+1)*1.5)
    return grande.crop((x,y,x+w,y+h))
