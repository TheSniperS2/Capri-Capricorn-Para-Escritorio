"""Cola y selección de agentes; ninguna acción dentro de una partida."""
import copy
import json
from pathlib import Path
import re
import threading
import time
import unicodedata
from valorant_cliente import ClienteValorant,ErrorValorant,AGENTES,uuid

MENSAJES={
 'cliente':'Abre Valorant y deja preparada una sala para conectar con Capri.',
 'conexion':'No pude conectar con Valorant. Comprueba el cliente y tu conexión.',
 'sesion':'La sesión de Valorant cambió. Vuelve a intentarlo con el juego abierto.',
 'region':'No pude identificar la región de Valorant. Abre el juego y vuelve a intentarlo.',
 'version':'No pude identificar la versión del cliente de Valorant.',
 'rechazo':'Valorant rechazó la acción. Revisa los avisos del juego.',
 'apagado':'Selección automática de agentes desactivada',
 'esperando':'Esperando la selección de agentes de Valorant',
 'seleccion':'Selección de agentes disponible',
 'sin_opciones':'Tus agentes no están disponibles. Capri no elegirá otro fuera de tus preferencias.',
 'manual':'Selección manual detectada; continúa desde Valorant',
 'confirmado':'Valorant confirmó tu agente',
 'enviado':'Selección enviada; comprueba el resultado en Valorant',
 'preparando':'Comprobando tus preferencias de agente',
 'buscando':'Valorant confirmó que la búsqueda está en marcha.',
 'solicitud':'Envié la búsqueda; Valorant todavía no la confirmó.',
 'cancelada':'Valorant confirmó la cancelación. No volveré a iniciar la búsqueda.',
 'cancelando':'Pedí cancelar la búsqueda; comprueba el resultado en Valorant.',
 'sin_cola':'No hay una búsqueda activa en Valorant.',
 'sala':'Prepara una sala y elige el modo desde Valorant.',
 'lider':'Solo el líder del grupo puede iniciar o cancelar esta búsqueda.',
 'partida':'Ya estás en selección de agentes o en partida. No cambié la cola.',
 'pausa':'La búsqueda se detuvo. Esperaré a que vuelvas a iniciarla.',
 'penalizacion':'Valorant indica una restricción para buscar. Revisa el aviso del juego.',
}

# El servidor anuncia la selección antes de terminar la presentación del mapa.
ESPERA_PRESENTACION=6.0

def interpretar_valorant(texto):
    n=unicodedata.normalize('NFC',''.join(c for c in unicodedata.normalize('NFD',texto.casefold())
        if not (unicodedata.category(c)=='Mn' and 0x300<=ord(c)<=0x36f))).strip(' .!?¿¡')
    n=re.sub(r'^(?:por favor[, ]+|please |can you |could you |voce pode )','',n)
    n=re.sub(r'[, ]+(?:por favor|please)$','',n)
    juego=r'\s+(?:(?:en|in|on|no|do|de)\s+(?:el\s+|o\s+|the\s+)?|del\s+)(?:valorant|valo)'
    elegir=r'(?:confirma|elige|selecciona|pickea) (?:mi|el) (?:agente|personaje)'
    if re.fullmatch(elegir+juego,n) or n in ('confirm my agent in valorant','confirme meu agente no valorant','valorantでエージェントを確定して'):return ('valorant_elegir','')
    buscar=(r'(?:(?:busca(?:r)?(?:me)?|busques) (?:una |la )?partida'
            r'|(?:inicia(?:r)?|inicies|tira(?:r)?|tires|pon|poner|pongas|ponme|lanza|lanzar|lances) (?:una |la |en )?(?:cola|partida|busqueda)'
            r'|(?:realiza(?:r)?|realices) (?:una |la )?busqueda'
            r'|dale a buscar (?:una |la )?partida'
            r'|(?:find|search for) (?:a )?match|start (?:the )?queue|busque (?:uma )?partida)')
    if re.fullmatch(buscar+juego,n) or n=='valorantでマッチを検索して':return ('valorant_buscar','')
    if re.fullmatch(r'(?:(?:cancela(?:r)?|deten|para) (?:la )?(?:cola|busqueda)|cancel (?:the )?(?:queue|matchmaking)|cancele (?:a )?fila)'+juego,n) or n=='valorantのマッチングをキャンセルして':return ('valorant_cancelar','')
    return None

