"""OCR local y casillas visibles de CS2; sin leer memoria ni escribir archivos del juego."""
import statistics,time,re,tempfile
from pathlib import Path
from PIL import Image,ImageFilter,ImageOps,ImageChops
from fortnite import ErrorFortnite,Texto
from skins_vision import VistaSkins
from counter_strike import (PantallaCS2,MapaVisible,ErrorCS2,clave,nombre_mapa,NOMBRES_MAPAS,EMPAREJAMIENTO,COMPETITIVO,cabecera)


def componentes(imagen):
    """Componentes de bordes, sin dependencias de visión adicionales."""
    w,h=imagen.size;datos=bytearray(imagen.tobytes());salida=[]
    for inicio in range(len(datos)):
        if not datos[inicio]:continue
        datos[inicio]=0;pendientes=[inicio];x0=x1=inicio%w;y0=y1=inicio//w;cantidad=0
        while pendientes:
            i=pendientes.pop();x=i%w;y=i//w;cantidad+=1
            x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
            for j in ((i-1 if x else -1),(i+1 if x<w-1 else -1),i-w,i+w):
                if 0<=j<len(datos) and datos[j]:datos[j]=0;pendientes.append(j)
        if cantidad>=8:salida.append((x0,y0,x1+1,y1+1))
    return salida


def casillas(imagen):
    factor=min(1,1500/imagen.width);im=imagen.resize((round(imagen.width*factor),round(imagen.height*factor))).convert('RGB')
    w,h=im.size;bordes=im.convert('L').filter(ImageFilter.FIND_EDGES).point(lambda v:255 if v>=28 else 0)
    candidatos=[]
    for x,y,r,b in componentes(bordes):
        a=r-x;alto=b-y
        if not (.012*h<a<.045*h and .012*h<alto<.045*h and .78<a/alto<1.28 and .15*w<x<.98*w and .12*h<y<.88*h):continue
        # Las cuatro esquinas de una casilla deben conservar un borde claro.
        caja=im.crop((x,y,r,b));pix=caja.load();an,al=caja.size
        def claro(rgb):return min(rgb)>=120 and max(rgb)-min(rgb)<110
        lineas=[]
        for lado in ('arriba','abajo','izquierda','derecha'):
            if lado in ('arriba','abajo'):
                valores=[any(claro(pix[xx,yy]) for yy in (range(min(3,al)) if lado=='arriba' else range(max(0,al-3),al))) for xx in range(2,an-2)]
            else:
                valores=[any(claro(pix[xx,yy]) for xx in (range(min(3,an)) if lado=='izquierda' else range(max(0,an-3),an))) for yy in range(2,al-2)]
            lineas.append(sum(valores)/max(1,len(valores)))
        if min(lineas)<.68:continue
        margen=max(3,round(min(an,al)*.2));centro=list(caja.crop((margen,margen,an-margen,al-margen)).getdata())
        if not centro:continue
        naranja=sum(r>150 and g>85 and b<110 and r-b>90 for r,g,b in centro)/len(centro)
        azul=sum(b>115 and b-r>30 for r,g,b in centro)/len(centro)
        if naranja>.10 and azul>.15:continue # Emblema azul/naranja de CS2, no una casilla.
        blanco=sum(min(p)>=205 and max(p)-min(p)<65 for p in centro)/len(centro)
        oscuro=sum(max(p)<155 for p in centro)/len(centro)
        if blanco>.48 and .035<oscuro<.45:seleccionado=True
        elif blanco<.32:seleccionado=False
        else:continue
        rect=(x/factor,y/factor,a/factor,alto/factor)
        if not any(abs(rect[0]-q[0][0])<a/factor*.3 and abs(rect[1]-q[0][1])<alto/factor*.3 for q in candidatos):candidatos.append((rect,seleccionado))
    if not candidatos:return []
    lado=statistics.median(q[0][2] for q in candidatos)
    candidatos=[q for q in candidatos if lado*.82<q[0][2]<lado*1.20]
    filas=[]
    for q in sorted(candidatos,key=lambda q:q[0][1]):
        fila=next((f for f in filas if abs(f[0][0][1]-q[0][1])<imagen.height*.015),None)
        if fila is None:filas.append([q])
        else:fila.append(q)
    principal=max(filas,key=len);columnas=[q[0][0] for q in principal]
    return [q for f in filas for q in f if len(f)>=2 or any(abs(q[0][0]-x)<lado*.5 for x in columnas)]


def resaltado(imagen,t):
    x,y,w,h=t.rect
    caja=imagen.crop((max(0,round(x-5)),max(0,round(y-3)),min(imagen.width,round(x+w+5)),min(imagen.height,round(y+h+3)))).convert('RGB')
    pix=sorted(caja.resize((32,12)).getdata(),key=lambda p:sum(p))[:192]
    if not pix:return False
    r,g,b=(statistics.median(p[i] for p in pix) for i in range(3))
    return b-r>10 and g-r>8 and (r+g+b)/3>40


