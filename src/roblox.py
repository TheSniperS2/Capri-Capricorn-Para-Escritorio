"""Preferencias locales y lecturas públicas de Roblox. No accede a sesiones ni credenciales."""
import hashlib
import io
import json
import math
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

PERFILES=('clasica','terror','aventura','estilo','discreta')
EVENTOS=('victoria','derrota','muerte')

class ErrorRoblox(Exception):pass

def clave(t):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(t).casefold()) if unicodedata.category(c)!='Mn').split()).strip(' .!?¿¡…')

def texto(t,limite=160):
    return ' '.join(str(t).split())[:limite] if isinstance(t,str) else ''

def enlace(valor):
    """Solo páginas/compartidos oficiales. No ejecuta protocolos ni argumentos del usuario."""
    valor=str(valor).strip()
    if re.fullmatch(r'[1-9]\d{0,18}',valor):return 'https://www.roblox.com/games/'+valor
    try:
        u=urllib.parse.urlsplit(valor);puerto=u.port
    except ValueError:raise ErrorRoblox('Usa un enlace oficial de Roblox o un ID de experiencia.')
    if u.scheme!='https' or u.hostname not in ('roblox.com','www.roblox.com') or u.username or u.password or puerto not in (None,443) or u.fragment:
        raise ErrorRoblox('Usa un enlace oficial de Roblox o un ID de experiencia.')
    m=re.fullmatch(r'/games/([1-9]\d{0,18})(?:/[\w-]+)?/?',u.path)
    if m and not u.query:return 'https://www.roblox.com/games/'+m[1]
    if u.path.rstrip('/')=='/share':
        try:q=urllib.parse.parse_qs(u.query,strict_parsing=True)
        except ValueError:raise ErrorRoblox('Usa un enlace oficial de Roblox o un ID de experiencia.')
        if set(q)=={'code','type'} and all(len(v)==1 for v in q.values()) and re.fullmatch(r'[A-Za-z0-9_-]{8,200}',q['code'][0]) and q['type'][0] in ('ExperienceDetails','Server'):
            return 'https://www.roblox.com/share?'+urllib.parse.urlencode({'code':q['code'][0],'type':q['type'][0]})
    # Enlaces privados antiguos: conservar el código, sin registrar ni expandirlo.
    if m:
        q=urllib.parse.parse_qs(u.query)
        if set(q)=={'privateServerLinkCode'} and len(q['privateServerLinkCode'])==1 and re.fullmatch(r'[A-Za-z0-9_-]{8,200}',q['privateServerLinkCode'][0]):
            return 'https://www.roblox.com/games/'+m[1]+'?'+urllib.parse.urlencode({'privateServerLinkCode':q['privateServerLinkCode'][0]})
    raise ErrorRoblox('Usa un enlace oficial de Roblox o un ID de experiencia.')

def reglas_eventos(d):
    d=d if isinstance(d,dict) else {}
    return {'activo':d.get('activo') is True,**{k:'|'.join([texto(p,45) for p in str(d.get(k,'')).split('|') if texto(p,45)][:8]) for k in EVENTOS}}

