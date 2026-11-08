"""Retrato y visor preparados durante el saludo, sin remuestreo al reproducir."""
import math
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import PhotoImage
from PIL import Image,ImageTk,ImageFilter,ImageDraw

ATLAS='capri-intro-abrazo-v1.png'
ZOOM=1.0
VENTANA_HORIZONTAL=(.13,.87)
PASOS=180
PREPARADOS=5
CIERRE=.22
ENCOGER=.30
FONDO=(1,2,3)


def imagen_opaca(im):
    """Misma mezcla que Canvas sobre su color-key, calculada una sola vez."""
    salida=Image.new('RGB',im.size,FONDO)
    salida.paste(im,mask=im.getchannel('A'))
    return salida


def suave(t):
    t=max(0,min(1,t));return t*t*(3-2*t)


def recurso(nombre):
    return next(p for p in (Path(__file__).parent/'assets'/nombre,
                           Path(__file__).parents[1]/'assets'/nombre) if p.exists())


def marco_visor(destino,u,factor):
    """Marco y chat del aspecto elegido, con la foto revelada al final."""
    if u>=1 and abs(factor-1)<.001:return destino.copy()
    im=destino.copy();d=ImageDraw.Draw(im);escala=im.width/360
    izq,arr,der,ab=(round(v*escala) for v in (20,55,340,265))
    foto=suave((u-.78)/.22)
    if foto<1:d.rectangle((izq+round((der-izq)*foto),arr,der-1,ab-1),fill=(0,0,0,0))
    limite=round(ab+(im.height-ab)*suave((u-.30)/.45))
    if limite<im.height:d.rectangle((0,limite,im.width,im.height),fill=(0,0,0,0))
    opacidad=suave((u-.20)/.10)
    if opacidad<1:im.putalpha(im.getchannel('A').point(lambda a:round(a*opacidad)))
    tam=(max(1,round(im.width*factor)),max(1,round(im.height*factor)))
    return im.resize(tam,Image.Resampling.BILINEAR) if tam!=im.size else im


def plan_transicion(b,u,fuente=(1238,941)):
    """Primero cerrar el visor, despues mover y reducir el conjunto."""
    z,ox,oy,caja,factor=b.geometria_salida(u)
    w,h=fuente
    escala=b.w*z/w
    a=suave(u/CIERRE)
    cy=(1-a)*b.h*.42+a*((caja[1]+caja[3])/2-(530-h/2)*escala)
    posicion=(ox-w*escala/2,cy-h*escala/2)
    apertura=tuple(x+(y-x)*a for x,y in zip((0,0,b.w,b.h),caja))
    return {'u':u,'escala':escala,'posicion':posicion,'apertura':apertura,
            'caja':caja,'factor':factor,'pantalla':(b.w,b.h),
            'marco_centro':((caja[0]+caja[2])/2,(caja[1]+caja[3])/2+(b.destino_tamano[1]/2-160*b.destino_tamano[0]/360)*factor)}


def plan_personaje(b,u,fuente=(1238,941)):
    """Retirar el saludo en su sitio; materializar y trasladar el sprite definitivo."""
    w,h=fuente;dw,dh=b.destino_tamano
    if u<.12:
        escala=b.w*ZOOM/w;centro=(b.w*.5,b.h*.42);opacidad=1-suave(u/.12);retrato=True
    else:
        viajar=suave((u-.24)/.76);inicio=(b.w*.5,b.h*.54)
        centro=tuple(a+(z-a)*viajar for a,z in zip(inicio,b.fin))
        escala=1+.08*(1-viajar);opacidad=suave((u-.12)/.12);retrato=False
    return {'personaje':True,'u':u,'pantalla':(b.w,b.h),'centro':centro,
            'escala':escala,'opacidad':opacidad,'retrato':retrato}