def analizar(p,imagen):
    cajas=casillas(imagen);w,h=imagen.size
    online=cabecera(p,EMPAREJAMIENTO,(.1,0,.9,.25));competitivo=cabecera(p,COMPETITIVO,(.1,0,.9,.3))
    es_online=bool(online and resaltado(imagen,online));es_comp=bool(competitivo and resaltado(imagen,competitivo))
    # El tiempo de espera bajo cada título confirma que se está leyendo una
    # tarjeta de la cuadrícula, no el nombre del mapa en un chat o un logotipo.
    esperas=[]
    for t in sorted(p.textos,key=lambda t:-t.rect[2]):
        if not (t.rect[0]>.15*w and t.rect[1]>.22*h):continue
        n=clave(t.texto).replace(' ','')
        if not any(a in n for a in ('waittime','wailtime','tiempodeespera','tempodeespera','待機時間','待ち時間')):continue
        if not any(abs(t.rect[0]-a.rect[0])<w*.05 and abs(t.rect[1]-a.rect[1])<h*.02 for a in esperas):esperas.append(t)
    filas=[]
    for caja in sorted(cajas,key=lambda v:v[0][1]):
        fila=next((f for f in filas if abs(f[0][0][1]-caja[0][1])<h*.015),None)
        if fila is None:filas.append([caja])
        else:fila.append(caja)
    pasos=[b[0][0]-a[0][0] for f in filas for a,b in zip(sorted(f),sorted(f)[1:]) if b[0][0]-a[0][0]>.055*w]
    ancho=statistics.median(pasos) if pasos else w*.20
    mapas=[];usadas=set()
    for fila in filas:
        arriba=statistics.median(c[0][1] for c in fila)
        siguiente=min((f[0][0][1] for f in filas if f[0][0][1]>arriba+h*.04),default=h*.995)
        for rect,seleccionado in fila:
            x,y,cw,ch=rect;centro=x+cw/2
            anclas=[t for t in esperas if centro-ancho*.95<t.rect[0]<centro-cw*.1 and arriba+(siguiente-arriba)*.6<t.rect[1]<siguiente]
            titulos=[t for t in p.textos if arriba+(siguiente-arriba)*.60<t.rect[1]<arriba+(siguiente-arriba)*.87
                     and centro-ancho*.95<t.rect[0]+t.rect[2]*.5<centro-cw*.3 and nombre_mapa(t.texto)]
            from core import error_de_una_letra
            conocidos={}
            for t in titulos:
                n=clave(nombre_mapa(t.texto));exacto=[s for s in NOMBRES_MAPAS if clave(s)==n]
                similares=exacto or [s for s in NOMBRES_MAPAS if len(s)>=4 and error_de_una_letra(n,clave(s))]
                if len(similares)==1:conocidos[clave(similares[0])]=similares[0]
            if len(conocidos)==1:nombre=next(iter(conocidos.values()))
            elif conocidos:continue
            else:
                if len(anclas)!=1:continue
                ay=anclas[0].rect[1];titulos=[t for t in titulos if 0<ay-(t.rect[1]+t.rect[3]*.5)<max(ch*3,h*.07)]
                if not titulos:continue
                ultimo=max(t.rect[1] for t in titulos);titulo=max((t for t in titulos if abs(t.rect[1]-ultimo)<ch*.3),key=lambda t:t.rect[2]);nombre=nombre_mapa(titulo.texto)
            if clave(nombre) in usadas:continue
            usadas.add(clave(nombre));mapas.append(MapaVisible(nombre,Texto(nombre,rect),seleccionado))
    completa=bool(len(mapas)>=2 and len(mapas)==len(cajas))
    # Un hueco interior o una fila anterior recortada puede ocultar otra selección.
    for i,fila in enumerate(filas):
        xs=sorted(r[0][0] for r in fila)
        if any(b-a>ancho*1.35 for a,b in zip(xs,xs[1:])):completa=False
        if i<len(filas)-1 and len(fila)<max(map(len,filas)):completa=False
    for fila in filas:
        arriba=statistics.median(c[0][1] for c in fila)
        fin=min((f[0][0][1] for f in filas if f[0][0][1]>arriba+h*.04),default=h*.995)
        for t in p.textos:
            if not (.15*w<t.rect[0]<.98*w and arriba+(fin-arriba)*.60<t.rect[1]<arriba+(fin-arriba)*.87):continue
            nombre=nombre_mapa(t.texto)
            if any(clave(nombre)==clave(n) for n in NOMBRES_MAPAS) and clave(nombre) not in usadas:completa=False
    return PantallaCS2(p.ventana,p.rect,p.textos,p.momento,(),tuple(mapas),completa,es_online,es_comp)


