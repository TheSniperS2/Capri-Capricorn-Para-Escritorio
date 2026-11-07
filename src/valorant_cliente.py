"""Transporte acotado de Valorant. Tokens efímeros en memoria, sin contraseñas."""
import base64
from dataclasses import dataclass,field
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import threading
import time
import urllib.request
import urllib.error
from league import SinRedireccion

UUID=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
AGENTES='01bb38e1-da47-4e6a-9b3d-945fe4655707'
REGIONES={'na':'na','latam':'na','br':'na','eu':'eu','ap':'ap','kr':'kr'}
PLATAFORMA=base64.b64encode(json.dumps({'platformType':'PC','platformOS':'Windows',
    'platformOSVersion':'10.0.19045.1.256.64bit','platformChipset':'Unknown'}).encode()).decode()

class ErrorValorant(Exception):
    def __init__(self,clave='conexion'):
        self.clave=clave;super().__init__(clave)

def uuid(valor):return isinstance(valor,str) and re.fullmatch(UUID,valor) is not None

@dataclass(frozen=True)
class SesionRiot:
    jugador:str=field(repr=False)
    acceso:str=field(repr=False)
    derecho:str=field(repr=False)
    region:str
    shard:str
    version:str
    def __post_init__(self):
        if (not uuid(self.jugador) or REGIONES.get(self.region)!=self.shard
            or not re.fullmatch(r'[A-Za-z0-9._-]{5,120}',self.version)
            or any(not isinstance(v,str) or not v or len(v)>20000 or any(c.isspace() for c in v) for v in (self.acceso,self.derecho))):
            raise ErrorValorant('conexion')

def _abridor(local=False):
    contexto=ssl.create_default_context()
    if local:contexto.check_hostname=False;contexto.verify_mode=ssl.CERT_NONE
    return urllib.request.build_opener(urllib.request.ProxyHandler({}),SinRedireccion(),urllib.request.HTTPSHandler(context=contexto))

def _json(abridor,peticion,ausente=False):
    try:
        with abridor.open(peticion,timeout=4) as r:
            datos=r.read(2*1024*1024+1)
            if len(datos)>2*1024*1024:raise ErrorValorant()
            return json.loads(datos) if datos else None
    except urllib.error.HTTPError as e:
        if ausente and e.code==404:return None
        raise ErrorValorant('sesion' if e.code in (401,403) else 'rechazo' if e.code in (400,409,422,429) else 'conexion') from None
    except (OSError,ValueError,urllib.error.URLError):raise ErrorValorant() from None

def juego_en_ejecucion():
    """Riot puede mantener Idle durante una sesión real. Solo lee nombres de procesos."""
    if os.name!='nt':return False
    powershell=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
    try:
        r=subprocess.run([str(powershell),'-NoProfile','-NonInteractive','-Command',
            "Get-Process -Name 'VALORANT-Win64-Shipping' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName"],
            capture_output=True,text=True,timeout=4,creationflags=subprocess.CREATE_NO_WINDOW)
        return r.returncode==0 and any(n.strip().casefold()=='valorant-win64-shipping' for n in r.stdout.splitlines())
    except (OSError,subprocess.SubprocessError):return False


