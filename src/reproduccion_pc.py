"""Sesiones multimedia de Windows; un ayudante persistente mientras el panel está activo."""
import base64
import json
import math
import queue
import subprocess
import threading
import time


SCRIPT=r'''
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
[Console]::InputEncoding=New-Object Text.UTF8Encoding($false)
[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Drawing
$tipo=[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager,Windows.Media.Control,ContentType=WindowsRuntime]
$mediaTipo=[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties,Windows.Media.Control,ContentType=WindowsRuntime]
$streamTipo=[Windows.Storage.Streams.IRandomAccessStreamWithContentType,Windows.Storage.Streams,ContentType=WindowsRuntime]
$inputTipo=[Windows.Storage.Streams.IInputStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$randomTipo=[Windows.Storage.Streams.IRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$readerTipo=[Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime]
$asTask=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'} | Select-Object -First 1
function Esperar($op,[Type]$t) {
 $task=$asTask.MakeGenericMethod($t).Invoke($null,@($op))
 if(-not $task.Wait(1000)){throw 'Tiempo agotado'}
 return $task.Result
}
$gestor=Esperar ($tipo::RequestAsync()) $tipo
$artes=@{};$revisiones=@{}
function LeerPortada($referencia) {
 $stream=$null;$entrada=$null;$memoria=$null;$imagen=$null;$mini=$null;$salida=$null
 try {
  $stream=Esperar ($referencia.OpenReadAsync()) $streamTipo
  $inputStream=$randomTipo.GetMethod('GetInputStreamAt').Invoke($stream,@([uint64]0))
  $entrada=[System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead(($inputStream -as $inputTipo))
  $tamano=$randomTipo.GetProperty('Size').GetValue($stream)
  if($tamano -le 0 -or $tamano -gt 8388608){return ''}
  $memoria=New-Object IO.MemoryStream;$entrada.CopyTo($memoria);$memoria.Position=0
  $imagen=[Drawing.Image]::FromStream($memoria)
  if([long]$imagen.Width*$imagen.Height -gt 8000000){return ''}
  $factor=[Math]::Min(1.0,256.0/[Math]::Max($imagen.Width,$imagen.Height))
  $mini=New-Object Drawing.Bitmap ([int][Math]::Max(1,$imagen.Width*$factor)),([int][Math]::Max(1,$imagen.Height*$factor))
  $g=[Drawing.Graphics]::FromImage($mini)
  try {$g.DrawImage($imagen,0,0,$mini.Width,$mini.Height)} finally {$g.Dispose()}
  $salida=New-Object IO.MemoryStream;$mini.Save($salida,[Drawing.Imaging.ImageFormat]::Png)
  return [Convert]::ToBase64String($salida.ToArray())
 } catch {return ''} finally {
  foreach($obj in @($salida,$mini,$imagen,$memoria,$entrada,$stream)){
   if($obj){try {([IDisposable]$obj).Dispose()} catch {}}
  }
 }
}
while($null -ne ($linea=[Console]::ReadLine())) {
 try {
  if($linea.Length -gt 8192){throw 'Petición demasiado larga'}
  $peticion=$linea|ConvertFrom-Json
  if($peticion.accion -notin @('estado','pausa','reanudar','anterior','siguiente','posicion')){throw 'Acción inválida'}
  $candidatos=@()
  if($peticion.accion -ne 'estado') {
   $fuentes=@($gestor.GetSessions()|Where-Object {$_.SourceAppUserModelId -ceq $peticion.fuente})
   foreach($s in $fuentes) {
    try {
     $titulo=$peticion.titulo;$artista=$peticion.artista
     if($fuentes.Count -gt 1 -or $peticion.accion -eq 'posicion') {
      $m=Esperar ($s.TryGetMediaPropertiesAsync()) $mediaTipo;$titulo=[string]$m.Title;$artista=[string]$m.Artist
     }
     $c=$s.GetPlaybackInfo().Controls
     $candidatos+=,@{sesion=$s;datos=@{fuente=[string]$s.SourceAppUserModelId;titulo=$titulo;artista=$artista;
      controles=@{pausa=([bool]$c.IsPauseEnabled -or [bool]$c.IsPlayPauseToggleEnabled);
       reanudar=([bool]$c.IsPlayEnabled -or [bool]$c.IsPlayPauseToggleEnabled);
       anterior=[bool]$c.IsPreviousEnabled;siguiente=[bool]$c.IsNextEnabled;posicion=[bool]$c.IsPlaybackPositionEnabled}}}
    } catch {}
   }
  }
  $ok=$true;$codigo=''
  if($peticion.accion -ne 'estado') {
   $elegidos=@($candidatos|Where-Object {$_.datos.fuente -ceq $peticion.fuente -and $_.datos.titulo -ceq $peticion.titulo -and $_.datos.artista -ceq $peticion.artista})
   if($elegidos.Count -ne 1){$ok=$false;$codigo='cambio'}
   elseif(-not $elegidos[0].datos.controles[$peticion.accion]){$ok=$false;$codigo='no_disponible'}
   else {
    $s=$elegidos[0].sesion
    switch($peticion.accion) {
     'pausa' {$ok=Esperar ($s.TryPauseAsync()) ([bool])}
     'reanudar' {$ok=Esperar ($s.TryPlayAsync()) ([bool])}
     'anterior' {$ok=Esperar ($s.TrySkipPreviousAsync()) ([bool])}
     'siguiente' {$ok=Esperar ($s.TrySkipNextAsync()) ([bool])}
     'posicion' {
      $t=$s.GetTimelineProperties();$seg=[double]$peticion.posicion+$t.StartTime.TotalSeconds
      if([double]::IsNaN($seg) -or [double]::IsInfinity($seg) -or $seg -lt $t.MinSeekTime.TotalSeconds -or $seg -gt $t.MaxSeekTime.TotalSeconds){$ok=$false}
      else {$ok=Esperar ($s.TryChangePlaybackPositionAsync([int64][Math]::Round($seg*10000000))) ([bool])}
     }
    }
    if(-not $ok){$codigo='rechazo'}
   }
  }
  $items=@();$candidatos=@();$presupuesto=2097152;$reloj=[Diagnostics.Stopwatch]::StartNew()
  foreach($sesion in $gestor.GetSessions()) {
   $fuente=[string]$sesion.SourceAppUserModelId
   if($fuente -notmatch '(?i)(spotify|opera|chrome|msedge|firefox|brave|vivaldi)'){continue}
   if($items.Count -ge 8 -or $reloj.ElapsedMilliseconds -gt 6000){break}
   try {
    $media=Esperar ($sesion.TryGetMediaPropertiesAsync()) $mediaTipo
    $titulo=([string]$media.Title);$artista=([string]$media.Artist)
    if(-not $titulo){continue}
    $estadoNombre='Unknown';$ctrl=$null;$pos=0;$dur=0;$tasa=1
    try {
     $estado=$sesion.GetPlaybackInfo();$ctrl=$estado.Controls;$estadoNombre=$estado.PlaybackStatus.ToString()
     $tasa=[double]$estado.PlaybackRate;if($tasa -le 0 -or $tasa -gt 16){$tasa=1}
    } catch {}
    try {
     $timeline=$sesion.GetTimelineProperties()
     $pos=[double]$timeline.Position.TotalSeconds-[double]$timeline.StartTime.TotalSeconds
     $dur=[double]$timeline.EndTime.TotalSeconds-[double]$timeline.StartTime.TotalSeconds
     if($estadoNombre -eq 'Playing') {
      $delta=([DateTimeOffset]::UtcNow-$timeline.LastUpdatedTime).TotalSeconds
      if($delta -ge 0 -and $delta -lt 86400){$pos+=$delta*$tasa}
     }
    } catch {$pos=0;$dur=0}
    $clave=$fuente+"`n"+$titulo+"`n"+$artista
    if(-not $artes.ContainsKey($clave) -or (-not $artes[$clave] -and ([DateTime]::UtcNow-$revisiones[$clave]).TotalSeconds -gt 5)) {
     if($artes.Count -ge 8){$artes=@{};$revisiones=@{}}
     $artes[$clave]=''
     $revisiones[$clave]=[DateTime]::UtcNow
     if($media.Thumbnail){$artes[$clave]=LeerPortada $media.Thumbnail}
    }
    $datos=@{fuente=$fuente;titulo=$titulo;artista=$artista;estado=$estadoNombre;
      posicion=$pos;duracion=$dur;velocidad=$tasa;caratula=$artes[$clave];
      controles=@{pausa=([bool]$ctrl.IsPauseEnabled -or [bool]$ctrl.IsPlayPauseToggleEnabled);reanudar=([bool]$ctrl.IsPlayEnabled -or [bool]$ctrl.IsPlayPauseToggleEnabled);
                  anterior=[bool]$ctrl.IsPreviousEnabled;siguiente=[bool]$ctrl.IsNextEnabled;posicion=[bool]$ctrl.IsPlaybackPositionEnabled}}
    if($datos.caratula.Length -gt $presupuesto){$datos.caratula=''}else{$presupuesto-=$datos.caratula.Length}
    $items+=,$datos;$candidatos+=,@{sesion=$sesion;datos=$datos}
   } catch {}
  }
  [Console]::WriteLine((@{ok=[bool]$ok;codigo=$codigo;sesiones=@($items)}|ConvertTo-Json -Compress -Depth 5))
 } catch {[Console]::WriteLine('{"ok":false,"codigo":"lectura","sesiones":[]}')}
}
'''


