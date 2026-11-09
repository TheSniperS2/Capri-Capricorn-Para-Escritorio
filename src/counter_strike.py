"""Mapas y cola de CS2 mediante controles visibles, solo por orden explícita."""
from dataclasses import dataclass
import re,threading,time,unicodedata
from fortnite import Pantalla,Texto

MAPAS=('Dust II','Mirage','Inferno','Nuke','Ancient','Anubis','Cache','Train','Overpass','Vertigo','Office','Italy')
NOMBRES_MAPAS=(*MAPAS,'Basalt','Edin','Stronghold','Alpine','Warren','Boulder','Fachwerk','Shelter','Palacio','Golden','Agency')


def clave(t):
    t=''.join(c for c in unicodedata.normalize('NFD',str(t).casefold()) if unicodedata.category(c)!='Mn')
    return ' '.join(re.sub(r'[^\w\s]',' ',t).split())


def nombre_mapa(t):
    if not isinstance(t,str) or not 2<=len(t.strip())<=40:return ''
    t=t.strip(' ._•·!?,;:-')
    n=clave(t)
    if n in ('dust 2','dust ii','dust2'):return 'Dust II'
    for nombre in NOMBRES_MAPAS:
        if n==clave(nombre):return nombre
    if not re.fullmatch(r'[\w]+(?:[ -][\w]+){0,2}',t.strip()) or not any(c.isalpha() for c in t):return ''
    if n in ('wait time','tiempo de espera','tempo de espera','competitive','competitivo','premier','matchmaking') or n.replace(' ','') in ('wait','time','waittime','wailtime','wins','needed','winsneeded'):return ''
    return t.strip()


def normalizar(c):
    c=c if isinstance(c,dict) else {};salida={}
    for k in ('mapas','detectados'):
        valores=c.get(k,[]);v=[]
        for s in valores[:40] if isinstance(valores,list) else []:
            s=nombre_mapa(s)
            if s and clave(s) not in {clave(x) for x in v}:v.append(s)
        salida[k]=v
    return salida


def interpretar_cs2(texto):
    if texto.lstrip().startswith(('"',"'",'«','“')):return None
    n=clave(texto);juego=r'(?:counter ?strike(?: 2)?|counter|cs ?2|cs ?go)'
    sufijo=r' (?:en|in|no|de|del) (?:el |the |o )?'+juego
    buscar=r'(?:(?:busca(?:r)?(?:me)?|busques|busque) (?:una |la |uma )?partida|(?:tira|inicia|pon|lanza|start) (?:la |una |the )?(?:cola|busqueda|partida|queue)|(?:find|search for) (?:a )?match)'
    cancelar=r'(?:(?:cancela(?:r)?|deten|para|cancele|cancel) (?:la |a |the )?(?:cola|busqueda|fila|queue|matchmaking))'
    if re.fullmatch(buscar+sufijo,n):return ('cs2_buscar','')
    if re.fullmatch(cancelar+sufijo,n):return ('cs2_cancelar','')
    if re.fullmatch(r'(?:acepta(?:r)? (?:la )?partida|accept (?:the )?match|aceite (?:a )?partida)'+sufijo,n):return ('cs2_aceptar','')
    if re.fullmatch(r'(?:aplica(?:r)?|prepara) (?:mis |los |las )?(?:mapas|opciones|preferencias)'+sufijo,n):return ('cs2_preparar','')
    if re.fullmatch(r'(?:lee|leer|detecta|sincroniza|actualiza) (?:los )?mapas'+sufijo,n):return ('cs2_leer','')
    if re.fullmatch(r'(?:configura(?:r)?|abre) (?:el panel de )?'+juego,n):return ('cs2_panel','')
    if n in ('cs2でマッチを検索して','counter strike 2でマッチを検索して'):return ('cs2_buscar','')
    if n=='cs2のマッチングをキャンセルして':return ('cs2_cancelar','')
    return None


class ErrorCS2(Exception):pass


