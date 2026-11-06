"""Preferencias por línea y confirmación acotada al turno local de selección."""
import copy
import json
import threading
from pathlib import Path
from league import ClienteLCU,ErrorCliente,FASE

ROLES=('TOP','JUNGLE','MIDDLE','BOTTOM','UTILITY')
NOMBRES=('Top','Jungla','Medio','ADC','Soporte')
SESION='/lol-champ-select/v1/session'
PICK='/lol-champ-select/v1/pickable-champion-ids'
BAN='/lol-champ-select/v1/bannable-champion-ids'
FICHA='/lol-champ-select/v1/grid-champions/'
APAGADO='Picks y baneos automáticos desactivados'
ESPERANDO='Esperando tu turno en selección de campeón'
SIN_LINEA='Esta selección no tiene una línea asignada; elige desde LoL'
SIN_OPCIONES='No quedan opciones disponibles; elige desde LoL'
MANUAL='Selección manual detectada; continúa desde LoL'
ENVIADO='Confirmación enviada; comprueba el resultado en LoL'
CONFIRMADO='LoL confirmó tu selección'
CONEXION='Esperando conexión con el cliente de LoL'
ERROR='LoL no confirmó la acción; continúa desde el cliente'
ESTADOS=(APAGADO,ESPERANDO,SIN_LINEA,SIN_OPCIONES,MANUAL,ENVIADO,CONFIRMADO,CONEXION,ERROR)


def carpeta_catalogo():
    base=Path(__file__).resolve().parent
    return next((p for p in (base/'assets/lol',base.parent/'assets/lol') if (p/'campeones.json').is_file()),base/'assets/lol')


def cargar_catalogo():
    try:return json.loads((carpeta_catalogo()/'campeones.json').read_text(encoding='utf8'))
    except (OSError,ValueError):return {'version':'','champions':[]}


def normalizar(config):
    config=config if isinstance(config,dict) else {}
    perfiles=config.get('roles',{})
    if not isinstance(perfiles,dict):perfiles={}
    resultado={'auto_pick':config.get('auto_pick') is True,'auto_ban':config.get('auto_ban') is True,'roles':{}}
    for rol in ROLES:
        perfil=perfiles.get(rol,{})
        if not isinstance(perfil,dict):perfil={}
        resultado['roles'][rol]={}
        for tipo in ('pick','ban'):
            lista=perfil.get(tipo,[]);limpia=[]
            if isinstance(lista,list):
                for valor in lista[:3]:
                    valor=valor if type(valor) is int and 0<valor<100000 and valor not in limpia else 0
                    limpia.append(valor)
            resultado['roles'][rol][tipo]=(limpia+[0]*3)[:3]
    return resultado


def turno(sesion):
    if not isinstance(sesion,dict) or sesion.get('timer',{}).get('phase')!='BAN_PICK':return None
    celda=sesion.get('localPlayerCellId')
    if type(celda) is not int or celda<0:return None
    jugador=next((j for j in sesion.get('myTeam',[]) if j.get('cellId')==celda),{})
    rol=str(jugador.get('assignedPosition','')).upper()
    acciones=[a for grupo in sesion.get('actions',[]) for a in grupo
              if a.get('actorCellId')==celda and a.get('isInProgress') is True and a.get('completed') is False
              and a.get('type') in ('pick','ban') and type(a.get('id')) is int and a['id']>=0]
    return (rol,acciones[0],jugador) if len(acciones)==1 else None


def candidato(sesion,lista,disponibles,tipo):
    ocupados={j.get('championId',0) for equipo in ('myTeam','theirTeam') for j in sesion.get(equipo,[])}
    for grupo in sesion.get('actions',[]):
        ocupados.update(a.get('championId',0) for a in grupo if a.get('completed'))
    for equipo in ('myTeamBans','theirTeamBans'):ocupados.update(sesion.get('bans',{}).get(equipo,[]))
    if tipo=='ban':ocupados.update(j.get('championPickIntent',0) for j in sesion.get('myTeam',[]))
    disponibles={v for v in disponibles if type(v) is int and v>0}
    return next((v for v in lista if v and v in disponibles and v not in ocupados),None)


