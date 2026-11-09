"""Rotaciones públicas de Fortnite. Sin cuenta Epic, entradas al juego ni compras."""
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
from html.parser import HTMLParser
import hashlib,json,os,threading,time
from pathlib import Path
import urllib.request
from urllib.parse import urlsplit

UTC=timezone.utc
TIENDA='https://fortnite-api.com/v2/shop?language=es'
MISIONES='https://vbucksdaily.com/'


def normalizar(c):
    c=c if isinstance(c,dict) else {}
    return {k:c.get(k) is True for k in ('tienda','pavos','fundador')}


class ErrorDatos(ValueError):pass


def instante(s):
    try:
        d=datetime.fromisoformat(s.replace('Z','+00:00'))
        if d.tzinfo is None:raise ValueError()
        return d.astimezone(UTC)
    except (ValueError,TypeError,AttributeError):raise ErrorDatos('Fecha pública no válida') from None


def entero(v,minimo,maximo):return type(v) is int and minimo<=v<=maximo


def texto_corto(v):
    if not isinstance(v,str) or not 1<=len(v)<=120 or any(ord(c)<32 for c in v):raise ErrorDatos('Campo público no válido')
    return v


def rotacion(fecha,ahora):
    inicio=instante(fecha);fin=inicio+timedelta(days=1)
    if inicio.time()!=datetime.min.time() or not inicio<=ahora<fin:raise ErrorDatos('Rotación pendiente o caducada')
    return inicio.date().isoformat(),fin.timestamp()


def leer_tienda(d,ahora):
    if not isinstance(d,dict) or d.get('status')!=200 or not isinstance(d.get('data'),dict):raise ErrorDatos('Tienda no disponible')
    d=d['data'];dia,vence=rotacion(d.get('date'),ahora)
    if not isinstance(d.get('entries'),list) or not d['entries'] or not isinstance(d.get('hash'),str):raise ErrorDatos('Tienda incompleta')
    return {'rotacion':dia,'vence':vence,'cantidad':len(d['entries'])}


class Bootstrap(HTMLParser):
    def __init__(self):super().__init__();self.dentro=False;self.partes=[];self.encontrados=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('id')=='mission-bootstrap' and a.get('type')=='application/json':
            self.dentro=True;self.encontrados+=1
    def handle_data(self,data):
        if self.dentro:self.partes.append(data)
    def handle_endtag(self,tag):
        if tag=='script':self.dentro=False


def leer_misiones(html,ahora):
    p=Bootstrap();p.feed(html)
    try:d=json.loads(''.join(p.partes))
    except (ValueError,TypeError):raise ErrorDatos('Misiones no disponibles') from None
    if p.encontrados!=1 or not isinstance(d,dict) or d.get('status')!='current':raise ErrorDatos('Misiones no actualizadas')
    s=d.get('snapshot')
    if not isinstance(s,dict) or s.get('mode')!='live' or s.get('complete') is not True or not isinstance(s.get('coverage'),list) or 'vbucks' not in s['coverage']:raise ErrorDatos('Misiones incompletas')
    dia,vence=rotacion(s.get('effectiveAt'),ahora)
    if s.get('rotationId')!=dia or instante(s.get('expiresAt')).timestamp()!=vence:raise ErrorDatos('Rotación de misiones no válida')
    filas=s.get('missions');total=s.get('vbucksHistory',{}).get('today',{}).get('total')
    if not isinstance(filas,list) or not entero(total,0,10000):raise ErrorDatos('Resumen de misiones incompleto')
    misiones={}
    for fila in filas:
        if not isinstance(fila,dict):raise ErrorDatos('Misión incompleta')
        if fila.get('category')!='vbucks':continue
        ident=texto_corto(fila.get('missionId'));cantidad=fila.get('quantity');nivel=fila.get('pl')
        if not entero(cantidad,1,1000) or not entero(nivel,1,300):raise ErrorDatos('Recompensa no válida')
        m={'id':ident,'pavos':cantidad,'nivel':nivel,'zona':texto_corto(fila.get('zone')),'tipo':texto_corto(fila.get('type'))}
        if ident in misiones and misiones[ident]!=m:raise ErrorDatos('Recompensas contradictorias')
        misiones[ident]=m
    misiones=sorted(misiones.values(),key=lambda m:(m['nivel'],m['id']))
    if sum(m['pavos'] for m in misiones)!=total:raise ErrorDatos('Total de pavos sin confirmar')
    huella=hashlib.sha256(json.dumps(misiones,sort_keys=True).encode()).hexdigest()[:20]
    return {'rotacion':dia,'vence':vence,'misiones':misiones,'total':total,'huella':huella}