@dataclass(frozen=True)
class MapaVisible:
    nombre:str
    control:Texto
    seleccionado:bool


@dataclass(frozen=True)
class PantallaCS2(Pantalla):
    mapas:tuple=()
    completa:bool=False
    online:bool=False
    competitivo:bool=False

    def buscar(self,nombres,zona=(0,0,1,1)):
        if tuple(nombres) in (EMPAREJAMIENTO,COMPETITIVO):return cabecera(self,nombres,zona)
        w=self.rect[2]-self.rect[0];h=self.rect[3]-self.rect[1];alias={clave(n) for n in nombres}
        encontrados=[t for t in self.textos if clave(t.texto) in alias and zona[0]<=(t.rect[0]+t.rect[2]/2)/w<=zona[2] and zona[1]<=(t.rect[1]+t.rect[3]/2)/h<=zona[3]]
        if not encontrados:return None
        mayor=max(encontrados,key=lambda t:t.rect[2]*t.rect[3]);x,y,an,al=mayor.rect
        return mayor if all(x-2<=t.rect[0]+t.rect[2]/2<=x+an+2 and y-2<=t.rect[1]+t.rect[3]/2<=y+al+2 for t in encontrados) else None


BUSCAR=('go','iniciar','empezar','buscar partida','encontrar partida','comecar','começar','jogar','開始')
CANCELAR=('cancelar','cancel','cancel search','cancelar busqueda','cancelar busca','キャンセル')
COLA=('buscando partida','buscando jugadores','buscando servidores','searching for','matchmaking search','procurando partida','procurando jogadores','マッチを検索')
BLOQUEO=('match ready','tu partida esta lista','partida encontrada','competitive cooldown',
         'suspension competitiva','no se pudo conectar','failed to connect','fase de compra','buy menu',
         'tiempo de compra','vac error','vac no pudo','no eres el lider','not the lobby leader','waiting for lobby leader')
EMPAREJAMIENTO=('emparejamiento','matchmaking','pareamento','マッチメイキング')
COMPETITIVO=('competitivo','competitive','対戦')
JUGAR=('jugar','play','jogar','プレイ')
ZONA_BOTON=(.62,.82,1,1)


def cabecera(p,nombres,zona):
    from core import error_de_una_letra
    w=p.rect[2]-p.rect[0];h=p.rect[3]-p.rect[1];candidatos=[]
    for t in p.textos:
        x,y,an,al=t.rect;cx=(x+an/2)/w;cy=(y+al/2)/h;n=clave(t.texto).replace(' ','')
        if not zona[0]<=cx<=zona[2] or not zona[1]<=cy<=zona[3]:continue
        def distancia(a,b):
            fila=list(range(len(b)+1))
            for i,ca in enumerate(a,1):
                nueva=[i]
                for j,cb in enumerate(b,1):nueva.append(min(nueva[-1]+1,fila[j]+1,fila[j-1]+(ca!=cb)))
                fila=nueva
            return fila[-1]
        if any(n==clave(a).replace(' ','') or len(n)>=8 and error_de_una_letra(n,clave(a).replace(' ',''))
               or len(n)>=10 and distancia(n,clave(a).replace(' ',''))<=2 for a in nombres):candidatos.append(t)
    if not candidatos:return None
    candidatos.sort(key=lambda t:t.rect[1]);primero=candidatos[0]
    otros=[t for t in candidatos[1:] if abs(t.rect[1]-primero.rect[1])<primero.rect[3] and abs(t.rect[0]-primero.rect[0])>primero.rect[2]*.4]
    return None if otros else primero