class ControlSeleccion:
    """No busca ni acepta partidas. Una petición como máximo por turno local."""
    def __init__(self,cliente=None):
        self.cliente=cliente or ClienteLCU();self.config=normalizar({});self.estado=APAGADO
        self._lock=threading.RLock();self._stop=threading.Event();self._stop.set()
        self.hilo=None;self._intentos=set()

    def configurar(self,config,iniciar=True):
        # Reemplazo atómico de una instantánea; guardar desde Tk nunca espera una petición LCU.
        self.config=normalizar(config)
        activo=self.config['auto_pick'] or self.config['auto_ban']
        self.estado=ESPERANDO if activo else APAGADO
        if not activo:self._stop.set()
        elif iniciar and (self.hilo is None or not self.hilo.is_alive() or self._stop.is_set()):
            self._stop.set();self._stop=threading.Event()
            self.hilo=threading.Thread(target=self._vigilar,args=(self._stop,),daemon=True);self.hilo.start()

    def cerrar(self):
        self._stop.set()

    def revisar(self,cancelar=None):
        # Serializa monitores viejos/nuevos durante una reconexión o un cambio de preferencias.
        with self._lock:self._revisar(cancelar)

    def _revisar(self,cancelar=None):
        cancelar=cancelar or threading.Event()
        with self._lock:config=copy.deepcopy(self.config)
        if cancelar.is_set() or not (config['auto_pick'] or config['auto_ban']):return
        if self.cliente.pedir('GET',FASE)!='ChampSelect':
            self._intentos.clear();self.estado=ESPERANDO;return
        sesion=self.cliente.pedir('GET',SESION);actual=turno(sesion)
        if not actual:self.estado=ESPERANDO;return
        rol,accion,jugador=actual;tipo=accion['type']
        if rol not in ROLES:self.estado=SIN_LINEA;return
        if not config['auto_'+tipo]:return
        if accion.get('championId',0) or (tipo=='pick' and jugador.get('championPickIntent',0)):
            self.estado=MANUAL;return
        clave=(sesion.get('gameId'),accion['id'],sesion.get('localPlayerCellId'),tipo)
        if clave in self._intentos:return
        ruta=PICK if tipo=='pick' else BAN
        disponibles=self._disponibles(ruta,tipo,config['roles'][rol][tipo],cancelar)
        elegido=candidato(sesion,config['roles'][rol][tipo],disponibles,tipo)
        if not elegido:self.estado=SIN_OPCIONES;return
        # Revalidar el turno, los hovers y la disponibilidad después de las lecturas.
        if cancelar.is_set() or self.cliente.pedir('GET',FASE)!='ChampSelect':return
        nueva=self.cliente.pedir('GET',SESION);ahora=turno(nueva)
        if not ahora or ahora!=actual or nueva.get('gameId')!=sesion.get('gameId'):return
        disponibles=self._disponibles(ruta,tipo,config['roles'][rol][tipo],cancelar)
        if candidato(nueva,config['roles'][rol][tipo],disponibles,tipo)!=elegido:return
        if tipo=='ban':
            # Las fichas pueden requerir varias lecturas: comprobar otra vez
            # el turno y los hovers después de consultarlas.
            if cancelar.is_set() or self.cliente.pedir('GET',FASE)!='ChampSelect':return
            final=self.cliente.pedir('GET',SESION)
            if turno(final)!=actual or final.get('gameId')!=sesion.get('gameId'):return
            if candidato(final,config['roles'][rol][tipo],disponibles,tipo)!=elegido:return
        with self._lock:
            if cancelar.is_set() or config!=self.config:return
            self._intentos.add(clave)
            self.estado=ENVIADO
            try:self.cliente.pedir('PATCH',SESION+'/actions/'+str(accion['id']),{'championId':elegido,'completed':True})
            except ErrorCliente:
                if not cancelar.is_set() and config==self.config:self.estado=ERROR
                return
        resultado=self.cliente.pedir('GET',SESION)
        if cancelar.is_set() or config!=self.config:return
        if any(a.get('id')==accion['id'] and a.get('completed') is True and a.get('championId')==elegido
               for grupo in resultado.get('actions',[]) for a in grupo):self.estado=CONFIRMADO

    def _disponibles(self,ruta,tipo,lista,cancelar):
        disponibles=self.cliente.pedir('GET',ruta)
        if not isinstance(disponibles,list):raise ErrorCliente()
        # Algunos clientes devuelven solo -1 ("ningún baneo") incluso durante
        # un turno válido. Verificado en el cliente real: la ficha individual
        # sí informa disabled/selectionStatus. No alterar listas positivas ni picks.
        if tipo!='ban' or any(type(v) is not int or v not in (-1,0) for v in disponibles):return disponibles
        disponibles=[]
        for identificador in lista:
            if cancelar.is_set():return []
            if not identificador:continue
            ficha=self.cliente.pedir('GET',FICHA+str(identificador))
            if not isinstance(ficha,dict):continue
            estado=ficha.get('selectionStatus')
            if (type(ficha.get('id')) is int and ficha['id']==identificador and ficha.get('disabled') is False
                and isinstance(estado,dict) and estado.get('isBanned') is False
                and estado.get('pickedByOtherOrBanned') is False
                and not estado.get('banIntented') and not estado.get('banIntentedByMe')
                and not estado.get('selectedByMe')):
                disponibles.append(identificador)
        return disponibles

    def _vigilar(self,stop):
        while not stop.is_set():
            try:self.revisar(stop)
            except (ErrorCliente,ValueError,TypeError,KeyError,AttributeError):
                if not stop.is_set():self.estado=CONEXION
            stop.wait(1.2 if self.estado==CONEXION else .6)