def carpeta_catalogo():
    base=Path(__file__).resolve().parent
    return next((p for p in (base/'assets/valorant',base.parent/'assets/valorant') if (p/'agentes.json').is_file()),base/'assets/valorant')

def cargar_catalogo():
    try:return json.loads((carpeta_catalogo()/'agentes.json').read_text(encoding='utf8'))
    except (OSError,ValueError):return {'version':'','agents':[]}

def normalizar(config):
    config=config if isinstance(config,dict) else {};lista=config.get('preferencias',[]);limpia=[]
    if isinstance(lista,list):
        for v in lista[:3]:limpia.append(v.lower() if isinstance(v,str) and uuid(v.lower()) and v.lower() not in limpia else '')
    return {'auto_pick':config.get('auto_pick') is True,'preferencias':(limpia+['']*3)[:3]}

def jugador_local(partida,sujeto):
    equipo=partida.get('AllyTeam')
    if not isinstance(equipo,dict):return None
    return next((p for p in equipo.get('Players',[]) if p.get('Subject')==sujeto),None)

def candidato(partida,lista,sujeto,disponibles):
    # También respetar un agente que el aliado esté señalando, sin esperar al lock.
    ocupados={p.get('CharacterID','').lower() for p in (partida.get('AllyTeam') or {}).get('Players',[])
              if p.get('Subject')!=sujeto and p.get('CharacterSelectionState') in ('selected','locked')}
    return next((v for v in lista if v and v in disponibles and v not in ocupados),None)

def propios(entitlements,base):
    if not isinstance(entitlements,dict):raise ErrorValorant()
    listas=[]
    if isinstance(entitlements.get('Entitlements'),list):listas.append(entitlements['Entitlements'])
    for grupo in entitlements.get('EntitlementsByTypes',[]):
        if grupo.get('ItemTypeID')==AGENTES and isinstance(grupo.get('Entitlements'),list):listas.append(grupo['Entitlements'])
    if not listas and 'Entitlements' not in entitlements and 'EntitlementsByTypes' not in entitlements:raise ErrorValorant()
    return set(base)|{p['ItemID'].lower() for lista in listas for p in lista if uuid(p.get('ItemID'))}

