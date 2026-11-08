"""Gustos de Capri: reconocimiento comprobado, cadencia y comentarios optativos."""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import random
import re
import threading
import time
import unicodedata
from skins_dialogos import frases


def clave(s):
    s=''.join(c for c in unicodedata.normalize('NFD',str(s).casefold()) if unicodedata.category(c)!='Mn')
    return ' '.join(re.sub(r'[^\w\s]',' ',s).split())


def normalizar(config):
    c=config if isinstance(config,dict) else {}
    frecuencia=c.get('frecuencia')
    return {'activo':c.get('activo') is True,'valorant':c.get('valorant',True) is True,
            'fortnite':c.get('fortnite',True) is True,
            'frecuencia':frecuencia if frecuencia in ('discreta','equilibrada','entusiasta') else 'equilibrada'}


@lru_cache(maxsize=1)
def catalogo():
    base=Path(__file__).resolve().parent
    ruta=next((p for p in (base/'assets/skins/catalogo.json',base.parent/'assets/skins/catalogo.json') if p.is_file()),None)
    if ruta is None:return ()
    return tuple(json.loads(ruta.read_text(encoding='utf8'))['skins'])


@dataclass(frozen=True)
class Lectura:
    juego:str
    contexto:str
    skins:tuple
    sesion:str=''
    @property
    def firma(self):return (self.juego,self.sesion,self.contexto,tuple(sorted(s['id'] for s in self.skins)))


@dataclass(frozen=True)
class Reaccion:
    texto:str
    skin:dict
    lectura:Lectura
    momento:float
    idioma:str='es'


class GustosCapri:
    def __init__(self,reloj=time.monotonic,azar=None):
        self.reloj=reloj;self.azar=azar or random.Random();self._lock=threading.RLock()
        self._estable=None;self._muestras=0;self._ultima_firma=None;self._ultimos_ids=set()
        self._ultima=-1e10;self._vistas={};self._frases={};self.pendiente=None

    def observar(self,lectura,frecuencia='equilibrada',idioma='es',manual=False):
        with self._lock:
            ahora=self.reloj()
            if lectura is None or not lectura.skins:
                self._estable=None;self._muestras=0;self.pendiente=None;return None
            firma=lectura.firma
            if self.pendiente and self.pendiente.lectura.firma!=firma:self.pendiente=None
            self._muestras=self._muestras+1 if self._estable==firma else 1;self._estable=firma
            if not manual:
                if self._muestras<2 or firma==self._ultima_firma:return None
                if ahora-self._ultima<{'discreta':18,'equilibrada':8,'entusiasta':3}.get(frecuencia,8):return None
                if self.pendiente and ahora-self.pendiente.momento<18:return None
            candidatas=list(lectura.skins)
            if not manual:
                nuevas=[s for s in candidatas if s['id'] not in self._ultimos_ids]
                if nuevas:candidatas=nuevas
            if not candidatas:return None
            def prioridad(s):
                return (bool(s.get('favorita')),s.get('arma') in ('Vandal','Phantom','Melee'))
            mejor=max(map(prioridad,candidatas));skin=self.azar.choice([s for s in candidatas if prioridad(s)==mejor])
            reencuentro=not manual and (lectura.juego,skin['id']) in self._vistas
            opciones=frases(skin,idioma,reencuentro=reencuentro);llave=(skin['juego'],skin['id'],idioma)
            texto=self.azar.choice([f for f in opciones if f!=self._frases.get(llave)] or list(opciones))
            plan=Reaccion(texto,skin,lectura,ahora,idioma)
            if not manual:self.pendiente=plan
            return plan

    def confirmar(self,plan,manual=False):
        with self._lock:
            if not manual and (self.pendiente is not plan or self.reloj()-plan.momento>18):return False
            self._ultima=self.reloj();self._ultima_firma=plan.lectura.firma
            self._ultimos_ids={s['id'] for s in plan.lectura.skins}
            self._vistas[plan.lectura.juego,plan.skin['id']]=self._ultima
            self._frases[plan.skin['juego'],plan.skin['id'],plan.idioma]=plan.texto
            while len(self._vistas)>256:del self._vistas[next(iter(self._vistas))]
            while len(self._frases)>512:del self._frases[next(iter(self._frases))]
            self.pendiente=None;return True

    def anular(self):
        with self._lock:self.pendiente=None;self._estable=None;self._muestras=0


def interpretar_skins(texto):
    n=clave(texto)
    n=re.sub(r'^(?:please |can you |could you |voce pode )','',n)
    if re.match(r'^(?:no|nunca|como |explica|si digo)',n):return None
    m=re.fullmatch(r'(?:mira(?:r)?|comenta|reacciona a|que (?:opinas|piensas) de|que te (?:parece|parecen)|te gusta(?:n)?) (?:mi|mis|esta|estas|la|las) (?:skin|skins|aspecto|aspectos)(?: (?:en|de|del) (valorant|valo|fortnite))?',n)
    if m:return ('skins_opinar','valorant' if m[1]=='valo' else m[1] or '')
    m=re.fullmatch(r'(?:look at|check|what do you think of) (?:my|this|these) skins?(?: in (valorant|fortnite))?',n)
    if not m:m=re.fullmatch(r'(?:olhe|veja|o que acha de) (?:(?:minha|esta|essa) skin|minhas skins)(?: no (valorant|fortnite))?',n)
    if m:return ('skins_opinar',m[1] or '')
    for juego,rotulos in (('valorant',('valorant','ヴァロラント')),('fortnite',('fortnite','フォートナイト'))):
        if any(n==clave(r+'のスキンを見て') for r in rotulos):return ('skins_opinar',juego)
    return None