def renderizar_personaje(im,destino,p):
    """Un único fotograma compuesto; sin retrato que cae ni estelas añadidas."""
    sw,sh=p['pantalla'];cx,cy=p['centro'];s=p['escala'];peso=p['opacidad']
    fuente=im if p['retrato'] else destino
    x=cx-fuente.width*s/2;y=cy-fuente.height*s/2
    l,a,r,b=max(0,round(x)),max(0,round(y)),min(sw,round(x+fuente.width*s)),min(sh,round(y+fuente.height*s))
    if r<=l or b<=a or peso<=0:return Image.new('RGBA',(1,1)),(0,0)
    box=(max(0,(l-x)/s),max(0,(a-y)/s),min(fuente.width,(r-x)/s),min(fuente.height,(b-y)/s))
    base=fuente if fuente.mode=='RGBa' else fuente.convert('RGBa')
    salida=base.resize((r-l,b-a),Image.Resampling.LANCZOS,box=box).convert('RGBA')
    if peso<1:salida.putalpha(salida.getchannel('A').point(lambda n:round(n*peso)))
    return salida,(l,a)


def renderizar_transicion(im,destino,p,tinta):
    """Solo Pillow. Remuestrea el area visible, nunca un retrato enorme entero."""
    if p.get('personaje'):return renderizar_personaje(im,destino,p)
    u=p['u'];sw,sh=p['pantalla'];s=p['escala'];ix,iy=p['posicion']
    l,a,r,b=p['apertura']
    foto=(max(0,math.ceil(l),math.ceil(ix)),max(0,math.ceil(a),math.ceil(iy)),
          min(sw,math.floor(r),math.floor(ix+im.width*s)),min(sh,math.floor(b),math.floor(iy+im.height*s)))
    marco=None;mx=my=0;cajas=[]
    if foto[2]>foto[0] and foto[3]>foto[1]:cajas.append(foto)
    if u>.20:
        marco=marco_visor(destino,u,p['factor']);cx,cy=p['marco_centro']
        mx=round(cx-marco.width/2);my=round(cy-marco.height/2)
        cajas.append((max(0,mx),max(0,my),min(sw,mx+marco.width),min(sh,my+marco.height)))
    cajas=[c for c in cajas if c[2]>c[0] and c[3]>c[1]]
    if not cajas:return Image.new('RGBA',(1,1)),(0,0)
    x0=min(c[0] for c in cajas);y0=min(c[1] for c in cajas)
    x1=max(c[2] for c in cajas);y1=max(c[3] for c in cajas)
    salida=Image.new('RGBA',(x1-x0,y1-y0))
    if foto in cajas:
        fl,fa,fr,fb=foto
        origen=(max(0,(fl-ix)/s),max(0,(fa-iy)/s),min(im.width,(fr-ix)/s),min(im.height,(fb-iy)/s))
        # RGBa evita convertir a alfa premultiplicado en cada remuestreo.
        filtro=Image.Resampling.LANCZOS if s<1 else Image.Resampling.BICUBIC
        retrato=im.resize((fr-fl,fb-fa),filtro,box=origen)
        if retrato.mode!='RGBA':retrato=retrato.convert('RGBA')
        salida.alpha_composite(retrato,(fl-x0,fa-y0))
    if 0<u<.32:
        alfa=round(255*suave(u/.04)*(1-suave((u-.22)/.10)))
        rgb=tuple(bytes.fromhex(tinta.lstrip('#')))
        borde=Image.new('RGBA',salida.size);d=ImageDraw.Draw(borde)
        d.rectangle((l-x0,a-y0,r-x0-1,b-y0-1),outline=(*rgb,alfa),width=max(1,round(min(sw,sh)/600)))
        salida=Image.alpha_composite(salida,borde)
    if marco is not None:salida.alpha_composite(marco,(mx-x0,my-y0))
    return salida,(x0,y0)


def preparar_imagen(im,destino,p,tinta):
    cuadro,pos=renderizar_transicion(im,destino,p,tinta)
    opaca=imagen_opaca(cuadro)
    # El encabezado y los bytes se preparan fuera del hilo de la interfaz.
    return f'P6\n{opaca.width} {opaca.height}\n255\n'.encode('ascii')+opaca.tobytes(),pos