def normalizar(d):
    d=d if isinstance(d,dict) else {};favoritos=[];vistos=set();nombres=set()
    for f in (d.get('favoritos') if isinstance(d.get('favoritos'),list) else [])[:40]:
        if not isinstance(f,dict):continue
        try:url=enlace(f.get('url',''))
        except (ErrorRoblox,ValueError):continue
        nombre=texto(f.get('nombre'),55);identidad=hashlib.sha256(url.encode()).hexdigest()[:20]
        if not nombre or identidad in vistos or clave(nombre) in nombres:continue
        vistos.add(identidad);nombres.add(clave(nombre))
        favoritos.append({'id':identidad,'nombre':nombre,'url':url,'perfil':f.get('perfil') if f.get('perfil') in PERFILES else 'clasica',
                          'modo_perfil':'manual' if f.get('modo_perfil')=='manual' else 'auto','eventos':reglas_eventos(f.get('eventos'))})
    notas={k:v[:4000] for k,v in (d.get('notas') if isinstance(d.get('notas'),dict) else {}).items()
           if re.fullmatch('[a-f0-9]{20}',str(k)) and isinstance(v,str)}
    notas=dict(list(notas.items())[:80]);recordatorios=[];ids=set()
    for r in (d.get('recordatorios') if isinstance(d.get('recordatorios'),list) else [])[:30]:
        if not isinstance(r,dict):continue
        identificador=r.get('id');vence=r.get('vence');mensaje=texto(r.get('texto'))
        if not isinstance(identificador,str) or not re.fullmatch('[a-f0-9]{20,32}',identificador) or identificador in ids:continue
        if type(vence) not in (int,float) or not math.isfinite(vence) or not 0<vence<4102444800 or not mensaje:continue
        ids.add(identificador);recordatorios.append({'id':identificador,'vence':vence,'texto':mensaje,'juego':texto(r.get('juego'),55)})
    usuario=texto(d.get('usuario'),25)
    if usuario and not (re.fullmatch('[A-Za-z0-9_]{3,20}',usuario) or re.fullmatch('[1-9][0-9]{0,18}',usuario)):usuario=''
    return {'favoritos':favoritos,'seleccion':d.get('seleccion') if d.get('seleccion') in vistos else (favoritos[0]['id'] if favoritos else ''),
            'notas':notas,'recordatorios':recordatorios,'usuario':usuario,'avatar_auto':d.get('avatar_auto') is True,'acompanar':d.get('acompanar') is True}

def seleccionado(d):
    d=normalizar(d)
    return next((f for f in d['favoritos'] if f['id']==d['seleccion']),None)

def agregar_favorito(d,nombre,url):
    d=normalizar(d);nombre=texto(nombre,55);url=enlace(url)
    if not nombre:
        lugar=re.search(r'/games/(\d+)',url)
        nombre='Experiencia '+lugar[1] if lugar else 'Experiencia '+hashlib.sha256(url.encode()).hexdigest()[:6]
    identidad=hashlib.sha256(url.encode()).hexdigest()[:20]
    if any(clave(f['nombre'])==clave(nombre) and f['id']!=identidad for f in d['favoritos']):raise ErrorRoblox('Ya hay un favorito con ese nombre.')
    anterior=next((f for f in d['favoritos'] if f['id']==identidad),{})
    if not anterior and len(d['favoritos'])>=40:raise ErrorRoblox('Puedes guardar hasta 40 favoritos de Roblox.')
    nuevo={'id':identidad,'nombre':nombre,'url':url,'perfil':anterior.get('perfil','clasica'),'modo_perfil':anterior.get('modo_perfil','auto'),'eventos':anterior.get('eventos',{})}
    d['favoritos']=[f for f in d['favoritos'] if f['id']!=identidad]+[nuevo];d['seleccion']=identidad
    return normalizar(d)

def recordar(d,mensaje,minutos,ahora=None):
    import uuid
    d=normalizar(d)
    if len(d['recordatorios'])>=30:raise ErrorRoblox('Puedes guardar hasta 30 recordatorios de Roblox.')
    if type(minutos) not in (int,float) or not math.isfinite(minutos) or not 1<=minutos<=10080:raise ErrorRoblox('Elige entre 1 y 10080 minutos.')
    mensaje=texto(mensaje)
    if not mensaje:raise ErrorRoblox('Escribe el texto del recordatorio.')
    f=seleccionado(d)
    d['recordatorios'].append({'id':uuid.uuid4().hex,'texto':mensaje,'vence':(time.time() if ahora is None else ahora)+minutos*60,'juego':f['nombre'] if f else 'Roblox'})
    return normalizar(d)

