"""Caché local de datos e iconos públicos. No contiene enlaces privados ni ajustes."""
from pathlib import Path
import io,json,math,os,re,tempfile,time
from PIL import Image
from roblox_info import perfil_automatico

def identificador(valor):return isinstance(valor,(str,int)) and bool(re.fullmatch('[1-9][0-9]{0,18}',str(valor)))

class CacheRoblox:
    def __init__(self,carpeta):self.carpeta=Path(carpeta)
    def escribir(self,nombre,datos):
        temporal=None
        try:
            self.carpeta.mkdir(parents=True,exist_ok=True)
            fd,temporal=tempfile.mkstemp(prefix='.capri-',suffix='.tmp',dir=self.carpeta)
            with os.fdopen(fd,'wb') as f:f.write(datos)
            os.replace(temporal,self.carpeta/nombre)
        except OSError:pass
        finally:
            if temporal:
                try:Path(temporal).unlink(missing_ok=True)
                except OSError:pass
    @staticmethod
    def informacion(info,lugar):
        if not isinstance(info,dict) or str(info.get('lugar'))!=str(lugar) or not identificador(info.get('universo')):return None
        claves={'nombre':100,'descripcion':3000,'genero':80,'subgenero':80,'genero_original':80,'creador':80}
        nuevo={k:' '.join(info[k].split())[:limite] if isinstance(info.get(k),str) else '' for k,limite in claves.items()}
        if not nuevo['nombre']:return None
        nuevo.update(lugar=str(lugar),universo=str(info['universo']));nuevo['perfil']=perfil_automatico(nuevo)
        return nuevo
    def leer_info(self,lugar):
        if not identificador(lugar):return None
        try:
            with (self.carpeta/('experiencia-'+str(lugar)+'.json')).open('rb') as f:b=f.read(64001)
            if len(b)>64000:return None
            d=json.loads(b);fecha=d.get('guardado');info=self.informacion(d.get('datos'),lugar)
            if d.get('version')!=1 or type(fecha) not in (int,float) or not math.isfinite(fecha) or not 0<fecha<=time.time()+60 or not info:return None
            return fecha,info
        except (OSError,ValueError,AttributeError):return None
    def guardar_info(self,info):
        if not isinstance(info,dict) or not identificador(info.get('lugar')):return
        normal=self.informacion(info,info['lugar'])
        if normal:self.escribir('experiencia-'+str(info['lugar'])+'.json',json.dumps({'version':1,'guardado':time.time(),'datos':normal},ensure_ascii=False).encode('utf8'))
    def leer_icono(self,universo):
        if not identificador(universo):return None
        try:
            p=self.carpeta/('icono-'+str(universo)+'.png')
            with p.open('rb') as f:b=f.read(2000001)
            if len(b)>2000000:return None
            with Image.open(io.BytesIO(b)) as im:
                if im.format!='PNG' or not 0<im.width<=512 or not 0<im.height<=512:return None
                return p.stat().st_mtime,im.convert('RGB').copy()
        except (OSError,ValueError,Image.DecompressionBombError):return None
    def guardar_icono(self,universo,imagen):
        if not identificador(universo) or not 0<imagen.width<=512 or not 0<imagen.height<=512:return
        b=io.BytesIO();imagen.convert('RGB').save(b,format='PNG')
        self.escribir('icono-'+str(universo)+'.png',b.getvalue())