class Redirecciones(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        origen=urlsplit(req.full_url);destino=urlsplit(newurl)
        if destino.scheme!='https' or destino.netloc!=origen.netloc:raise ErrorDatos('Redirección del proveedor no admitida')
        return super().redirect_request(req,fp,code,msg,headers,newurl)


class FuentesAvisos:
    def obtener(self,tipo,ahora):
        url=TIENDA if tipo=='tienda' else MISIONES
        solicitud=urllib.request.Request(url,headers={'User-Agent':'Capri/1.0 (public rotation notifications)','Accept':'application/json' if tipo=='tienda' else 'text/html'})
        with urllib.request.build_opener(Redirecciones()).open(solicitud,timeout=10) as r:
            datos=r.read(3_000_001)
        if len(datos)>3_000_000:raise ErrorDatos('Respuesta pública demasiado grande')
        texto=datos.decode('utf8')
        return leer_tienda(json.loads(texto),ahora) if tipo=='tienda' else leer_misiones(texto,ahora)


@dataclass(frozen=True)
class Aviso:
    tipo:str
    clave:str
    datos:dict
    version:int


class MonitorFortnite:
    def __init__(self,ruta,fuentes=None,reloj=time.time):
        self.ruta=Path(ruta)/'cache/fortnite/avisos.json';self.fuentes=fuentes or FuentesAvisos();self.reloj=reloj
        self.lock=threading.RLock();self.stop=threading.Event();self.hilo=None;self.consultando=False
        self.config=normalizar({});self.version=0;self.proxima=0;self.ultima_consulta=-1e10
        self.datos={};self.errores={};self.pendientes={};self.memoria={};self.actualizado=None
        try:
            if self.ruta.stat().st_size<=16384:
                d=json.loads(self.ruta.read_text(encoding='utf8'))
                if isinstance(d,dict):
                    self.memoria={k:v for k,v in d.items() if k in ('tienda_base','tienda','pavos') and isinstance(v,str) and len(v)<=100}
        except (OSError,ValueError):pass

    def _persistir(self):
        try:
            self.ruta.parent.mkdir(parents=True,exist_ok=True);tmp=self.ruta.with_suffix('.tmp')
            tmp.write_text(json.dumps(self.memoria),encoding='utf8');os.replace(tmp,self.ruta)
        except OSError:pass

    def configurar(self,c,iniciar=True):
        with self.lock:
            self.config=normalizar(c);self.version+=1;self.pendientes.clear();self.proxima=0
            activo=self.config['tienda'] or self.config['pavos'] and self.config['fundador']
            if iniciar and activo and (self.hilo is None or not self.hilo.is_alive()):
                self.hilo=threading.Thread(target=self._vigilar,daemon=True,name='Capri-avisos-Fortnite');self.hilo.start()

    def _vigilar(self):
        while not self.stop.wait(1):
            with self.lock:activo=self.config['tienda'] or self.config['pavos'] and self.config['fundador']
            if activo and self.reloj()>=self.proxima:self.actualizar()

    def actualizar(self):
        with self.lock:
            if self.stop.is_set() or self.consultando or self.reloj()-self.ultima_consulta<30:return False
            self.consultando=True;self.ultima_consulta=self.reloj()
            threading.Thread(target=self._consultar,daemon=True,name='Capri-datos-Fortnite').start();return True

    def _consultar(self):
        with self.lock:c=dict(self.config);version=self.version
        tipos=['tienda'] if c['tienda'] else []
        if c['pavos'] and c['fundador']:tipos.append('pavos')
        # El botón permite revisar las fuentes antes de habilitar avisos.
        if not tipos:tipos=['tienda','pavos']
        fallos=False
        try:
            for tipo in tipos:
                if self.stop.is_set():break
                try:
                    d=self.fuentes.obtener(tipo,datetime.fromtimestamp(self.reloj(),UTC))
                    with self.lock:
                        if version!=self.version or self.stop.is_set():continue
                        self.errores.pop(tipo,None);self.datos[tipo]=d;self._preparar(tipo,d,version)
                except Exception:
                    fallos=True
                    with self.lock:
                        if version==self.version:self.errores[tipo]=True;self.pendientes.pop(tipo,None)
            with self.lock:
                self.actualizado=self.reloj();self.proxima=self.reloj()+(60 if fallos else 300) if version==self.version else 0
        finally:
            with self.lock:self.consultando=False

    def _preparar(self,tipo,d,version):
        if tipo=='tienda':
            anterior=self.memoria.get('tienda_base')
            if anterior is None:
                self.memoria['tienda_base']=d['rotacion'];self._persistir();return
            clave=d['rotacion']
            if not self.config['tienda'] or clave<=anterior or self.memoria.get('tienda')==clave:return
        else:
            clave=d['rotacion']+':'+d['huella']
            if not self.config['pavos'] or not self.config['fundador'] or not d['total'] or self.memoria.get('pavos')==clave:
                self.pendientes.pop(tipo,None);return
        self.pendientes[tipo]=Aviso(tipo,clave,d,version)

    def siguiente(self):
        with self.lock:
            for tipo,p in list(self.pendientes.items()):
                if p.version!=self.version or p.datos['vence']<=self.reloj():self.pendientes.pop(tipo,None);continue
                return p
        return None

    def confirmar(self,p):
        with self.lock:
            if self.stop.is_set() or self.pendientes.get(p.tipo) is not p or p.version!=self.version or p.datos['vence']<=self.reloj():return False
            if not self.config[p.tipo] or p.tipo=='pavos' and not self.config['fundador']:return False
            self.pendientes.pop(p.tipo);self.memoria[p.tipo]=p.clave
            if p.tipo=='tienda':self.memoria['tienda_base']=p.datos['rotacion']
            self._persistir();return True

    def copia(self):
        with self.lock:
            return {'datos':dict(self.datos),'errores':dict(self.errores),'consultando':self.consultando,'actualizado':self.actualizado}

    def cerrar(self):
        self.stop.set()
        with self.lock:self.version+=1;self.pendientes.clear()


def mensaje(aviso,idioma='es'):
    from idiomas import ui
    if aviso.tipo=='tienda':return ui('La tienda de Fortnite acaba de cambiar. Ya puedes revisar la nueva rotación.',idioma)
    d=aviso.datos
    return ui('Hay misiones de Salvar el Mundo con {0} pavos en total para fundadores. Revisa las zonas y los niveles en Ajustes → Juegos → Fortnite → Avisos; tienes hasta {1}.',idioma).format(d['total'],datetime.fromtimestamp(d['vence']).astimezone().strftime('%d/%m %H:%M'))