def interpretar_roblox(t):
    t=re.sub(r'^(?:oye\s+)?capri[, :]*','',str(t).strip(),flags=re.I).strip(' .!¿?¡')
    n=clave(t)
    if t.startswith(('"','«','“',"'")) or re.match(r'^(?:no|nunca|si digo|dije|como|explica)\b',n):return None
    if re.fullmatch(r'(?:abre|abrir|configura|muestra)(?: el)? (?:panel de |mis favoritos de )?roblox|(?:mis favoritos|configuracion) de roblox',n):return ('roblox_panel','')
    if n in ('open roblox panel','configure roblox','abrir painel do roblox','configurar roblox','robloxの設定を開いて'):return ('roblox_panel','')
    if n in ('look at my avatar in roblox','what do you think of my roblox avatar','olhe meu avatar no roblox','robloxのアバターを見て'):return ('roblox_avatar','')
    if re.fullmatch(r'(?:mira|opina sobre|analiza)(?: mi)? (?:avatar|outfit)(?: en| de)? roblox|que te parece mi (?:avatar|outfit)(?: en| de)? roblox',n):return ('roblox_avatar','')
    if re.fullmatch(r'(?:lee|recuerda|muestra)(?:me)? (?:mi |la )?(?:nota|objetivo)(?: en| de) roblox',n):return ('roblox_nota_leer','')
    m=re.fullmatch(r'(?:anota|guarda una nota) (?:en|de) roblox\s*:?\s+(.+)',t,re.I)
    if not m:m=re.fullmatch(r'(?:save a note in|anote no) roblox\s*:?\s+(.+)',t,re.I)
    if m:return ('roblox_nota_guardar',m[1][:4000])
    m=re.fullmatch(r'(?:modo|perfil) (clasica|terror|aventura|estilo|discreta) (?:en|de) roblox',n)
    if m:return ('roblox_perfil',m[1])
    m=re.fullmatch(r'recu[eé]rdame en (\d{1,5}) minutos? (.+?) en roblox',t,re.I)
    if m:return ('roblox_recordar',json.dumps({'minutos':int(m[1]),'texto':m[2]},ensure_ascii=False))
    if n in ('cancela mis recordatorios de roblox','cancela los recordatorios de roblox'):return ('roblox_cancelar_recordatorios','')
    for prefijo,evento in (('gane','victoria'),('ganamos','victoria'),('perdi','derrota'),('perdimos','derrota'),('me mori','muerte')):
        if n==prefijo+' en roblox':return ('roblox_evento',evento)
    if n in ('cuanto llevo en roblox','cuanto llevo jugando roblox'):return ('roblox_tiempo','')
    m=re.fullmatch(r'(?:abre|abrir|juega|inicia) (.+?) en roblox',t,re.I)
    if not m:m=re.fullmatch(r'(?:open|play|abra|jogue) (.+?) (?:in|on|no) roblox',t,re.I)
    if m and len(m[1])<=55 and not re.search(r'\b(?:y abre|y busca|y juega|despues|luego)\b',clave(m[1])):return ('roblox_abrir',m[1])
    return None

def preparar_local(d,tipo,valor,idioma='es'):
    """Cambios explícitos aplicados en el hilo principal antes del trabajo de red."""
    from idiomas import ui
    from roblox_dialogos import PERFILES,elegir,reaccion
    d=normalizar(d);f=seleccionado(d)
    if tipo=='roblox_abrir':
        f=next((x for x in d['favoritos'] if clave(x['nombre'])==clave(valor)),None)
        if not f:raise ErrorRoblox('No encontré ese favorito en el panel de Roblox.')
        d['seleccion']=f['id'];return d,None
    if tipo in ('roblox_nota_leer','roblox_nota_guardar','roblox_perfil') and not f:raise ErrorRoblox('Selecciona un favorito.')
    if tipo=='roblox_nota_guardar':
        d['notas'][f['id']]=str(valor)[:4000];return d,ui('Nota guardada para {0}.',idioma).format(f['nombre'])
    if tipo=='roblox_nota_leer':
        nota=d['notas'].get(f['id'],'')
        return d,ui('Tu nota para {0}: {1}',idioma).format(f['nombre'],nota) if nota else ui('Todavía no tienes una nota para {0}.',idioma).format(f['nombre'])
    if tipo=='roblox_perfil':
        if valor not in PERFILES:raise ErrorRoblox('Selecciona un favorito.')
        d['favoritos']=[{**x,'perfil':valor,'modo_perfil':'manual'} if x['id']==f['id'] else x for x in d['favoritos']]
        return d,ui('Perfil de Capri: {0}.',idioma).format(elegir(PERFILES[valor],idioma))
    if tipo=='roblox_evento':
        if valor not in EVENTOS:raise ErrorRoblox('Selecciona un favorito.')
        return d,reaccion(valor,f['perfil'] if f else 'clasica',idioma)
    if tipo=='roblox_recordar':
        datos=json.loads(valor);d=recordar(d,datos['texto'],datos['minutos'])
        return d,ui('Recordatorio para {0} en {1} minutos.',idioma).format(f['nombre'] if f else 'Roblox',datos['minutos'])
    if tipo=='roblox_cancelar_recordatorios':
        d['recordatorios']=[];return d,ui('Cancelé tus recordatorios de Roblox.',idioma)
    return d,None

class SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):raise ErrorRoblox('Roblox devolvió una redirección inesperada.')

class ClientePublico:
    def __init__(self,cache=None):
        from roblox_cache import CacheRoblox
        self.opener=urllib.request.build_opener(SinRedireccion());self.ids={};self.experiencias={};self.iconos={}
        self.cache=CacheRoblox(cache) if cache is not None else None
    def json(self,url,datos=None):
        u=urllib.parse.urlsplit(url)
        if u.scheme!='https' or u.hostname not in ('users.roblox.com','avatar.roblox.com','thumbnails.roblox.com','apis.roblox.com','games.roblox.com') or u.username or u.password or u.port not in (None,443):raise ErrorRoblox('Dirección de Roblox no admitida.')
        req=urllib.request.Request(url,data=json.dumps(datos).encode() if datos is not None else None,headers={'Content-Type':'application/json','User-Agent':'CapriDesktop/1.0'})
        try:
            with self.opener.open(req,timeout=8) as r:b=r.read(2000001)
            if len(b)>2000000:raise ErrorRoblox('La respuesta de Roblox es demasiado grande.')
            d=json.loads(b)
            if not isinstance(d,dict):raise ValueError('Objeto esperado')
            return d
        except (OSError,ValueError,urllib.error.URLError) as e:raise ErrorRoblox('No pude consultar Roblox. Inténtalo de nuevo en un momento.') from e
    def avatar(self,usuario):
        if not usuario:raise ErrorRoblox('Configura tu usuario de Roblox en el panel.')
        if re.fullmatch('[1-9][0-9]{0,18}',usuario):uid=usuario
        else:
            uid=self.ids.get(usuario.casefold())
            if not uid:
                d=self.json('https://users.roblox.com/v1/usernames/users',{'usernames':[usuario],'excludeBannedUsers':True})
                filas=d.get('data',[])
                if not isinstance(filas,list) or len(filas)!=1 or not isinstance(filas[0],dict) or type(filas[0].get('id')) is not int or filas[0]['id']<1:raise ErrorRoblox('No encontré ese usuario. Usa su nombre de usuario, no el nombre visible.')
                uid=str(filas[0]['id']);self.ids[usuario.casefold()]=uid
        datos=self.json('https://avatar.roblox.com/v1/users/'+uid+'/avatar')
        if not isinstance(datos,dict) or not isinstance(datos.get('assets'),list) or not datos['assets']:raise ErrorRoblox('No pude leer el avatar público de esa cuenta.')
        piezas=[{'id':a['id'],'nombre':texto(a.get('name'),80),'tipo':texto((a.get('assetType') if isinstance(a.get('assetType'),dict) else {}).get('name'),40),
                 'tipo_id':(a.get('assetType') if isinstance(a.get('assetType'),dict) else {}).get('id')}
                for a in datos['assets'][:100] if isinstance(a,dict) and type(a.get('id')) is int and a['id']>0]
        if not piezas:raise ErrorRoblox('No pude leer el avatar público de esa cuenta.')
        # Preferencias basadas en las prendas/accesorios, no en rasgos corporales.
        cuerpo={'head','dynamichead','leftarm','rightarm','leftleg','rightleg','torso','face'}
        ropa=sorted(a['id'] for a in piezas if 'animation' not in a['tipo'].casefold() and a['tipo'].casefold() not in cuerpo)
        fp=hashlib.sha256(json.dumps(ropa or sorted(a['id'] for a in piezas)).encode()).hexdigest()
        return {'usuario':usuario,'user_id':uid,'piezas':piezas,'huella':fp,'gusto':int(fp[:8],16)%3}
    def miniatura(self,uid):
        d=self.json('https://thumbnails.roblox.com/v1/users/avatar?'+urllib.parse.urlencode({'userIds':uid,'size':'150x150','format':'Png','isCircular':'false'}))
        return self._imagen_miniatura(d,uid)
    def _imagen_miniatura(self,d,uid):
        opciones=d.get('data',[])
        if not isinstance(opciones,list):return None
        url=next((a.get('imageUrl','') for a in opciones if isinstance(a,dict) and str(a.get('targetId'))==str(uid) and a.get('state')=='Completed'),'')
        if not isinstance(url,str):return None
        try:
            u=urllib.parse.urlsplit(url)
            if u.scheme!='https' or not u.hostname or not (u.hostname=='rbxcdn.com' or u.hostname.endswith('.rbxcdn.com')) or u.username or u.password or u.port not in (None,443):return None
        except ValueError:return None
        with self.opener.open(urllib.request.Request(url,headers={'User-Agent':'CapriDesktop/1.0'}),timeout=4) as r:b=r.read(2000001)
        if len(b)>2000000:return None
        from PIL import Image
        with Image.open(io.BytesIO(b)) as im:
            if im.width>2048 or im.height>2048:return None
            return im.convert('RGB').copy()

    def detalles_guardados(self,lugar):
        lugar=str(lugar);previo=self.experiencias.get(lugar)
        if not previo and self.cache:
            guardado=self.cache.leer_info(lugar)
            if guardado:
                fecha,info=guardado;previo=(time.monotonic()-max(0,time.time()-fecha),info);self.experiencias[lugar]=previo
        return dict(previo[1]) if previo else None
    def detalles_lugar(self,lugar,forzar=False):
        lugar=str(lugar)
        if not re.fullmatch('[1-9][0-9]{0,18}',lugar):raise ErrorRoblox('Usa un enlace oficial de Roblox o un ID de experiencia.')
        guardado=self.detalles_guardados(lugar);previo=self.experiencias.get(lugar)
        if previo and not forzar and time.monotonic()-previo[0]<1800:return guardado
        try:info=self._consultar_lugar(lugar)
        except (ErrorRoblox,OSError):
            if guardado and not forzar:return guardado
            raise
        self.experiencias[lugar]=(time.monotonic(),info)
        if self.cache:self.cache.guardar_info(info)
        return dict(info)
    def _consultar_lugar(self,lugar):
        d=self.json('https://apis.roblox.com/universes/v1/places/'+lugar+'/universe');universo=d.get('universeId')
        if type(universo) is not int or universo<1:raise ErrorRoblox('No pude leer la información de esta experiencia.')
        d=self.json('https://games.roblox.com/v1/games?'+urllib.parse.urlencode({'universeIds':universo}))
        filas=d.get('data')
        if not isinstance(filas,list) or not filas or not isinstance(filas[0],dict) or filas[0].get('id')!=universo:raise ErrorRoblox('No pude leer la información de esta experiencia.')
        f=filas[0];creador=f.get('creator') if isinstance(f.get('creator'),dict) else {}
        info={'lugar':lugar,'universo':str(universo),'nombre':texto(f.get('name'),100),'descripcion':texto(f.get('description'),3000),
              'genero':texto(f.get('genre_l1') or f.get('genre'),80),'subgenero':texto(f.get('genre_l2'),80),
              'genero_original':texto(f.get('genre'),80),'creador':texto(creador.get('name'),80)}
        if not info['nombre']:raise ErrorRoblox('No pude leer la información de esta experiencia.')
        from roblox_info import perfil_automatico
        info['perfil']=perfil_automatico(info)
        return dict(info)

    def icono_guardado(self,universo):
        universo=str(universo);previo=self.iconos.get(universo)
        if not previo and self.cache:
            guardado=self.cache.leer_icono(universo)
            if guardado:
                fecha,im=guardado;previo=(time.monotonic()-max(0,time.time()-fecha),im);self.iconos[universo]=previo
        return previo[1].copy() if previo else None
    def icono_experiencia(self,universo,forzar=False):
        universo=str(universo)
        if not re.fullmatch('[1-9][0-9]{0,18}',universo):raise ErrorRoblox('No pude leer la información de esta experiencia.')
        guardado=self.icono_guardado(universo);previo=self.iconos.get(universo)
        if previo and not forzar and time.monotonic()-previo[0]<604800:return guardado
        # Reutiliza las mismas comprobaciones de host, tamaño y formato de miniatura.
        try:
            d=self.json('https://thumbnails.roblox.com/v1/games/icons?'+urllib.parse.urlencode({'universeIds':universo,'size':'150x150','format':'Png','isCircular':'false'}))
            im=self._imagen_miniatura(d,universo)
        except (ErrorRoblox,OSError):
            if guardado is not None:return guardado
            raise
        if im is None:return guardado
        self.iconos[universo]=(time.monotonic(),im.copy())
        if self.cache:self.cache.guardar_icono(universo,im)
        return im

