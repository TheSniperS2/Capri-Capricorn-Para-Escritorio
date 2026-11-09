"""Cliente ligero para una voz inglesa local opcional, en un proceso separado."""
from pathlib import Path
import atexit
import hashlib
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
import wave

CONFIG = Path(__file__).with_name('voz-ingles-local.json')
HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def cargar_config(ruta=None):
    ruta = Path(ruta or CONFIG).resolve()
    datos = json.loads(ruta.read_text(encoding='utf-8-sig'))
    for campo in ('python', 'modelo', 'perfil', 'cache'):
        valor = Path(datos[campo]).expanduser()
        datos[campo] = (ruta.parent / valor).resolve() if not valor.is_absolute() else valor.resolve()
    if not datos['python'].is_file() or not datos['perfil'].is_file():
        raise RuntimeError('Falta el motor o el perfil de la voz local.')
    if not (datos['modelo'] / 'config.json').is_file() or not (datos['modelo'] / 'model.safetensors').is_file():
        raise RuntimeError('Falta el modelo de la voz local.')
    datos['ruta'] = ruta
    datos['huella'] = hashlib.sha256(datos['perfil'].read_bytes()).hexdigest()
    if isinstance(datos.get('rapida'),dict):
        for campo in ('codigo','config','pesos','perfil'):
            valor=Path(datos['rapida'][campo]).expanduser()
            datos['rapida'][campo]=(ruta.parent/valor).resolve() if not valor.is_absolute() else valor.resolve()
    return datos


def disponible(ruta=None):
    try:
        cargar_config(ruta)
        return True
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return False


def clave_audio(config, texto, modo='local'):
    identidad = [1, config['huella'], str(config['modelo']),
                 config.get('revision_modelo', ''), ' '.join(texto.split())]
    if modo=='rapida':
        rapido=config['rapida']
        identidad += ['rapida-v1',hashlib.sha256(rapido['perfil'].read_bytes()).hexdigest(),
                      rapido.get('voz_base','en-US-AriaNeural'),rapido.get('tono_base','+8Hz'),
                      str(rapido['pesos']),rapido['pesos'].stat().st_mtime_ns]
    return hashlib.sha256(json.dumps(identidad, ensure_ascii=False).encode('utf8')).hexdigest()


def limpiar_trabajo(cache,ticket):
    import re
    if not ticket or not re.fullmatch('[a-f0-9]{32}',ticket):return
    trabajo=cache/'trabajos'/ticket
    if trabajo.parent.resolve()!=(cache/'trabajos').resolve() or not trabajo.is_dir():return
    for p in trabajo.iterdir():
        if p.is_file():
            try:p.unlink()
            except OSError:pass
    try:trabajo.rmdir()
    except OSError:pass


def podar_cache(cache,actual):
    import re
    archivos=sorted((p for p in cache.glob('*.wav') if re.fullmatch(r'[a-f0-9]{64}\.wav',p.name)),key=lambda p:p.stat().st_mtime,reverse=True)
    total=0
    for i,p in enumerate(archivos):
        total+=p.stat().st_size
        if p!=actual and (i>=256 or total>128*1024*1024):p.unlink(missing_ok=True)


def rapida_disponible(ruta=None):
    try:
        rapido=cargar_config(ruta)['rapida']
        return all(rapido[k].is_file() for k in ('config','pesos','perfil')) and (rapido['codigo']/'openvoice/models.py').is_file()
    except (OSError,ValueError,KeyError,TypeError,RuntimeError):return False


def wav_valido(ruta):
    try:
        with wave.open(str(ruta), 'rb') as audio:
            n = audio.getnframes()
            return (audio.getnchannels() == 1 and audio.getsampwidth() == 2
                    and audio.getframerate() == 24000 and n > 0
                    and len(audio.readframes(n)) == n * 2)
    except (OSError, EOFError, wave.Error):
        return False