class ControlCS2:
    def __init__(self,vista=None):
        self.vista=vista;self.config=normalizar({});self.estado='Counter-Strike 2 se comprueba al pulsar una acción.'
        self.catalogo=();self.version=0;self._lock=threading.Lock();self._datos=threading.RLock();self._stop=threading.Event()

    def configurar(self,c):
        with self._datos:self.config=normalizar(c);self.version+=1

    def cerrar(self):
        self._stop.set()
        if self.vista is not None and callable(getattr(self.vista,'cerrar',None)):
            threading.Thread(target=self.vista.cerrar,daemon=True).start()

    def _comprobar(self,cancelar):
        if self._stop.is_set() or cancelar is not None and cancelar.is_set():raise InterruptedError()
        if self._version!=self.version:raise ErrorCS2('Tus mapas cambiaron durante la operación. Vuelve a pedirla con las preferencias actuales.')
        if time.monotonic()>self._limite:raise ErrorCS2('Counter-Strike 2 tardó demasiado. Deja preparado el menú Jugar y vuelve a pedirlo.')

    def _ver(self,cancelar,activar=False):
        self._comprobar(cancelar);p=self.vista.capturar(activar=activar);self._comprobar(cancelar)
        if p.contiene(BLOQUEO) or p.buscar(('aceptar','accept','reconnect','reconectar','volver a conectar','abandonar','abandon match'),(.1,.1,.9,.9)):
            raise ErrorCS2('Counter-Strike muestra una partida, una confirmación o una restricción. Revisa el juego antes de pedir otra acción.')
        return p

    def _clic(self,p,t,cancelar):
        self._comprobar(cancelar)
        if t is None:raise ErrorCS2('No pude identificar ese control de Counter-Strike. Deja el menú visible y vuelve a intentarlo.')
        self.vista.pulsar(p,t)
        if self._stop.wait(.25):raise InterruptedError()
        self._comprobar(cancelar)

    def _esperar(self,condicion,cancelar):
        for _ in range(4):
            p=self._ver(cancelar)
            if condicion(p):return p
            if self._stop.wait(.25):raise InterruptedError()
        return p

    @staticmethod
    def _cola(p):return bool(p.contiene(COLA) and p.buscar(CANCELAR,ZONA_BOTON))

    def _menu(self,p,cancelar):
        if p.online and p.competitivo and p.mapas:return p
        if not p.buscar(EMPAREJAMIENTO,(.1,0,.9,.25)):
            t=p.buscar(JUGAR,(.15,0,.85,.16))
            self._clic(p,t,cancelar);p=self._esperar(lambda q:q.buscar(EMPAREJAMIENTO,(.1,0,.9,.25)),cancelar)
        if not p.online:
            self._clic(p,p.buscar(EMPAREJAMIENTO,(.1,0,.9,.25)),cancelar)
            p=self._esperar(lambda q:q.online,cancelar)
        if not p.online:raise ErrorCS2('Deja abierto Jugar, Emparejamiento en Counter-Strike 2. No inicié ninguna partida.')
        if not p.competitivo:
            self._clic(p,p.buscar(COMPETITIVO,(.1,0,.9,.3)),cancelar)
            p=self._esperar(lambda q:q.competitivo and q.mapas,cancelar)
        if not p.online or not p.competitivo or not p.mapas:raise ErrorCS2('No pude confirmar el menú Competitivo con sus mapas. Deja ese menú visible en el juego.')
        return p

    @staticmethod
    def _seleccion(p):return {clave(m.nombre) for m in p.mapas if m.seleccionado}

    def _validar_mapas(self,p,deseados):
        if not p.online or not p.competitivo or not p.completa:raise ErrorCS2('No pude leer todas las casillas de mapas. Deja completa la selección de Competitivo visible; no inicié la búsqueda.')
        disponibles={clave(m.nombre) for m in p.mapas}
        faltan=deseados-disponibles
        if faltan:raise ErrorCS2('Hay mapas guardados que no aparecen en este menú. Usa Leer mapas del juego y revisa tu selección antes de buscar.')

    def ejecutar(self,accion,valor='',cancelar=None):
        if accion=='cs2_aceptar':
            self.estado='La aceptación de partida en Counter-Strike es manual. Confírmala desde el juego.';return self.estado
        if accion not in ('cs2_buscar','cs2_cancelar','cs2_preparar','cs2_leer'):return ''
        if not self._lock.acquire(False):return 'Ya estoy comprobando una acción de Counter-Strike.'
        try:
            with self._datos:config=normalizar(self.config);self._version=self.version
            if accion=='cs2_leer':self.catalogo=()
            self._limite=time.monotonic()+75;deseados={clave(s) for s in config['mapas']}
            if accion in ('cs2_buscar','cs2_preparar') and not deseados:
                self.estado='Elige al menos un mapa en el panel de Counter-Strike antes de buscar.';return self.estado
            if self.vista is None:
                from counter_strike_vision import VistaCS2
                self.vista=VistaCS2()
            self.estado='Comprobando Counter-Strike 2…';p=self._ver(cancelar,activar=True)
            if accion=='cs2_cancelar':
                if not self._cola(p):self.estado='No pude confirmar una búsqueda activa de Counter-Strike.';return self.estado
                self._clic(p,p.buscar(CANCELAR,ZONA_BOTON),cancelar)
                p=self._esperar(lambda q:not self._cola(q) and q.buscar(BUSCAR,ZONA_BOTON),cancelar)
                self.estado=('Counter-Strike confirmó la cancelación. Esperaré una nueva orden para buscar.' if not self._cola(p) and p.buscar(BUSCAR,ZONA_BOTON)
                             else 'Pedí cancelar en Counter-Strike. Comprueba el resultado en el juego.')
                return self.estado
            if self._cola(p):self.estado='Counter-Strike ya está buscando partida.';return self.estado
            p=self._menu(p,cancelar);self._validar_mapas(p,set())
            self.catalogo=tuple(m.nombre for m in p.mapas)
            if accion=='cs2_leer':self.estado='Mapas visibles de Counter-Strike leídos. Elige tus preferencias en el panel.';return self.estado
            self._validar_mapas(p,deseados)
            originales={clave(m.nombre) for m in p.mapas}
            # Activar primero los deseados evita pasar por una selección vacía.
            cambios=[clave(m.nombre) for m in p.mapas if clave(m.nombre) in deseados and not m.seleccionado]
            cambios += [clave(m.nombre) for m in p.mapas if clave(m.nombre) not in deseados and m.seleccionado]
            for ident in cambios:
                self._comprobar(cancelar);self._validar_mapas(p,deseados)
                if {clave(m.nombre) for m in p.mapas}!=originales:raise ErrorCS2('La lista de mapas cambió durante la operación. Revisa Counter-Strike antes de buscar.')
                m=next(m for m in p.mapas if clave(m.nombre)==ident);estado=ident in deseados
                if m.seleccionado==estado:raise ErrorCS2('La selección cambió mientras la comprobaba. No inicié la búsqueda.')
                anterior=self._seleccion(p);esperada=(anterior|{ident}) if estado else anterior-{ident}
                self._clic(p,m.control,cancelar)
                p=self._esperar(lambda q:q.completa and self._seleccion(q)==esperada,cancelar)
                if self._seleccion(p)!=esperada:raise ErrorCS2('No pude confirmar el cambio de mapa. No repetiré el clic ni iniciaré la búsqueda.')
            p=self._ver(cancelar);self._validar_mapas(p,deseados)
            if self._seleccion(p)!=deseados:raise ErrorCS2('Los mapas visibles no coinciden con tus preferencias. No inicié la búsqueda.')
            if accion=='cs2_preparar':self.estado='Mapas confirmados en Counter-Strike. La búsqueda espera tu orden.';return self.estado
            self._clic(p,p.buscar(BUSCAR,ZONA_BOTON),cancelar)
            p=self._esperar(self._cola,cancelar)
            self.estado=('Counter-Strike confirmó que está buscando partida.' if self._cola(p)
                         else 'Pulsé Buscar en Counter-Strike; todavía no pude confirmar la cola. Revisa el juego antes de pedir otra búsqueda.')
            return self.estado
        except ErrorCS2 as e:self.estado=str(e);return self.estado
        finally:self._lock.release()