def proveedor(fuente):
    f=fuente.casefold()
    for clave,nombre in (('spotify','Spotify'),('opera','Opera'),('chrome','Chrome'),('msedge','Edge'),
                         ('firefox','Firefox'),('brave','Brave'),('vivaldi','Vivaldi')):
        if clave in f:return nombre
    return ''


def normalizar_sesion(d):
    if not isinstance(d,dict) or not isinstance(d.get('fuente'),str) or not proveedor(d['fuente']):return None
    if not isinstance(d.get('titulo'),str) or not d['titulo'].strip():return None
    if len(d['fuente'])>1024 or len(d['titulo'])>2000 or not isinstance(d.get('artista',''),str) or len(d.get('artista',''))>2000:return None
    def numero(k):
        n=d.get(k,0)
        return max(0,min(604800,float(n))) if type(n) in (int,float) and math.isfinite(n) else 0
    r={k:d.get(k,'') for k in ('fuente','titulo','artista')}
    r.update(proveedor=proveedor(r['fuente']),estado=d.get('estado') if d.get('estado') in ('Playing','Paused','Stopped') else 'Unknown',
             posicion=numero('posicion'),duracion=numero('duracion'),
             velocidad=min(16,max(.125,numero('velocidad') or 1)),
             controles={k:d.get('controles',{}).get(k) is True for k in ('pausa','reanudar','anterior','siguiente','posicion')} if isinstance(d.get('controles'),dict) else {})
    arte=d.get('caratula','');r['caratula']=arte if isinstance(arte,str) and len(arte)<=1400000 else ''
    return r