class ControlValorant:
    def __init__(self,cliente=None,reloj=time.monotonic):
        self.cliente=cliente or ClienteValorant();self.config=normalizar({})
        self.estado=MENSAJES['apagado'];self.cola_estado=MENSAJES['cliente']
        self._lock=threading.RLock();self._stop=threading.Event();self._stop.set();self.hilo=None
        self._partida=None;self._intentados=set();self._confirmados=set();self._pendiente=None
        self._base={a['id'] for a in cargar_catalogo()['agents'] if a.get('base') is True}
        self._ultimo_estado=None
        self._reloj=reloj;self._preparacion=None

    def _seleccion_preparada(self,match,partida,local):
        mapa=partida.get('MapID');restante=partida.get('PhaseTimeRemainingNS')
        if (partida.get('PregameState')!='character_select_active' or not isinstance(mapa,str) or not mapa.strip()
            or type(restante) is not int or restante<=0
            or not local or local.get('PregamePlayerState')!='joined'):
            self._preparacion=None;return False
        clave=(match,mapa)
        if not self._preparacion or self._preparacion[:2]!=clave:
            self._preparacion=(*clave,self._reloj())
        return self._reloj()-self._preparacion[2]>=ESPERA_PRESENTACION

    def configurar(self,config,iniciar=True):
        self.config=normalizar(config)
        self.estado=MENSAJES['esperando' if self.config['auto_pick'] else 'apagado']
        if not self.config['auto_pick']:self._stop.set()
        elif iniciar and (self.hilo is None or not self.hilo.is_alive() or self._stop.is_set()):
            self._stop.set();self._stop=threading.Event()
            self.hilo=threading.Thread(target=self._vigilar,args=(self._stop,),daemon=True);self.hilo.start()

    def cerrar(self):self._stop.set()

    def _pregame(self):
        sujeto=self.cliente.jugador;d=self.cliente.pedir('GET',f'/pregame/v1/players/{sujeto}')
        if d is None:return None
        if not isinstance(d,dict) or d.get('Subject')!=sujeto or not uuid(d.get('MatchID')):raise ErrorValorant()
        return d['MatchID']

    def _sala(self):
        sujeto=self.cliente.jugador;d=self.cliente.pedir('GET',f'/parties/v1/players/{sujeto}')
        if not isinstance(d,dict) or d.get('Subject')!=sujeto or not uuid(d.get('CurrentPartyID')):raise ErrorValorant()
        sala=self.cliente.pedir('GET','/parties/v1/parties/'+d['CurrentPartyID'])
        if not isinstance(sala,dict) or sala.get('ID')!=d['CurrentPartyID']:raise ErrorValorant()
        return sala

    def consultar(self):
        with self._lock:
            if self._pregame():self.cola_estado=MENSAJES['seleccion'];return
            sala=self._sala();estado=sala.get('State')
            if estado=='MATCHMAKING':self.cola_estado=MENSAJES['buscando']
            elif estado in ('MATCHMADE','CLOSED'):self.cola_estado=MENSAJES['partida']
            elif self._ultimo_estado=='MATCHMAKING':self.cola_estado=MENSAJES['pausa']
            else:self.cola_estado=MENSAJES['sala']
            self._ultimo_estado=estado

    def ejecutar(self,accion,valor='',cancelar=None):
        cancelar=cancelar or threading.Event()
        if accion not in ('valorant_buscar','valorant_cancelar','valorant_elegir'):raise ValueError('Acción no permitida.')
        if accion=='valorant_elegir':return self.revisar(cancelar,manual=True)
        with self._lock:
            try:
                sujeto=self.cliente.jugador
                if cancelar.is_set():return MENSAJES['sin_cola']
                if self._pregame() or self.cliente.pedir('GET',f'/core-game/v1/players/{sujeto}') is not None:return MENSAJES['partida']
                sala=self._sala();estado=sala.get('State');identificador=sala['ID']
                if accion=='valorant_cancelar' and estado!='MATCHMAKING':return MENSAJES['sin_cola']
                if accion=='valorant_buscar' and estado=='MATCHMAKING':return MENSAJES['buscando']
                if estado not in ('DEFAULT','MATCHMAKING'):return MENSAJES['sala']
                propio=next((m for m in sala.get('Members',[]) if m.get('Subject')==sujeto),{})
                if propio.get('IsOwner') is not True:return MENSAJES['lider']
                if accion=='valorant_buscar' and (sala.get('RestrictedSeconds',0)>0 or sala.get('QueueIneligibilities')):return MENSAJES['penalizacion']
                if cancelar.is_set():return MENSAJES['sin_cola']
                nueva=self._sala()
                if nueva.get('ID')!=identificador or nueva.get('State')!=estado:return MENSAJES['sala']
                lider=next((m for m in nueva.get('Members',[]) if m.get('Subject')==sujeto),{})
                if lider.get('IsOwner') is not True:return MENSAJES['lider']
                if accion=='valorant_buscar' and (nueva.get('RestrictedSeconds',0)>0 or nueva.get('QueueIneligibilities')):return MENSAJES['penalizacion']
                if cancelar.is_set():return MENSAJES['sin_cola']
                self.cliente.pedir('POST',f'/parties/v1/parties/{identificador}/matchmaking/'+('join' if accion=='valorant_buscar' else 'leave'))
                confirmado=self._sala().get('State')=='MATCHMAKING'
                clave=('buscando' if confirmado else 'solicitud') if accion=='valorant_buscar' else ('cancelando' if confirmado else 'cancelada')
                self.cola_estado=MENSAJES[clave];return self.cola_estado
            except ErrorValorant as e:return MENSAJES.get(e.clave,MENSAJES['conexion'])

    def revisar(self,cancelar=None,manual=False):
        cancelar=cancelar or threading.Event()
        with self._lock:
            cfg=copy.deepcopy(self.config)
            if cancelar.is_set() or (not manual and not cfg['auto_pick']):return self.estado
            try:
                match=self._pregame();sujeto=self.cliente.jugador
                if not match:
                    self._partida=None;self._pendiente=None;self._preparacion=None
                    self.estado=MENSAJES['esperando'];return self.estado
                ruta='/pregame/v1/matches/'+match
                partida=self.cliente.pedir('GET',ruta);local=jugador_local(partida,sujeto)
                if partida.get('ID')!=match or partida.get('PregameState')!='character_select_active' or not local:
                    self._preparacion=None;self.estado=MENSAJES['esperando'];return self.estado
                if local.get('CharacterSelectionState')=='locked':
                    self.estado=MENSAJES['confirmado' if match in self._confirmados else 'manual'];return self.estado
                actual=local.get('CharacterID','').lower()
                if actual and actual!='00000000-0000-0000-0000-000000000000' and self._pendiente!=(match,actual):
                    self.estado=MENSAJES['manual'];return self.estado
                self._partida=match
                if not self._seleccion_preparada(match,partida,local):
                    self.estado=MENSAJES['esperando'];return self.estado
                disponibles=propios(self.cliente.pedir('GET',f'/store/v1/entitlements/{sujeto}/{AGENTES}'),self._base)
                candidatos=[v for v in cfg['preferencias'] if (match,v) not in self._intentados]
                elegido=candidato(partida,candidatos,sujeto,disponibles)
                if not elegido:self.estado=MENSAJES['sin_opciones'];return self.estado
                nueva=self.cliente.pedir('GET',ruta);nuevo_local=jugador_local(nueva,sujeto)
                if (cancelar.is_set() or cfg!=self.config or self.cliente.jugador!=sujeto or self._pregame()!=match
                    or nueva.get('PregameState')!='character_select_active' or nuevo_local!=local
                    or not self._seleccion_preparada(match,nueva,nuevo_local)
                    or candidato(nueva,candidatos,sujeto,disponibles)!=elegido):return self.estado
                self._intentados.add((match,elegido));self.estado=MENSAJES['enviado'];self._pendiente=(match,elegido)
                self.cliente.pedir('POST',ruta+'/select/'+elegido)
                ultima=self.cliente.pedir('GET',ruta);yo=jugador_local(ultima,sujeto)
                if (cancelar.is_set() or cfg!=self.config or self.cliente.jugador!=sujeto or self._pregame()!=match
                    or ultima.get('PregameState')!='character_select_active' or not yo
                    or not self._seleccion_preparada(match,ultima,yo)
                    or yo.get('CharacterID','').lower()!=elegido or yo.get('CharacterSelectionState')!='selected'
                    or candidato(ultima,[elegido],sujeto,disponibles)!=elegido):return self.estado
                self.cliente.pedir('POST',ruta+'/lock/'+elegido)
                fin=self.cliente.pedir('GET',ruta);yo=jugador_local(fin,sujeto)
                if cancelar.is_set() or cfg!=self.config:return self.estado
                if yo and yo.get('CharacterID','').lower()==elegido and yo.get('CharacterSelectionState')=='locked':
                    self._confirmados.add(match);self.estado=MENSAJES['confirmado']
                return self.estado
            except ErrorValorant as e:
                if not cancelar.is_set():self.estado=MENSAJES.get(e.clave,MENSAJES['conexion'])
                return self.estado

    def _vigilar(self,stop):
        while not stop.is_set():
            try:self.revisar(stop)
            except (ValueError,TypeError,KeyError,AttributeError):
                if not stop.is_set():self.estado=MENSAJES['conexion']
            error=self.estado in (MENSAJES[k] for k in ('cliente','conexion','sesion','region','version','rechazo'))
            rapido=self._partida and self.estado not in (MENSAJES['confirmado'],MENSAJES['manual'],MENSAJES['sin_opciones'])
            stop.wait(2 if error else .25 if rapido else .75)
