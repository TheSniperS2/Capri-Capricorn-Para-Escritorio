"""Preferencias y controles del lobby. No vigila partidas ni reinicia la cola."""
import re
import threading
import time
import unicodedata
from dataclasses import dataclass


def clave(texto):
    n=''.join(c for c in unicodedata.normalize('NFD',str(texto).casefold()) if unicodedata.category(c)!='Mn')
    return ' '.join(n.strip(' .!¡?¿,:;…•').split())


MODOS={'actual':('Modo actual',()),'br':('Battle Royale',('battle royale','construccion','construction','construcao')),
       'cero':('Cero construcción',('cero construccion','cero construccioi','cero construccio','cero construccion - battle royale','zero build','zero build - battle royale','construcao zero'))}
EQUIPOS={'actual':('Equipo actual',()),'solo':('Solo',('solo','solos','en solitario')),
         'duo':('Dúo',('duo','duos','duplas','en duo','en duos')),'trio':('Trío',('trio','trios','en trio','en trios')),
         'squad':('Squad',('squad','squads','escuadron','escuadrones','en escuadron','en escuadrones','esquadroes'))}


def normalizar(config):
    c=config if isinstance(config,dict) else {}
    return {k:c.get(k) if isinstance(c.get(k),str) and c[k] in opciones else 'actual'
            for k,opciones in (('modo',MODOS),('equipo',EQUIPOS))}


def interpretar_fortnite(texto):
    n=clave(texto)
    juego=r' (?:en|in|on|no|de|del) (?:el |o |the )?fortnite'
    buscar=(r'(?:(?:busca(?:r)?(?:me)?|busques) (?:una |la )?partida|(?:inicia(?:r)?|tira(?:r)?|pon|ponme|lanza) '
            r'(?:una |la |en )?(?:cola|partida|busqueda)|(?:realiza(?:r)?|haz) (?:una |la )?busqueda|'
            r'(?:find|search for) (?:a )?match|start (?:the )?queue|busque (?:uma )?partida)')
    if re.fullmatch(buscar+juego,n) or n=='fortniteでマッチを検索して':return ('fortnite_buscar','')
    if re.fullmatch(r'(?:(?:cancela(?:r)?|deten|para) (?:la )?(?:cola|busqueda)|cancel (?:the )?(?:queue|matchmaking)|cancele (?:a )?fila)'+juego,n) or n=='fortniteのマッチングをキャンセルして':return ('fortnite_cancelar','')
    if re.fullmatch(r'(?:aplica(?:r)?|prepara) (?:mis |las )?(?:opciones|preferencias)'+juego,n):return ('fortnite_preparar','')
    return None


class ErrorFortnite(Exception):pass


@dataclass(frozen=True)
class Texto:
    texto:str
    rect:tuple


@dataclass(frozen=True)
class Pantalla:
    ventana:int
    rect:tuple
    textos:tuple
    momento:float
    equipos:tuple=()

    def buscar(self,nombres,zona=(0,0,1,1)):
        """Solo etiquetas completas en una zona; la ambigüedad detiene la acción."""
        nombres={clave(n) for n in nombres};x,y,r,b=self.rect;ancho=r-x;alto=b-y
        encontrados=[]
        for t in self.textos:
            l,a,w,h=t.rect;cx=(l+w/2)/ancho;cy=(a+h/2)/alto
            if clave(t.texto) in nombres and zona[0]<=cx<=zona[2] and zona[1]<=cy<=zona[3]:encontrados.append(t)
        return encontrados[0] if len(encontrados)==1 else None

    def contiene(self,frases):
        return any(clave(f) in clave(t.texto) for f in frases for t in self.textos)


JUGAR=('jugar','play','jogar','listo','ready','ready!')
CANCELAR=('cancelar','cancel','cancelar busqueda','cancel matchmaking','no estoy listo','not ready','unready','nao estou pronto')
BUSCANDO=('buscando partida','buscando una partida','buscando emparejamiento','matchmaking','finding match','finding a match','emparejamiento','pareamento')
RESTRICCION=('no eres el lider','not the party leader','solo el lider del grupo','only the party leader','error de emparejamiento','matchmaking error')
LOBBY=(0,.42,.46,1)