def elegir(sesiones,preferencia='auto',fuente=None):
    if preferencia not in ('auto','spotify','navegador'):preferencia='auto'
    opciones=[s for s in sesiones if preferencia=='auto' or (s['proveedor']=='Spotify')==(preferencia=='spotify')]
    if preferencia=='auto':
        sonando=[s for s in opciones if s['estado']=='Playing']
        if sonando:return min(sonando,key=lambda s:s.get('_orden',float('inf')))
    if fuente:
        iguales=[s for s in opciones if (s['fuente'],s['titulo'],s['artista'])==fuente] if isinstance(fuente,tuple) else [s for s in opciones if s['fuente']==fuente]
        if not iguales and isinstance(fuente,tuple):iguales=[s for s in opciones if s['fuente']==fuente[0]]
        if len(iguales)==1:return iguales[0]
    return next((s for s in opciones if s['estado']=='Playing'),opciones[0] if opciones else None)


class OrdenReproduccion:
    """Conserva el inicio observado y amortigua lecturas ausentes, sin controlar audio."""
    def __init__(self):
        self.anteriores=[];self.secuencia=0

    def actualizar(self,sesiones,ahora):
        anteriores=self.anteriores
        nuevos=[];usados=set()
        for dato in sesiones:
            identidad=tuple(dato[k] for k in ('fuente','titulo','artista'))
            candidatos=[(i,s) for i,s in enumerate(anteriores) if i not in usados and tuple(s[k] for k in ('fuente','titulo','artista'))==identidad]
            if not candidatos and sum(s['fuente']==dato['fuente'] for s in sesiones)==1:
                candidatos=[(i,s) for i,s in enumerate(anteriores) if i not in usados and s['fuente']==dato['fuente']]
            previo=None
            if len(candidatos)==1:
                i,previo=candidatos[0];usados.add(i)
            orden=previo.get('_orden') if previo and previo['estado']=='Playing' and dato['estado']=='Playing' else None
            if dato['estado']=='Playing' and orden is None:
                self.secuencia+=1;orden=self.secuencia
            nuevos.append({**dato,'_orden':orden or float('inf'),'_visto':ahora,'_fecha':ahora,'_confirmada':True})
        for i,s in enumerate(anteriores):
            if i not in usados and ahora-s['_visto']<=3.5:
                nuevos.append({**s,'_confirmada':False,'controles':{}})
        self.anteriores=nuevos
        return nuevos


