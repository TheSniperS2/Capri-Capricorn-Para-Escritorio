"""Intro muda con el retrato aprobado, sus expresiones y el saludo visual."""
import math
from PIL import Image,ImageTk
from fuentes import FAMILIA
from idiomas import ui
from intro import suave,DURACION
from tema_ui import color

SALIDA=5.2
PASOS_MARCO=120
SALUDO='¡Hola!'
TRANSPARENTE='#010203'


def limitar(v):return max(0.,min(1.,v))


class LienzoAnimado:
    """Reutiliza primitivas Tk en lugar de destruir y reconstruir toda la escena."""
    def __init__(self,canvas):
        self.canvas=canvas;self.items={};self.opciones={};self.ocultos=set();self.usados=set();self.contadores={}
        self.coordenadas={};self.orden=[];self.orden_anterior=()

    def delete(self,tag):
        if self.items and not self.canvas.type(next(iter(self.items.values()))):
            self.items.clear();self.opciones.clear();self.ocultos.clear();self.coordenadas.clear();self.orden_anterior=()
        self.usados.clear();self.contadores.clear();self.orden=[]

    def crear(self,tipo,p,kw):
        tag=str(kw.get('tags',''));grupo=(tipo,tag);n=self.contadores.get(grupo,0);self.contadores[grupo]=n+1
        clave=(tipo,tag,n);self.usados.add(clave)
        if clave not in self.items:
            item=getattr(self.canvas,tipo)(*p,**kw);self.items[clave]=item;self.opciones[clave]=dict(kw)
        else:
            item=self.items[clave]
            if self.coordenadas.get(clave)!=p:self.canvas.coords(item,*p)
            cambios={k:v for k,v in kw.items() if self.opciones[clave].get(k)!=v}
            if clave in self.ocultos:cambios.update(state='normal',tags=kw.get('tags',()));self.ocultos.remove(clave)
            if cambios:self.canvas.itemconfigure(item,**cambios)
            self.opciones[clave]=dict(kw)
        self.coordenadas[clave]=p;self.orden.append(item)
        return item

    def create_polygon(self,*p,**kw):return self.crear('create_polygon',p,kw)
    def create_line(self,*p,**kw):return self.crear('create_line',p,kw)
    def create_image(self,*p,**kw):return self.crear('create_image',p,kw)
    def create_text(self,*p,**kw):return self.crear('create_text',p,kw)
    def terminar(self):
        for clave in self.items.keys()-self.usados-self.ocultos:
            self.canvas.itemconfigure(self.items[clave],state='hidden',tags=());self.ocultos.add(clave)
        orden=tuple(self.orden)
        if orden!=self.orden_anterior:
            for item in orden:self.canvas.tag_raise(item)
            self.orden_anterior=orden