class ControlFortnite:
    def __init__(self,vista=None):
        self.vista=vista;self.config=normalizar({});self.estado='Fortnite se comprueba al pulsar una acción.'
        self._lock=threading.Lock();self._stop=threading.Event()

    def configurar(self,config):self.config=normalizar(config)
    def cerrar(self):self._stop.set()

    def _comprobar(self,cancelar):
        if self._stop.is_set() or (cancelar is not None and cancelar.is_set()):raise InterruptedError()
        if time.monotonic()>self._limite:raise ErrorFortnite('Fortnite tardó demasiado en mostrar los controles. Revisa el lobby y vuelve a intentarlo.')

    def _ver(self,cancelar,activar=False):
        self._comprobar(cancelar)
        p=self.vista.capturar(activar=activar);self._comprobar(cancelar)
        if p.contiene(RESTRICCION):raise ErrorFortnite('Fortnite muestra una restricción. Revisa los avisos y el líder del grupo en el juego.')
        return p

    def _pulsar(self,p,t,cancelar):
        self._comprobar(cancelar)
        if t is None:raise ErrorFortnite('No pude identificar ese control de Fortnite. Deja el lobby visible y vuelve a intentarlo.')
        self.vista.pulsar(p,t)
        # Espera de transición acotada; nunca es un reintento del clic.
        if self._stop.wait(.35):raise InterruptedError()
        self._comprobar(cancelar)

    def _esperar(self,condicion,cancelar):
        for _ in range(4):
            p=self._ver(cancelar)
            if condicion(p):return p
            if self._stop.wait(.35):raise InterruptedError()
        return p

    @staticmethod
    def _lobby(p):
        return bool(p.buscar(JUGAR,LOBBY) and p.contiene(('taquilla','locker','vestiario','tienda','item shop')))

    @staticmethod
    def _cola(p):return bool(p.contiene(BUSCANDO) and p.buscar(CANCELAR,LOBBY))

    def _lista(self,p,config):
        if self._cola(p) or p.equipos:return True
        if not self._lobby(p):return False
        return all(config[campo]=='actual' or self._opcion(p,opciones)[0]
                   for campo,opciones in (('modo',MODOS),('equipo',EQUIPOS)))

    @staticmethod
    def _opcion(p,opciones,zona=LOBBY):
        if zona==LOBBY:
            # La tarjeta actual envuelve «Construcción, En / escuadrón,
            # Llenar» en varias líneas. Leer el grupo anclado al modo evita
            # confundirlo con tarjetas de noticias o con el título del menú.
            ancho=p.rect[2]-p.rect[0];alto=p.rect[3]-p.rect[1]
            candidatos=[]
            for t in p.textos:
                if t.rect[0]>ancho*.32 or not alto*.53<t.rect[1]<alto*.85:continue
                n=clave(t.texto)
                for k,v in MODOS.items():
                    for alias in v[1]:
                        if re.match(re.escape(clave(alias))+r'(?:[, ]|$)',n):candidatos.append((len(alias),k,t))
            if candidatos:
                _,modo,t=max(candidatos,key=lambda v:v[0])
                if opciones is MODOS:return modo,t
                grupo=clave(' '.join(x.texto for x in sorted(p.textos,key=lambda x:x.rect[1])
                    if t.rect[1]<=x.rect[1]<t.rect[1]+t.rect[3]*3.2 and abs(x.rect[0]-t.rect[0])<ancho*.08))
                encontrados=[k for k,v in opciones.items() if any(re.search(r'(?<!\w)'+re.escape(clave(a))+r'(?!\w)',grupo) for a in v[1])]
                if len(encontrados)==1:return encontrados[0],t
        coincidencias=[(k,p.buscar(v[1],zona)) for k,v in opciones.items() if v[1]]
        coincidencias=[(k,t) for k,t in coincidencias if t]
        return coincidencias[0] if len(coincidencias)==1 else ('',None)

    @staticmethod
    def _boton_modo(p,modo):
        zona=(.56,0,1,.23);exacto=p.buscar(MODOS[modo][1],zona)
        if exacto:return exacto
        # La tipografía de Fortnite puede convertir la C inicial en «}».
        # Tolerar una sola letra únicamente dentro del menú ya reconocido.
        if len(p.equipos)!=4:return None
        from core import error_de_una_letra
        ancho=p.rect[2]-p.rect[0];alto=p.rect[3]-p.rect[1]
        candidatos=[t for t in p.textos if t.rect[0]>ancho*.56 and t.rect[1]<alto*.23
            and any(len(a)>7 and error_de_una_letra(clave(t.texto),clave(a)) for a in MODOS[modo][1])]
        return candidatos[0] if len(candidatos)==1 else None

    def _preparar(self,p,config,cancelar):
        if not self._lobby(p):raise ErrorFortnite('Deja Fortnite en el lobby de Battle Royale o Cero construcción, con el botón Jugar visible.')
        modo,actual=self._opcion(p,MODOS)
        equipo,t_equipo=self._opcion(p,EQUIPOS)
        cambios=any(config[k]!='actual' and config[k]!=v for k,v in (('modo',modo),('equipo',equipo)))
        if cambios:
            self._pulsar(p,actual or t_equipo,cancelar)
            p=self._esperar(lambda q:len(q.equipos)==4,cancelar)
            # Menú actual: dos experiencias y cuatro botones con siluetas.
            # Se reconocen los rectángulos de la fila; no se usan puntos fijos.
            if p.equipos:
                if config['modo']!='actual' and modo!=config['modo']:
                    self._pulsar(p,self._boton_modo(p,config['modo']),cancelar)
                    p=self._esperar(lambda q:len(q.equipos)==4,cancelar)
                if config['equipo']!='actual' and self._opcion(p,EQUIPOS,(.57,.24,.78,.47))[0]!=config['equipo']:
                    if len(p.equipos)!=4:raise ErrorFortnite('No pude leer los cuatro botones del equipo. Revisa las opciones de Fortnite.')
                    self._pulsar(p,p.equipos[('solo','duo','trio','squad').index(config['equipo'])],cancelar)
                    p=self._esperar(lambda q:self._opcion(q,EQUIPOS,(.57,.24,.78,.47))[0]==config['equipo'],cancelar)
                    if self._opcion(p,EQUIPOS,(.57,.24,.78,.47))[0]!=config['equipo']:
                        raise ErrorFortnite('Fortnite no confirmó el tamaño del equipo. No inicié la búsqueda.')
                self._comprobar(cancelar);self.vista.volver(p)
                p=self._esperar(self._lobby,cancelar)
                if not self._lobby(p):raise ErrorFortnite('No pude volver al lobby de Fortnite. Revisa el juego.')
                for campo,opciones in (('modo',MODOS),('equipo',EQUIPOS)):
                    if config[campo]!='actual' and self._opcion(p,opciones)[0]!=config[campo]:
                        raise ErrorFortnite('No pude confirmar las opciones en el lobby de Fortnite. No inicié la búsqueda.')
                return p
            raise ErrorFortnite('No pude leer el menú de opciones de Fortnite. No inicié la búsqueda.')
        return p

    def ejecutar(self,accion,valor='',cancelar=None):
        if accion not in ('fortnite_buscar','fortnite_cancelar','fortnite_preparar'):return ''
        if not self._lock.acquire(False):return 'Ya estoy comprobando una acción de Fortnite.'
        try:
            self._limite=time.monotonic()+65
            if self.vista is None:
                from fortnite_vision import VistaFortnite
                self.vista=VistaFortnite()
            config=dict(self.config);self.estado='Comprobando el lobby de Fortnite…'
            p=self._ver(cancelar,activar=True)
            if not self._lista(p,config):
                # Al salir de minimizado el juego puede devolver primero su
                # pantalla de transición. Solo repetir lecturas, nunca clics.
                p=self._esperar(lambda q:self._lista(q,config),cancelar)
            if p.equipos:
                # Puede haberse minimizado dejando abiertas las opciones.
                self._comprobar(cancelar);self.vista.volver(p)
                p=self._esperar(self._lobby,cancelar)
            if accion=='fortnite_cancelar':
                if not self._cola(p):self.estado='No pude confirmar una búsqueda activa en Fortnite.';return self.estado
                self._pulsar(p,p.buscar(CANCELAR,LOBBY),cancelar)
                p=self._esperar(self._lobby,cancelar)
                self.estado=('Fortnite confirmó la cancelación. Esperaré una nueva orden para buscar.' if self._lobby(p)
                             else 'Pedí cancelar en Fortnite. Comprueba el resultado en el juego.')
                return self.estado
            if self._cola(p):self.estado='Fortnite ya está buscando partida.';return self.estado
            p=self._preparar(p,config,cancelar)
            if accion=='fortnite_preparar':self.estado='Opciones confirmadas en Fortnite. La búsqueda espera tu orden.';return self.estado
            # Otra lectura antes del único clic que puede iniciar una partida.
            p=self._ver(cancelar)
            if not self._lobby(p):raise ErrorFortnite('El lobby cambió. Comprueba Fortnite antes de volver a buscar.')
            for campo,opciones in (('modo',MODOS),('equipo',EQUIPOS)):
                if config[campo]!='actual' and self._opcion(p,opciones)[0]!=config[campo]:
                    raise ErrorFortnite('Las opciones de Fortnite cambiaron. No inicié la búsqueda.')
            self._pulsar(p,p.buscar(JUGAR,LOBBY),cancelar)
            p=self._esperar(self._cola,cancelar)
            self.estado=('Fortnite confirmó que está buscando partida.' if self._cola(p)
                         else 'Pulsé Jugar en Fortnite; todavía no pude confirmar la cola. Revisa el juego.')
            return self.estado
        except ErrorFortnite as e:self.estado=str(e);return self.estado
        finally:self._lock.release()