class ClienteMedia:
    def __init__(self):
        encoded=base64.b64encode(SCRIPT.encode('utf-16-le')).decode('ascii')
        self.proceso=subprocess.Popen(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',encoded],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf8',
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.respuestas=queue.Queue(maxsize=3)
        threading.Thread(target=self._leer,daemon=True,name='Capri-media-respuestas').start()

    def _leer(self):
        try:
            while True:
                linea=self.proceso.stdout.readline(4000001)
                if not linea or len(linea)>4000000:break
                self.respuestas.put_nowait(json.loads(linea))
        except (OSError,ValueError,queue.Full):pass
        try:self.respuestas.put_nowait(None)
        except queue.Full:pass

    def pedir(self,accion='estado',sesion=None,posicion=None):
        if accion not in ('estado','pausa','reanudar','anterior','siguiente','posicion'):raise ValueError('Acción multimedia inválida.')
        datos={'accion':accion}
        if accion!='estado':
            if not sesion:raise ValueError('Falta la sesión multimedia.')
            datos.update({k:sesion[k] for k in ('fuente','titulo','artista')})
            if accion=='posicion':
                if type(posicion) not in (int,float) or not math.isfinite(posicion) or not 0<=posicion<=sesion.get('duracion',0):raise ValueError('Posición inválida.')
                datos['posicion']=posicion
        self.proceso.stdin.write(json.dumps(datos,ensure_ascii=True)+'\n');self.proceso.stdin.flush()
        try:r=self.respuestas.get(timeout=12)
        except queue.Empty:raise OSError('La sesión no respondió.')
        if not isinstance(r,dict):raise OSError('La sesión no respondió.')
        return r

    def cerrar(self):
        if self.proceso.poll() is None:self.proceso.kill()
        try:self.proceso.wait(timeout=2)
        except subprocess.TimeoutExpired:pass
        for stream in (self.proceso.stdin,self.proceso.stdout):
            if stream:
                try:stream.close()
                except OSError:pass


class ReproduccionPC:
    def __init__(self,cliente=ClienteMedia):
        self.crear_cliente=cliente;self.cliente=None;self.sesiones=[];self.fecha=0;self.error='';self.ocupado=False
        self.activo=threading.Event();self.fin=threading.Event();self.despertar=threading.Event()
        self.ordenes=queue.Queue(maxsize=1);self.hilo=None
        self.orden=OrdenReproduccion()
        self.pendiente=None

    def presentar(self,sesion):
        p=self.pendiente
        if p and time.monotonic()<p['hasta'] and tuple(sesion[k] for k in ('fuente','titulo','artista'))==p['identidad']:
            return {**sesion,'estado':p['estado'],'posicion':p['posicion'],'_fecha':p['fecha'],'_pendiente':True}
        return sesion

    def activar(self,activo):
        cambio=self.activo.is_set()!=bool(activo)
        if activo:
            self.activo.set()
            if self.hilo is None:
                self.hilo=threading.Thread(target=self._trabajar,daemon=True,name='Capri-multimedia');self.hilo.start()
        else:self.activo.clear()
        if cambio:self.despertar.set()

    def solicitar(self,accion,sesion,posicion=None):
        if self.ocupado or self.fin.is_set() or not self.activo.is_set() or accion not in ('pausa','reanudar','anterior','siguiente','posicion'):return False
        if not sesion or sesion.get('_confirmada') is False or not sesion.get('controles',{}).get(accion):return False
        if accion=='posicion' and (type(posicion) not in (int,float) or not math.isfinite(posicion) or not 0<=posicion<=sesion.get('duracion',0)):return False
        self.ocupado=True
        ahora=time.monotonic()
        if accion in ('pausa','reanudar'):
            self.pendiente={'identidad':tuple(sesion[k] for k in ('fuente','titulo','artista')),
                            'estado':'Paused' if accion=='pausa' else 'Playing','fecha':ahora,
                            'posicion':min(sesion.get('duracion',0),sesion.get('posicion',0)+(max(0,ahora-sesion.get('_fecha',ahora))*sesion.get('velocidad',1) if sesion.get('estado')=='Playing' else 0)),'hasta':ahora+3}
        try:self.ordenes.put_nowait((accion,dict(sesion),posicion))
        except queue.Full:self.ocupado=False;self.pendiente=None;return False
        self.despertar.set();return True

    def _trabajar(self):
        try:
            while not self.fin.is_set():
                if not self.activo.is_set():
                    if self.cliente:self.cliente.cerrar();self.cliente=None
                    try:self.ordenes.get_nowait()
                    except queue.Empty:pass
                    self.ocupado=False;self.despertar.wait(.5);self.despertar.clear();continue
                try:
                    if self.cliente is None:self.cliente=self.crear_cliente()
                    try:accion,sesion,posicion=self.ordenes.get_nowait()
                    except queue.Empty:accion,sesion,posicion='estado',None,None
                    r=self.cliente.pedir(accion,sesion,posicion) if accion=='posicion' else self.cliente.pedir(accion,sesion)
                    if not r.get('ok'):self.error='Control no disponible.'
                    else:self.error=''
                    if not r.get('ok'):self.pendiente=None
                    # La respuesta ya incluye el estado posterior al control.
                    ahora=time.monotonic()
                    self.sesiones=self.orden.actualizar([s for d in r.get('sesiones',[])[:8] if (s:=normalizar_sesion(d))],ahora)
                    self.fecha=ahora
                    if self.pendiente:
                        p=self.pendiente
                        if ahora>=p['hasta'] or any(tuple(s[k] for k in ('fuente','titulo','artista'))==p['identidad'] and s['estado']==p['estado'] for s in self.sesiones):self.pendiente=None
                except (OSError,ValueError,TypeError,AttributeError):
                    self.error='No se pudo leer la reproducción.'
                    self.pendiente=None
                    ahora=time.monotonic();self.sesiones=self.orden.actualizar([],ahora);self.fecha=ahora if self.sesiones else 0
                    if self.cliente:self.cliente.cerrar();self.cliente=None
                finally:self.ocupado=False
                self.despertar.wait(.4 if self.fecha else 5);self.despertar.clear()
        finally:
            if self.cliente:self.cliente.cerrar();self.cliente=None

    def cerrar(self):
        self.activo.clear();self.fin.set();self.despertar.set()
        cliente=self.cliente
        if cliente and cliente.proceso.poll() is None:cliente.proceso.kill()