class Bienvenida:
    def __init__(self,estados,destino,fin,ancho,alto,saludo=None,pantalla=True):
        self.w,self.h=ancho,alto;self.fin=fin;self.saludo=saludo or ui(SALUDO)
        self.centro=(ancho/2,alto/2);self.salida_desde=None;self.retenida=False
        self.f=max(.55,alto/1080)
        self.pantalla=pantalla;self.destino_tamano=destino.size;self.recorte=None
        self.lienzo=None
        self.llegada=[]
        for i in range(1 if pantalla else 21):
            zoom=1 if pantalla else 1+.28*(1-i/20)
            im=destino.resize((max(1,round(destino.width*zoom)),max(1,round(destino.height*zoom))),Image.Resampling.LANCZOS)
            self.llegada.append(ImageTk.PhotoImage(im))
        self.marcos={};self.destino=destino.copy();self.apertura_salida=0;self.progreso_salida=0
        self.aparicion_t=None;self.numero_forma=0
        self.espera_preparacion=None;self.pausa_preparacion=0.
        from retrato_intro import RetratoIntro
        self.retrato_aprobado=RetratoIntro(self)

    def detener(self):
        self.retrato_aprobado.detener()
        self.marcos.clear()

    def tiempo(self,t,esperando_voz=False):
        # La bienvenida no depende de un sintetizador ni de eventos de audio.
        if t>=.45:self.retrato_aprobado.preparar()
        visual=t-self.pausa_preparacion
        if visual>=SALIDA and not self.retrato_aprobado.preparado:
            if self.espera_preparacion is None:self.espera_preparacion=t
            return SALIDA-.001
        if self.espera_preparacion is not None:
            self.pausa_preparacion+=t-self.espera_preparacion
            self.espera_preparacion=None
            visual=t-self.pausa_preparacion
        return visual

    def retrato(self,c,t,z,dx=0,dy=0):
        self.rig=(1,0,1,0,self.w*z/1086,self.w*.5+dx,self.h*.42+dy,0)
        self.retrato_aprobado.dibujar(c,self,t)

    def cartel(self,c,t):
        q=suave((t-.24)/.20)
        if q<=0:return
        f=min(self.f,self.w/960);w=312*f
        x=self.w-w-70*f+(1-q)*24*f;y=self.h*.15
        def placa(puntos,**kw):
            return c.create_polygon(*[v for px,py in puntos for v in (x+px*f,y+py*f)],tags='intro_saludo',**kw)
        # Cian y tinta oscura para contrastar con el pelo rosa.
        ancho=w/f
        placa(((19,8),(ancho+9,8),(ancho-9,123),(0,123)),fill='#0c0813',outline='')
        placa(((15,5),(ancho+5,5),(ancho-13,117),(-3,117)),fill='#2463bf',outline='')
        placa(((12,0),(ancho,0),(ancho-18,110),(-6,110)),fill='#62e7f5',outline='#0c0813',width=max(1,round(2*f)))
        placa(((5,121),(ancho-15,121),(ancho-23,166),(-3,166)),fill='#0c0813',outline='')
        c.create_line(x+24*f,y+7*f,x+86*f,y+7*f,fill='#d7fbff',width=max(1,round(2*f)),tags='intro_saludo')
        c.create_line(x-13*f,y+20*f,x-19*f,y+52*f,fill='#62e7f5',width=max(2,round(3*f)),tags='intro_saludo')
        c.create_text(x+w/2-3*f,y+54*f,text=self.saludo,fill='#08131f',
                      font=(FAMILIA,-max(26,round(58*f)),'bold'),tags='intro_saludo')
        c.create_text(x+w/2-11*f,y+142*f,text='Capricorn Desktop',fill='#ffffff',
                      font=(FAMILIA,-max(14,round(21*f)),'bold'),tags=('intro_saludo','intro_subtitulo'))

    def dibujar(self,c,t,hablando=False,boca=False,bandas=()):
        if hasattr(c,'tk'):
            if self.lienzo is None or self.lienzo.canvas is not c:self.lienzo=LienzoAnimado(c)
            c=self.lienzo
        c.delete('all')
        self.recorte=None;self.apertura_salida=0;self.aparicion_t=t if 0<=t<.34 else None
        if t<SALIDA:
            z=self.encuadre(t)
            # Materialización breve en su posición definitiva, sin recorrido vertical.
            self.retrato(c,t,z)
            self.cartel(c,t)
            if isinstance(c,LienzoAnimado):c.terminar()
            return
        u=limitar((t-SALIDA)/(DURACION-SALIDA));self.progreso_salida=u
        q=suave(max(0,(u-.08)/.92))
        if self.pantalla:
            self.apertura_salida=suave(u/.22)
            z,ox,oy,caja,factor=self.geometria_salida(u)
            # El retrato y el marco comparten un solo fotograma compuesto.
            self.retrato(c,SALIDA,z,ox-self.w*.5,oy-self.h*.42)
            self.recorte=None
            if isinstance(c,LienzoAnimado):c.terminar()
            return
        if u<.20:
            salida=suave(u/.20)
            self.retrato(c,SALIDA,1.25,self.w*.12*salida,self.h*salida)
        i=min(len(self.llegada)-1,round(q*(len(self.llegada)-1)))
        cx,cy=self.centro;x=cx+(self.fin[0]-cx)*q;y=cy+(self.fin[1]-cy)*q-40*math.sin(math.pi*q)
        c.create_image(x,y,image=self.llegada[i],tags='intro_llegada')
        if q<.85:
            for k in (1,2,3):
                p=max(0,q-k*.025);tx=cx+(self.fin[0]-cx)*p;ty=cy+(self.fin[1]-cy)*p-40*math.sin(math.pi*p)
                c.create_line(tx-10,ty,tx+10,ty,fill=color('#8e304a'),width=2,tags='intro_estela')
        if isinstance(c,LienzoAnimado):c.terminar()

    @staticmethod
    def encuadre(t):
        from retrato_intro import ZOOM
        return ZOOM

    def geometria_salida(self,u):
        from retrato_intro import ENCOGER
        q=suave((u-ENCOGER)/(1-ENCOGER));escala=self.destino_tamano[0]/360
        s0=self.w*self.encuadre(SALIDA)/1086;s1=320*escala/600
        s=s0+(s1-s0)*q
        # Mantiene un único centro de proyección desde el primer plano hasta la cámara.
        ox=self.w*.5+(self.fin[0]-self.w*.5)*q
        fin_y=self.fin[1]-(23-14*escala)-55*s1
        oy=self.h*.42+(fin_y-self.h*.42)*q
        factor=s/s1;cx=ox;cy=oy+55*s
        caja=(cx-160*escala*factor,cy-105*escala*factor,cx+160*escala*factor,cy+105*escala*factor)
        return s*1086/self.w,ox,oy,caja,factor


def recortar(coords,caja):
    """Recorte de polígonos contra la cámara que se va formando (Sutherland-Hodgman)."""
    xs=coords[::2];ys=coords[1::2]
    if min(xs)>=caja[0] and max(xs)<=caja[2] and min(ys)>=caja[1] and max(ys)<=caja[3]:return coords
    if max(xs)<caja[0] or min(xs)>caja[2] or max(ys)<caja[1] or min(ys)>caja[3]:return []
    puntos=list(zip(xs,ys))
    for eje,limite,signo in ((0,caja[0],1),(0,caja[2],-1),(1,caja[1],1),(1,caja[3],-1)):
        if not puntos:break
        salida=[];anterior=puntos[-1];d0=(anterior[eje]-limite)*signo
        for actual in puntos:
            d1=(actual[eje]-limite)*signo
            if (d1>=0)!=(d0>=0):
                q=d0/(d0-d1)
                salida.append(tuple(a+(b-a)*q for a,b in zip(anterior,actual)))
            if d1>=0:salida.append(actual)
            anterior=actual;d0=d1
        puntos=salida
    return [v for p in puntos for v in p]