def descubrir():
    base=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData/Local'))
    try:
        partes=(base/'Riot Games/Riot Client/Config/lockfile').read_text(encoding='utf8').strip().split(':')
        if len(partes)!=5 or partes[4]!='https' or not 1<=int(partes[2])<=65535:raise ErrorValorant('cliente')
        token=partes[3]
        if not token or len(token)>512 or any(c.isspace() for c in token):raise ErrorValorant('cliente')
        local=_abridor(True)
        def leer(ruta):
            req=urllib.request.Request('https://127.0.0.1:'+partes[2]+ruta,
                headers={'Authorization':'Basic '+base64.b64encode(('riot:'+token).encode()).decode(),'Accept':'application/json'})
            return _json(local,req)
        sesiones=leer('/product-session/v1/external-sessions')
        candidatas=[s for s in sesiones.values() if isinstance(s,dict) and s.get('productId')=='valorant']
        activas=[s for s in candidatas if str(s.get('phase','')).lower()=='running']
        if not activas and len(candidatas)==1 and str(candidatas[0].get('phase','')).lower()=='idle' and juego_en_ejecucion():
            activas=candidatas
        if len(activas)!=1:raise ErrorValorant('cliente')
        juego=activas[0];args=juego.get('launchConfiguration',{}).get('arguments',[])
        region=next((a.split('=',1)[1].lower() for a in args if a.startswith('-ares-deployment=')),None)
        log=base/'VALORANT/Saved/Logs/ShooterGame.log'
        with log.open('rb') as f:
            inicio=f.read(256*1024);f.seek(max(0,log.stat().st_size-256*1024))
            texto=(inicio+b'\n'+f.read()).decode('utf8',errors='replace')
        regiones=re.findall(r'https://glz-(na|latam|br|eu|ap|kr)-1\.(na|eu|ap|kr)\.a\.pvp\.net',texto)
        if region not in REGIONES:
            if not regiones:raise ErrorValorant('region')
            region=regiones[-1][0]
        versiones=re.findall(r'CI server version:\s*([A-Za-z0-9._-]+)',texto)
        version=juego.get('version','')
        if not str(version).startswith('release-'):
            if not versiones:raise ErrorValorant('version')
            version=versiones[-1]
        auth=leer('/entitlements/v1/token')
        return SesionRiot(auth['subject'].lower(),auth['accessToken'],auth['token'],region,REGIONES[region],version)
    except ErrorValorant:raise
    except (OSError,ValueError,TypeError,KeyError,AttributeError):raise ErrorValorant('cliente') from None

def permitida(metodo,ruta,jugador):
    if metodo=='GET':
        if ruta in (f'/parties/v1/players/{jugador}',f'/pregame/v1/players/{jugador}',f'/core-game/v1/players/{jugador}',
                    f'/store/v1/entitlements/{jugador}/{AGENTES}'):return True
        return re.fullmatch(rf'/(?:parties/v1/parties|pregame/v1/matches)/{UUID}',ruta) is not None
    return metodo=='POST' and (re.fullmatch(rf'/parties/v1/parties/{UUID}/matchmaking/(?:join|leave)',ruta) is not None
        or re.fullmatch(rf'/pregame/v1/matches/{UUID}/(?:select|lock)/{UUID}',ruta) is not None)

class ClienteValorant:
    def __init__(self,obtener=descubrir):
        self.obtener=obtener;self._sesion=None;self._hasta=0;self._lock=threading.RLock();self.abridor=_abridor()
    def conectar(self,forzar=False):
        with self._lock:
            if forzar or self._sesion is None or time.monotonic()>self._hasta:
                self._sesion=self.obtener();self._hasta=time.monotonic()+30
            return self._sesion
    @property
    def jugador(self):return self.conectar().jugador
    def pedir(self,metodo,ruta):
        with self._lock:
            anterior=self._sesion
            s=self.conectar(forzar=metodo=='POST')
            if metodo=='POST' and anterior is not None and anterior.jugador!=s.jugador:raise ErrorValorant('sesion')
            if not permitida(metodo,ruta,s.jugador):raise ValueError('Acción de Valorant no permitida.')
            host=f'pd.{s.shard}.a.pvp.net' if ruta.startswith('/store/') else f'glz-{s.region}-1.{s.shard}.a.pvp.net'
            req=urllib.request.Request('https://'+host+ruta,method=metodo,data=b'' if metodo=='POST' else None,
                headers={'Authorization':'Bearer '+s.acceso,'X-Riot-Entitlements-JWT':s.derecho,
                         'X-Riot-ClientVersion':s.version,'X-Riot-ClientPlatform':PLATAFORMA,
                         'Accept':'application/json','User-Agent':'CapriDesktop'})
            try:return _json(self.abridor,req,ausente=metodo=='GET' and ruta in (f'/pregame/v1/players/{s.jugador}',f'/core-game/v1/players/{s.jugador}'))
            except ErrorValorant as e:
                if e.clave in ('sesion','conexion'):self._sesion=None
                raise
