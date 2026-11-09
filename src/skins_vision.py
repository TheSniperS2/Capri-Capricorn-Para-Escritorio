"""Ficha visible de Valorant mediante OCR local; sin entradas al juego."""
from pathlib import Path
import tempfile
import hashlib,threading,time
from fortnite import ErrorFortnite,Pantalla,Texto
from fortnite_vision import VistaFortnite,leer_imagen


class VistaSkins(VistaFortnite):
    """Reutiliza OCR y texto cuando las áreas de interfaz siguen iguales."""
    def __init__(self,ocr=None):
        super().__init__()
        from ocr_skins import OcrSkins
        self.ocr=ocr or OcrSkins();self._lectura=None;self._firma=None;self._lock=threading.RLock()
    @staticmethod
    def firma(imagen):
        from PIL import ImageChops
        w,h=imagen.size;partes=[]
        # Texto de navegación/ficha/acciones; el modelo animado central queda fuera.
        for l,t,r,b in ((0,0,1,.16),(0,.16,.44,.98),(.44,.70,1,1),(.62,.16,1,.70)):
            im=imagen.crop((round(l*w),round(t*h),round(r*w),round(b*h))).convert('RGB')
            rojo,verde,azul=im.split();minimo=ImageChops.darker(ImageChops.darker(rojo,verde),azul)
            partes.append(minimo.point(lambda x:255 if x>=175 else 0).tobytes())
        return hashlib.sha256(b''.join(partes)).digest()
    def _leer(self,ruta):
        lector=getattr(self,'ocr',None)
        return lector.leer(ruta) if lector else leer_imagen(ruta)
    def capturar(self,activar=False):
        # Compatibilidad con vistas de prueba sin constructor nativo.
        lock=getattr(self,'_lock',None)
        if lock is None:return self._capturar(activar)
        with lock:return self._capturar(activar)
    def _capturar(self,activar=False):
        h=self._ventana();recuperada=self._activar(h) if activar else False
        imagen,rect,inicio=self._imagen(h,esperar=recuperada);firma=(h,rect,self.firma(imagen))
        previo=getattr(self,'_lectura',None)
        if previo is not None and firma==getattr(self,'_firma',None) and inicio-getattr(self,'_leida',0)<4:
            self._validar(h,rect);return Pantalla(h,rect,previo.textos,inicio)
        with tempfile.TemporaryDirectory(prefix='capri-skin-') as temporal:
            factor=min(1,2500/max(imagen.size));ruta=Path(temporal)/'ficha.png'
            lectura=imagen.resize((round(imagen.width*factor),round(imagen.height*factor))) if factor<1 else imagen
            lectura.save(ruta);textos=self._leer(ruta)
            if factor<1:textos=tuple(Texto(t.texto,tuple(v/factor for v in t.rect)) for t in textos)
        self._validar(h,rect);p=Pantalla(h,rect,textos,inicio)
        self._firma=firma;self._lectura=p;self._leida=inicio;self._detalle=None;return p
    def leer_ficha(self,p):
        self._validar(p.ventana,p.rect)
        if getattr(self,'_detalle',None) is not None:return self._detalle
        regiones=self.regiones_ficha(p)
        if not regiones:return None
        from PIL import Image,ImageGrab,ImageOps,ImageChops
        self._validar(p.ventana,p.rect);imagen=ImageGrab.grab(bbox=p.rect,all_screens=True).convert('RGB')
        self._validar(p.ventana,p.rect);partes=[];mapa=[];alto=0
        for l,a,r,b in regiones:
            original=imagen.crop((l,a,r,b));rojo,verde,azul=original.split()
            minimo=ImageChops.darker(ImageChops.darker(rojo,verde),azul)
            contraste=ImageOps.invert(minimo.point(lambda v:255 if v>=145 else 0))
            for recorte in (original,contraste):
                escala=min(2.5,2800/max(original.size));tam=(round(original.width*escala),round(original.height*escala))
                partes.append(recorte.resize(tam,Image.Resampling.LANCZOS));mapa.append((alto,alto+tam[1],l,a,escala));alto+=tam[1]+24
        ancho=max(im.width for im in partes);hoja=Image.new('RGB',(ancho,alto),'black')
        for im,datos in zip(partes,mapa):hoja.paste(im,(0,datos[0]))
        if max(hoja.size)>2500:
            # Acotar el tamaño admitido por OcrEngine conservando el mapa de origen.
            factor=2500/max(hoja.size);hoja=hoja.resize((round(hoja.width*factor),round(hoja.height*factor)))
        else:factor=1
        with tempfile.TemporaryDirectory(prefix='capri-skin-nombre-') as temporal:
            ruta=Path(temporal)/'nombre.png';hoja.save(ruta);lecturas=self._leer(ruta)
        nuevos=[]
        for t in lecturas:
            x,y,w,h=(v/factor for v in t.rect)
            fila=next((m for m in mapa if m[0]<=y and y+h<=m[1]+2),None)
            if fila:
                arriba,_,l,a,escala=fila;nuevos.append(Texto(t.texto,(l+x/escala,a+(y-arriba)/escala,w/escala,h/escala)))
        conservados=[t for t in p.textos if not any(l<=t.rect[0]<r and a<=t.rect[1]<b for l,a,r,b in regiones)]
        self._validar(p.ventana,p.rect)
        detalle=Pantalla(p.ventana,p.rect,tuple(conservados+nuevos),time.monotonic())
        self._lectura=detalle;self._detalle=detalle;return detalle
    def cerrar(self):
        if getattr(self,'ocr',None):self.ocr.cerrar()

class VistaValorantSkins(VistaSkins):
    NOMBRES={'valorant-win64-shipping.exe'}

    def capturar(self,activar=False):
        try:
            return super().capturar(activar)
        except ErrorFortnite as e:
            raise ErrorFortnite(str(e).replace('Fortnite','Valorant').replace('lobby','colección')) from e