class VistaCS2(VistaSkins):
    NOMBRES={'cs2.exe'}
    def __init__(self):
        self.imagen=None
        try:super().__init__()
        except ErrorFortnite as e:raise ErrorCS2(str(e).replace('Fortnite','Counter-Strike 2')) from e

    def _imagen(self,*args,**kw):
        im,rect,inicio=super()._imagen(*args,**kw);self.imagen=im;return im,rect,inicio

    def _leer(self,ruta):return self.ocr.leer(ruta,palabras=True)

    def ampliar_tarjetas(self,p,contraste=False):
        cajas=casillas(self.imagen)
        if len(cajas)<2:return p
        filas=[];w,h=self.imagen.size
        for rect,_ in sorted(cajas,key=lambda v:v[0][1]):
            fila=next((f for f in filas if abs(f[0][1]-rect[1])<h*.015),None)
            if fila is None:filas.append([rect])
            else:fila.append(rect)
        pasos=[b[0]-a[0] for f in filas for a,b in zip(sorted(f),sorted(f)[1:]) if b[0]-a[0]>.055*w]
        if not pasos:return p
        ancho=statistics.median(pasos);regiones=[]
        for fila in filas:
            y=statistics.median(r[1] for r in fila);fin=min((f[0][1] for f in filas if f[0][1]>y+h*.04),default=h*.995)
            for x,_,cw,ch in fila:
                regiones.append((round(max(0,x-ancho*.88)),round(y+(fin-y)*.63),round(min(w,x+cw)),round(min(h,fin-ch*.4))))
        partes=[];mapa=[];alto=0;ancho_hoja=0
        for i,(l,a,r,b) in enumerate(regiones):
            recorte=self.imagen.crop((l,a,r,b));escala=min(2.1,600/recorte.width)
            if contraste:
                rojo,verde,azul=recorte.convert('RGB').split();gris=ImageChops.darker(ImageChops.darker(rojo,verde),azul)
                recorte=ImageOps.invert(gris.point(lambda v:255 if v>=160 else 0)).convert('RGB')
            recorte=recorte.resize((round(recorte.width*escala),round(recorte.height*escala)))
            if i%2==0:alto_fila=recorte.height+16
            ox=(i%2)*620;oy=alto
            partes.append((recorte,ox,oy));mapa.append((ox,oy,recorte.width,recorte.height,l,a,escala))
            ancho_hoja=max(ancho_hoja,ox+recorte.width)
            if i%2==1:alto+=max(alto_fila,recorte.height+16)
        if len(partes)%2:alto+=alto_fila
        hoja=Image.new('RGB',(ancho_hoja,alto),'black')
        for im,x,y in partes:hoja.paste(im,(x,y))
        factor=min(1,2500/max(hoja.size))
        if factor<1:hoja=hoja.resize((round(hoja.width*factor),round(hoja.height*factor)))
        with tempfile.TemporaryDirectory(prefix='capri-cs2-mapas-') as d:
            ruta=Path(d)/'mapas.png';hoja.save(ruta);textos=self._leer(ruta)
        salida=[t for t in p.textos if not any(l<=t.rect[0]<r and a<=t.rect[1]<b for l,a,r,b in regiones)]
        for t in textos:
            x,y,tw,th=(v/factor for v in t.rect)
            m=next((m for m in mapa if m[0]<=x<x+tw<=m[0]+m[2]+2 and m[1]<=y<y+th<=m[1]+m[3]+2),None)
            if m:
                ox,oy,_,_,l,a,escala=m;salida.append(Texto(t.texto,(l+(x-ox)/escala,a+(y-oy)/escala,tw/escala,th/escala)))
        return type(p)(p.ventana,p.rect,tuple(salida),p.momento)

    def capturar(self,activar=False):
        try:
            # Una acción exige títulos y casillas actuales, sin reutilizar texto
            # de otra lectura. Solo se reutiliza el proceso del motor OCR.
            self._leida=-float('inf')
            p=super().capturar(activar=activar);q=analizar(p,self.imagen)
            if not q.completa and casillas(self.imagen):q=analizar(self.ampliar_tarjetas(p),self.imagen)
            if not q.completa and q.mapas:q=analizar(self.ampliar_tarjetas(p,contraste=True),self.imagen)
            self._validar(q.ventana,q.rect);return q
        except ErrorFortnite as e:raise ErrorCS2(str(e).replace('Fortnite','Counter-Strike 2').replace('lobby','menú Jugar')) from e

    def pulsar(self,p,t):
        try:
            if t not in (*p.textos,*(m.control for m in p.mapas)):raise ErrorCS2('Ese control ya no pertenece a la lectura de Counter-Strike.')
            # La clase nativa verifica foco, antigüedad y ventana bajo el cursor.
            from fortnite import Pantalla
            base=Pantalla(p.ventana,p.rect,(*p.textos,*(m.control for m in p.mapas)),p.momento)
            return super().pulsar(base,t)
        except ErrorFortnite as e:raise ErrorCS2(str(e).replace('Fortnite','Counter-Strike 2')) from e