class MonitorSkins:
    """Un solo trabajador, sin Tk ni capturas cuando no hay permiso/contexto."""
    def __init__(self,avisar,fuentes=None,reloj=time.monotonic):
        self.avisar=avisar;self.fuentes=fuentes;self.motor=GustosCapri(reloj);self.reloj=reloj
        self.config=normalizar({});self.estado='Reacciones a skins desactivadas';self.ultima=None
        self._stop=threading.Event();self._lock=threading.RLock();self._version=0
        self._permitida=False;self._idioma='es';self.hilo=None

    def configurar(self,config,iniciar=True):
        with self._lock:
            self.config=normalizar(config);self._version+=1;self.motor.anular()
            self.estado='Esperando una skin reconocible fuera de partida' if self.config['activo'] else 'Reacciones a skins desactivadas'
            if iniciar and self.config['activo'] and (self.hilo is None or not self.hilo.is_alive()):
                self._stop=threading.Event();self.hilo=threading.Thread(target=self._vigilar,args=(self._stop,),daemon=True);self.hilo.start()

    def permitir(self,permitida,idioma='es'):
        with self._lock:
            if self._permitida and (not permitida or idioma!=self._idioma):self._version+=1;self.motor.anular()
            self._permitida=bool(permitida);self._idioma=idioma

    def _fuentes(self):
        if self.fuentes is None:
            from skins_fuentes import FuentesSkins
            self.fuentes=FuentesSkins()
        return self.fuentes

    def _vigilar(self,stop):
        ultimo=0
        while not stop.wait(1):
            with self._lock:
                c=dict(self.config);permitida=self._permitida;version=self._version;idioma=self._idioma
            if not c['activo'] or not permitida:continue
            fuente=self._fuentes();juego=fuente.primer_plano()
            if juego not in ('valorant','fortnite') or not c[juego]:self.motor.anular();continue
            if self.reloj()-ultimo<3:continue
            ultimo=self.reloj()
            try:
                lectura=fuente.leer(juego)
                with self._lock:
                    if stop.is_set() or version!=self._version or not self._permitida:continue
                    self.estado=fuente.estado
                    if fuente.primer_plano()!=juego:self.motor.anular();continue
                    plan=self.motor.observar(lectura,c['frecuencia'],idioma)
                    if plan:self.avisar(('skin_reaccion',(version,plan)))
            except Exception:
                # El fallo de una observación nunca altera el juego ni se narra.
                self.estado='No pude confirmar una skin; esperaré otra ocasión';self.motor.anular()

    def aceptar(self,version,plan):
        with self._lock:
            if (self._stop.is_set() or version!=self._version or not self.config['activo'] or not self.config[plan.lectura.juego]
                or not self._permitida or self._fuentes().primer_plano()!=plan.lectura.juego):return False
            if not self.motor.confirmar(plan):return False
            self.ultima=plan;self.estado='Última reacción: '+plan.skin['nombres'].get(self._idioma,plan.skin['nombres']['en']);return True

    def opinar(self,juego='',idioma='es',cancelar=None,preferido=''):
        from idiomas import ui
        fuente=self._fuentes();juego=juego or fuente.primer_plano() or preferido
        if juego not in ('valorant','fortnite'):return ui('Dime si quieres que mire tu skin en Valorant o Fortnite.',idioma)
        if cancelar is not None and cancelar.is_set():raise InterruptedError()
        try:lectura=fuente.leer(juego,manual=True)
        except InterruptedError:raise
        except Exception as error:
            from fortnite import ErrorFortnite
            if isinstance(error,ErrorFortnite):
                if cancelar is not None and cancelar.is_set():raise InterruptedError()
                return ui(str(error),idioma)
            lectura=None
        if cancelar is not None and cancelar.is_set():raise InterruptedError()
        if lectura is None or not lectura.skins:
            return ui('Abre la ficha de la skin en la colección o tienda de Valorant, con su nombre visible y fuera de partida.' if juego=='valorant'
                    else 'Muéstrame el nombre de la skin en el casillero o en su ficha de la tienda de Fortnite. No pude identificarla todavía.',idioma)
        plan=self.motor.observar(lectura,idioma=idioma,manual=True)
        self.motor.confirmar(plan,manual=True);self.ultima=plan;return plan.texto

    def cerrar(self):
        with self._lock:self._version+=1;self._permitida=False;self.motor.anular();self._stop.set()