class RetratoIntro:
    def __init__(self,b):
        self.reloj=None
        if os.name=='nt':
            import ctypes
            reloj=ctypes.windll.winmm
            if reloj.timeBeginPeriod(1)==0:self.reloj=reloj
        self.originales=[]
        with Image.open(recurso(ATLAS)) as atlas:
            w,h=atlas.width//2,atlas.height//2
            mascara=atlas.crop((0,0,w,h)).getchannel('A').point(lambda a:255 if a>=128 else 0)
            mascara=mascara.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
            for fila,col in ((0,0),(0,1),(1,0),(1,1)):
                im=atlas.crop((col*w,fila*h,(col+1)*w,(fila+1)*h)).convert('RGBA')
                im.putalpha(mascara);self.originales.append(im)
        self.ventana_fuente=(round(w*VENTANA_HORIZONTAL[0]),0,round(w*VENTANA_HORIZONTAL[1]),h)
        self.vistas=[im.crop(self.ventana_fuente) for im in self.originales]
        self.fuentes_premultiplicadas={i:self.vistas[i].convert('RGBa') for i in (2,3)}
        self.w,self.h=self.vistas[0].size
        self.base=(round(b.w*ZOOM),round(self.h*b.w*ZOOM/self.w))
        self.inicio=(round((b.w-self.base[0])/2),round(b.h*.42-self.base[1]/2))
        visible=(max(0,-self.inicio[0]),max(0,-self.inicio[1]),
                 min(self.base[0],b.w-self.inicio[0]),min(self.base[1],b.h-self.inicio[1]))
        s=self.base[0]/self.w
        origen_visible=tuple(v/s for v in visible)
        cuerpo=self.fuentes_premultiplicadas[2].resize((visible[2]-visible[0],visible[3]-visible[1]),
                    Image.Resampling.BICUBIC,box=origen_visible).convert('RGBA')
        self.cuerpo=ImageTk.PhotoImage(imagen_opaca(cuerpo))
        self.cuerpo_pos=(self.inicio[0]+visible[0],self.inicio[1]+visible[1])
        caja=(max(0,math.floor((670-self.ventana_fuente[0]-4)*s)),math.floor(376*s),
              min(self.base[0],math.ceil((1030-self.ventana_fuente[0]+4)*s)),math.ceil(674*s))
        self.cara_pos=(self.inicio[0]+caja[0],self.inicio[1]+caja[1]);self.caras=[]
        origen=tuple(v/s for v in caja)
        for im in self.vistas:
            cara=im.resize((caja[2]-caja[0],caja[3]-caja[1]),
                           Image.Resampling.BICUBIC if s>=1 else Image.Resampling.LANCZOS,box=origen)
            self.caras.append(ImageTk.PhotoImage(imagen_opaca(cara)))
        self.efectos=[]
        # Interferencias estrechas del dibujo real, sin una silueta blanca completa.
        for fraccion,alto,desplazamiento in ((.24,14,-1),(.48,24,1),(.73,10,-1)):
            y=round(cuerpo.height*fraccion);h=max(3,round(alto*b.f))
            im=cuerpo.crop((0,y,cuerpo.width,min(cuerpo.height,y+h)))
            self.efectos.append((ImageTk.PhotoImage(im),y,desplazamiento))
        self.fragmentos=[]
        for fila,col in ((0,0),(0,4),(1,2),(2,1),(2,5)):
            caja=(col*cuerpo.width//6,fila*cuerpo.height//3,(col+1)*cuerpo.width//6,(fila+1)*cuerpo.height//3)
            self.fragmentos.append((ImageTk.PhotoImage(imagen_opaca(cuerpo.crop(caja))),caja[:2]))
        self.pasos=PASOS if b.pantalla else 45
        plan=plan_transicion if b.pantalla else plan_personaje
        self.pantalla=b.pantalla
        self.planes=[plan(b,i/self.pasos,(self.w,self.h)) for i in range(self.pasos+1)]
        self.destino=b.destino.copy()
        from tema_ui import actual
        self.tinta=actual();self.pool=ThreadPoolExecutor(max_workers=3,thread_name_prefix='CapriRetrato')
        self.futuros={};self.fotos={};self.ultimo=None
        self.siguiente=0;self.preparado=False

    def preparar(self):
        """Una transferencia nativa por tick del saludo, nunca durante el viaje."""
        if self.preparado:return
        if not self.futuros:self.pedir(self.siguiente)
        f=self.futuros.get(self.siguiente)
        if f is None or not f.done() or f.cancelled():return
        datos,pos=f.result()
        self.fotos[self.siguiente]=(PhotoImage(data=datos,format='PPM'),pos)
        del self.futuros[self.siguiente]
        self.siguiente+=1
        self.preparado=self.siguiente>self.pasos
        if not self.preparado:self.pedir(self.siguiente)

    def pedir(self,indice):
        necesarios=range(indice,min(self.pasos+1,indice+PREPARADOS))
        for viejo in list(self.futuros):
            if viejo not in necesarios:self.futuros.pop(viejo).cancel()
        for i in necesarios:
            if i not in self.futuros:
                original=self.fuentes_premultiplicadas[3 if not self.pantalla or i/self.pasos<.08 else 2]
                self.futuros[i]=self.pool.submit(preparar_imagen,original,self.destino,self.planes[i],self.tinta)

    @staticmethod
    def expresion(t):
        if abs(t-1.86)<.10 or abs(t-3.28)<.10 or t>=4.35:return 3
        if t<.65:return 0
        return 1 if t<1.05 else 2

    def dibujar_retrato(self,c,t):
        c.create_image(*self.cuerpo_pos,image=self.cuerpo,anchor='nw',tags='intro_retrato')
        c.create_image(*self.cara_pos,image=self.caras[self.expresion(t)],anchor='nw',tags=('intro_retrato','intro_expresion'))

    def dibujar(self,c,b,t):
        from bienvenida import SALIDA
        if t>=SALIDA:
            u=b.progreso_salida
            if u>=1:
                c.create_image(*b.fin,image=b.llegada[-1],tags=('intro_retrato','intro_llegada'));return
            indice=round(u*self.pasos)
            if indice in self.fotos:
                self.ultimo=indice
                # Devuelve memoria conforme avanza; no hay trabajo Pillow ni Tk PhotoImage aqui.
                for viejo in list(self.fotos):
                    if viejo<indice:del self.fotos[viejo]
            if self.ultimo in self.fotos:
                foto,pos=self.fotos[self.ultimo]
                c.create_image(*pos,image=foto,anchor='nw',tags='intro_retrato')
            else:self.dibujar_retrato(c,SALIDA)
            return
        if t<.055:
            for foto,(x,y) in self.fragmentos:
                c.create_image(self.cuerpo_pos[0]+x,self.cuerpo_pos[1]+y,image=foto,anchor='nw',tags=('intro_retrato','intro_aparicion_fragmentos'))
            return
        self.dibujar_retrato(c,t)
        if t<.34 and self.efectos:
            distancia=30*b.f*(1-suave((t-.055)/.285))
            for foto,y,direccion in self.efectos:
                c.create_image(self.cuerpo_pos[0]+direccion*distancia,self.cuerpo_pos[1]+y,image=foto,
                               anchor='nw',tags=('intro_retrato','intro_aparicion_interferencia'))
        if t>=.34:self.efectos.clear();self.fragmentos.clear()

    def detener(self):
        if self.reloj is not None:self.reloj.timeEndPeriod(1);self.reloj=None
        self.pool.shutdown(wait=False,cancel_futures=True)
        self.futuros.clear();self.fotos.clear()