class DetectorEventos:
    def __init__(self):self.candidato=None;self.cuenta=0;self.ultimo=None;self.vacio=0;self.fecha=-1000
    def observar(self,lineas,reglas,ahora):
        textos={clave(t) for t in lineas};detectados=[]
        for e in ('victoria','derrota','muerte','duda'):
            palabras={clave(p) for p in reglas.get(e,'').split('|') if clave(p)}
            if palabras & textos:detectados.append(e)
        claros=[e for e in detectados if e!='duda']
        evento=claros[0] if len(claros)==1 else ('duda' if detectados else None)
        if evento is None:
            self.candidato=None;self.cuenta=0;self.vacio+=1
            if self.vacio>=2:self.ultimo=None
            return None
        self.vacio=0;self.cuenta=self.cuenta+1 if evento==self.candidato else 1;self.candidato=evento
        if self.cuenta>=2 and evento!=self.ultimo and ahora-self.fecha>=45:
            self.ultimo=evento;self.fecha=ahora;return evento
        return None

class ControlRoblox:
    def __init__(self,eventos=lambda e:None,iniciar=True,cliente=None,cache=None):
        self.eventos=eventos;self.iniciar=iniciar;self.cliente=cliente or ClientePublico(cache);self.config=normalizar({})
        self.lock=threading.RLock();self.fin=threading.Event();self.permitido=False;self.hilo=None;self.generacion=0
        self.avatar_actual=None;self.baseline=None;self.avisado=None;self.proximo_avatar=0;self.detector=DetectorEventos();self.inicio=None
        self.estado='Roblox listo';self.proximo_ocr=0;self.informacion={};self.experiencia_actual=None;self.proximo_juego=0
    def configurar(self,d):
        nuevo=normalizar(d)
        with self.lock:
            if nuevo!=self.config:
                usuario=nuevo['usuario']!=self.config['usuario'];self.generacion+=1
                if usuario:self.avatar_actual=None;self.baseline=None;self.avisado=None;self.proximo_avatar=0
                if nuevo['seleccion']!=self.config['seleccion']:self.detector=DetectorEventos()
                self.config=nuevo
            f=seleccionado(nuevo)
            if self.iniciar and (nuevo['acompanar'] or nuevo['avatar_auto'] or f) and (self.hilo is None or not self.hilo.is_alive()):
                if not self.fin.is_set():self.hilo=threading.Thread(target=self._vigilar,daemon=True,name='Capri-Roblox');self.hilo.start()
    def copia(self):
        with self.lock:return normalizar(self.config)
    def avatar(self,cancelar=None):
        usuario=self.copia()['usuario'];a=self.cliente.avatar(usuario)
        if cancelar and cancelar.is_set():raise InterruptedError()
        if self.copia()['usuario']!=usuario:raise InterruptedError()
        with self.lock:self.avatar_actual=a
        return a
    def abrir(self,nombre,cancelar=None,abrir=None):
        d=self.copia();f=next((f for f in d['favoritos'] if clave(f['nombre'])==clave(nombre)),None)
        if not f:raise ErrorRoblox('No encontré ese favorito en el panel de Roblox.')
        if cancelar and cancelar.is_set():raise InterruptedError()
        url=enlace(f['url'])
        if abrir is None:
            import os
            abrir=os.startfile
        abrir(url);self.inicio=(f['id'],time.monotonic())
        return f
    def informacion_guardada(self,favorito):
        with self.lock:info=self.informacion.get(favorito['id'])
        if info:return dict(info)
        m=re.search(r'/games/(\d+)',enlace(favorito['url']))
        info=self.cliente.detalles_guardados(m[1]) if m else None
        if info:
            with self.lock:self.informacion[favorito['id']]=info
        return info
    def detalles(self,favorito,forzar=False):
        m=re.search(r'/games/(\d+)',enlace(favorito['url']))
        if not m:raise ErrorRoblox('Este enlace compartido no muestra el ID. Usa la dirección de la página del juego para leer su descripción.')
        info=self.cliente.detalles_lugar(m[1],forzar)
        with self.lock:self.informacion[favorito['id']]=info
        return info
    def perfil(self):
        d=self.copia();f=seleccionado(d)
        with self.lock:info=self.experiencia_actual or (self.informacion.get(f['id']) if f else None)
        if info:return info['perfil']
        return f['perfil'] if f and f['modo_perfil']=='manual' else 'clasica'
    def _vigilar(self):
        from roblox_vision import en_primer_plano,leer_centro,lugar_actual
        from roblox_info import REGLAS_AUTOMATICAS
        while not self.fin.wait(.5):
            d=self.copia();f=seleccionado(d);gen=self.generacion
            if not self.permitido or not en_primer_plano():continue
            ahora=time.monotonic()
            if (d['acompanar'] or f) and ahora>=self.proximo_juego:
                self.proximo_juego=ahora+15
                try:
                    lugar=lugar_actual() if d['acompanar'] else None
                    if lugar:
                        info=self.cliente.detalles_lugar(lugar)
                        if not self.experiencia_actual or self.experiencia_actual['lugar']!=lugar:self.detector=DetectorEventos()
                        with self.lock:self.experiencia_actual=info
                    elif f and f['id'] not in self.informacion:self.detalles(f)
                except (OSError,ErrorRoblox):pass
            if d['avatar_auto'] and d['usuario'] and ahora>=self.proximo_avatar:
                self.proximo_avatar=ahora+60
                try:
                    a=self.avatar()
                    if self.baseline is None:self.baseline=a['huella']
                    elif a['huella']!=self.baseline and a['huella']!=self.avisado:
                        self.eventos(('roblox_aviso',{'tipo':'avatar','generacion':gen,'avatar':a,'fecha':time.monotonic()}))
                    self.estado='Avatar de Roblox actualizado'
                except (ErrorRoblox,InterruptedError):self.estado='No pude actualizar el avatar de Roblox'
            if self.fin.is_set() or not self.permitido or self.copia()!=d:continue
            if (d['acompanar'] or (f and f['eventos']['activo'])) and ahora>=self.proximo_ocr:
                self.proximo_ocr=ahora+3
                try:
                    lineas=leer_centro()
                    if lineas is None:continue
                    e=self.detector.observar(lineas,REGLAS_AUTOMATICAS,ahora)
                    if e:self.eventos(('roblox_aviso',{'tipo':'evento','generacion':gen,'evento':e,'perfil':self.perfil(),'fecha':time.monotonic()}))
                    self.estado='Observando el centro de la ventana de Roblox'
                except (OSError,RuntimeError):self.estado='No pude leer la ventana de Roblox'
    def contexto(self):
        d=self.copia();f=seleccionado(d)
        with self.lock:info=self.experiencia_actual or (self.informacion.get(f['id']) if f else None)
        if not f and not info:return None
        return {'experiencia_elegida':info['nombre'] if info else f['nombre'],'perfil':self.perfil(),
                'categoria':info.get('genero','') if info else '', 'descripcion_publica':info.get('descripcion','')[:700] if info else '',
                'origen':'cliente Roblox' if self.experiencia_actual else 'favorito seleccionado'}
    def cerrar(self):self.fin.set();self.permitido=False