def _terminar(proceso):
    if proceso is None:return
    try:
        if proceso.poll() is not None:return
        if os.name == 'nt':
            # El lanzador de un venv en Windows puede tener otro python hijo.
            exe = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'taskkill.exe'
            subprocess.run([str(exe), '/PID', str(proceso.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           creationflags=HIDDEN, timeout=3)
        else:
            proceso.terminate()
        proceso.wait(timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        try:proceso.kill()
        except OSError:pass
    finally:
        for flujo in (proceso.stdin, proceso.stdout):
            if flujo:
                try:flujo.close()
                except (OSError, ValueError):pass


class ClienteVozLocal:
    def __init__(self, ruta=None, motor=None, espera_inactiva=180):
        self.ruta = Path(ruta or CONFIG).resolve()
        self.motor = Path(motor or Path(__file__).with_name('voz_local_motor.py')).resolve()
        self.espera_inactiva = espera_inactiva
        self._turno = threading.Lock()
        self._control = threading.RLock()
        self._proceso = None
        self._mensajes = None
        self._firma = None
        self._temporizador = None
        self._cierres = set()
        self._fin_cierre = threading.Condition(self._control)

    def _cerrar(self, proceso=None):
        with self._control:
            if proceso is not None and proceso is not self._proceso:return
            actual = self._proceso
            self._proceso = None;self._mensajes = None;self._firma = None
            if self._temporizador:self._temporizador.cancel();self._temporizador = None
            if actual:self._cierres.add(actual)
        try:_terminar(actual)
        finally:
            with self._fin_cierre:
                self._cierres.discard(actual);self._fin_cierre.notify_all()

    def cerrar(self, esperar=False):
        if esperar:
            self._cerrar()
            with self._fin_cierre:self._fin_cierre.wait_for(lambda:not self._cierres,timeout=6)
        else:
            with self._control:actual = self._proceso
            if actual:threading.Thread(target=self._cerrar, args=(actual,), name='CapriCerrarVozLocal', daemon=True).start()

    def _iniciar(self, config, modo='local'):
        firma = (config['huella'], str(config['modelo']), str(config['python']),modo)
        if modo=='rapida':firma+=(hashlib.sha256(config['rapida']['perfil'].read_bytes()).hexdigest(),)
        with self._control:
            if self._temporizador:self._temporizador.cancel();self._temporizador = None
            proceso = self._proceso
            if proceso and proceso.poll() is None and self._firma == firma:
                return proceso, self._mensajes
        self._cerrar()
        config['cache'].mkdir(parents=True, exist_ok=True)
        mensajes = queue.Queue()
        entorno = dict(os.environ, PYTHONUTF8='1', HF_HUB_OFFLINE='1',
                       HF_HUB_DISABLE_IMPLICIT_TOKEN='1', TOKENIZERS_PARALLELISM='false')
        with (config['cache'] / 'motor.log').open('w', encoding='utf8') as log:
            proceso = subprocess.Popen([str(config['python']), '-u', str(self.motor), '--config', str(self.ruta),'--modo',modo],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log,
                                       text=True, encoding='utf8', creationflags=HIDDEN, env=entorno)
        with self._control:
            self._proceso = proceso;self._mensajes = mensajes;self._firma = firma
        def leer():
            try:
                for linea in proceso.stdout:
                    try:valor = json.loads(linea)
                    except ValueError:continue
                    if isinstance(valor, dict):mensajes.put(valor)
            except (OSError, ValueError):pass
            finally:mensajes.put({'tipo': 'cerrado'})
        threading.Thread(target=leer, name='CapriLeerVozLocal', daemon=True).start()
        return proceso, mensajes

    def precalentar(self,modo='rapida'):
        if not self._turno.acquire(blocking=False):return
        try:
            proceso,_=self._iniciar(cargar_config(self.ruta),modo)
            with self._control:
                self._temporizador=threading.Timer(self.espera_inactiva,lambda:self._cerrar(proceso))
                self._temporizador.daemon=True;self._temporizador.start()
        except (OSError,ValueError,KeyError,RuntimeError):pass
        finally:self._turno.release()

    def sintetizar(self, texto, cancelar, modo='local'):
        texto = ' '.join(texto.split())[:1800]
        if not texto:raise ValueError('Texto vacío.')
        config = cargar_config(self.ruta)
        archivo = config['cache'] / (clave_audio(config, texto,modo) + '.wav')
        if cancelar.is_set():raise InterruptedError()
        if wav_valido(archivo):return self._copiar(archivo, cancelar)
        while not self._turno.acquire(timeout=.05):
            if cancelar.is_set():raise InterruptedError()
        proceso = None;ticket=None
        try:
            if cancelar.is_set():raise InterruptedError()
            if wav_valido(archivo):return self._copiar(archivo, cancelar)
            proceso, mensajes = self._iniciar(config,modo)
            ticket = uuid.uuid4().hex
            proceso.stdin.write(json.dumps({'id': ticket, 'texto': texto, 'destino': str(archivo)}, ensure_ascii=False) + '\n')
            proceso.stdin.flush()
            limite = time.monotonic() + max(180, min(3600, len(texto) * 4))
            while True:
                if cancelar.is_set():raise InterruptedError()
                if time.monotonic() >= limite:raise TimeoutError('La voz local tardó demasiado.')
                try:mensaje = mensajes.get(timeout=.05)
                except queue.Empty:
                    if proceso.poll() is not None:raise RuntimeError('El motor local se cerró.')
                    continue
                if mensaje.get('tipo') == 'cerrado':raise RuntimeError('El motor local se cerró.')
                if mensaje.get('id') != ticket:continue
                if not mensaje.get('ok'):raise RuntimeError('No se pudo generar la voz local.')
                if Path(mensaje.get('archivo', '')).resolve() != archivo.resolve() or not wav_valido(archivo):
                    raise RuntimeError('El motor no entregó un audio válido.')
                return self._copiar(archivo, cancelar)
        except BaseException:
            if proceso:self._cerrar(proceso)
            raise
        finally:
            if modo=='rapida':limpiar_trabajo(config['cache'],ticket)
            with self._control:
                if self._proceso:
                    actual = self._proceso
                    self._temporizador = threading.Timer(self.espera_inactiva, lambda:self._cerrar(actual))
                    self._temporizador.daemon = True;self._temporizador.start()
            self._turno.release()

    def iterar(self,texto,cancelar):
        config=cargar_config(self.ruta)
        archivo=config['cache']/(clave_audio(config,texto,'rapida')+'.wav')
        if cancelar.is_set():raise InterruptedError()
        if wav_valido(archivo):
            yield self._copiar(archivo,cancelar),0,len(texto)
            return
        while not self._turno.acquire(timeout=.05):
            if cancelar.is_set():raise InterruptedError()
        proceso=None;ticket=uuid.uuid4().hex;trabajo=config['cache']/'trabajos'/ticket
        ultimo=0
        try:
            if cancelar.is_set():raise InterruptedError()
            proceso,mensajes=self._iniciar(config,'rapida')
            proceso.stdin.write(json.dumps({'id':ticket,'texto':texto,'destino':str(archivo),'fragmentos':True},ensure_ascii=False)+'\n');proceso.stdin.flush()
            limite=time.monotonic()+max(120,len(texto))
            while True:
                if cancelar.is_set():raise InterruptedError()
                if time.monotonic()>limite:raise TimeoutError('La voz rápida tardó demasiado.')
                try:m=mensajes.get(timeout=.05)
                except queue.Empty:
                    if proceso.poll() is not None:raise RuntimeError('El motor se cerró.')
                    continue
                if m.get('tipo')=='cerrado':raise RuntimeError('El motor se cerró.')
                if m.get('id')!=ticket:continue
                if m.get('tipo')=='fragmento':
                    p=Path(m.get('archivo','')).resolve();a=m.get('inicio');b=m.get('fin')
                    if p.parent!=trabajo.resolve() or not wav_valido(p) or not isinstance(a,int) or not isinstance(b,int) or not a==ultimo<b<=len(texto):
                        raise RuntimeError('Fragmento de voz inválido.')
                    ultimo=b
                    yield self._copiar(p,cancelar),a,b
                    continue
                if not m.get('ok') or Path(m.get('archivo','')).resolve()!=archivo.resolve() or not wav_valido(archivo):
                    raise RuntimeError('Audio de voz rápida inválido.')
                if ultimo==0:yield self._copiar(archivo,cancelar),0,len(texto)
                elif ultimo!=len(texto):raise RuntimeError('Respuesta de voz incompleta.')
                return
        except BaseException:
            if proceso:self._cerrar(proceso)
            raise
        finally:
            limpiar_trabajo(config['cache'],ticket)
            with self._control:
                if self._proceso:
                    actual=self._proceso
                    if self._temporizador:self._temporizador.cancel()
                    self._temporizador=threading.Timer(self.espera_inactiva,lambda:self._cerrar(actual))
                    self._temporizador.daemon=True;self._temporizador.start()
            self._turno.release()

    @staticmethod
    def _copiar(archivo, cancelar):
        if cancelar.is_set():raise InterruptedError()
        fd, nombre = tempfile.mkstemp(prefix='capri-voz-local-', suffix='.wav')
        os.close(fd)
        destino = Path(nombre)
        try:
            shutil.copyfile(archivo, destino)
            if cancelar.is_set():raise InterruptedError()
            return destino
        except BaseException:
            destino.unlink(missing_ok=True)
            raise


_clientes = {}
_lock = threading.Lock()


def cliente(ruta=None):
    ruta = Path(ruta or CONFIG).resolve()
    with _lock:
        if ruta not in _clientes:_clientes[ruta] = ClienteVozLocal(ruta)
        return _clientes[ruta]


def cerrar(ruta=None):
    with _lock:actual = _clientes.get(Path(ruta or CONFIG).resolve())
    if actual:actual.cerrar()


def _salir():
    for actual in list(_clientes.values()):actual.cerrar(esperar=True)


atexit.register(_salir)


def ajustar_velocidad(archivo, velocidad):
    """Atempo conserva el tono; la caché mantiene el audio original aprobado."""
    if abs(velocidad - 1) < .001:return archivo
    import av
    fd, nombre = tempfile.mkstemp(prefix='capri-voz-ritmo-', suffix='.wav');os.close(fd)
    salida = Path(nombre)
    try:
        with av.open(str(archivo)) as entrada, wave.open(str(salida), 'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(24000)
            grafo = av.filter.Graph()
            fuente = grafo.add_abuffer(template=entrada.streams.audio[0])
            tempo = grafo.add('atempo', str(velocidad))
            formato = grafo.add('aformat', 'sample_fmts=s16:sample_rates=24000:channel_layouts=mono')
            fin = grafo.add('abuffersink')
            fuente.link_to(tempo);tempo.link_to(formato);formato.link_to(fin);grafo.configure()
            def vaciar():
                while True:
                    try:frame = fin.pull()
                    except (BlockingIOError, EOFError):return
                    wav.writeframes(frame.to_ndarray().astype('<i2').tobytes())
            for frame in entrada.decode(audio=0):
                fuente.push(frame);vaciar()
            fuente.push(None);vaciar()
        if not wav_valido(salida):raise RuntimeError('No se pudo ajustar la velocidad.')
        return salida
    except BaseException:
        salida.unlink(missing_ok=True)
        raise
