import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
import threading
import time
import unittest
import wave
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from voz_local import ClienteVozLocal, disponible, ajustar_velocidad, wav_valido
from voz_local_motor import fragmentar
from voz import Voz


def wav(ruta, segundos=1):
    with wave.open(str(ruta), 'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000)
        f.writeframes(b''.join(struct.pack('<h', round(12000 * math.sin(2 * math.pi * 240 * i / 24000)))
                               for i in range(round(24000 * segundos))))


class MotorLocal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / 'modelo').mkdir()
        for n in ('config.json', 'model.safetensors'):(self.base / 'modelo' / n).write_text('fixture')
        (self.base / 'perfil.safetensors').write_text('fixture')
        self.config = self.base / 'local.json'
        self.config.write_text(json.dumps({'python':sys.executable, 'modelo':'modelo', 'perfil':'perfil.safetensors', 'cache':'cache'}))
        self.motor = self.base / 'motor.py'
        self.motor.write_text('''import sys,json,time,wave,os
from pathlib import Path
for linea in sys.stdin:
 d=json.loads(linea)
 if d['texto']=='lento':time.sleep(20)
 p=Path(d['destino']);p.parent.mkdir(exist_ok=True)
 with wave.open(str(p),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\\x00\\x00'*2400)
 print(json.dumps({'id':d['id'],'ok':True,'archivo':str(p)}),flush=True)
''', encoding='utf8')
        self.cliente = ClienteVozLocal(self.config, self.motor, espera_inactiva=20)
        self.addCleanup(lambda:self.cliente.cerrar(esperar=True))

    def test_reutiliza_proceso_y_cache_y_entrega_copia_independiente(self):
        self.assertTrue(disponible(self.config))
        stop = threading.Event()
        a = self.cliente.sintetizar('Primera frase', stop)
        proceso = self.cliente._proceso
        b = self.cliente.sintetizar('Otra frase', stop)
        self.assertIs(self.cliente._proceso, proceso)
        a.unlink();b.unlink()
        with patch.object(self.cliente, '_iniciar', side_effect=AssertionError('La cache no necesita motor')):
            c = self.cliente.sintetizar('Primera frase', stop)
        self.assertTrue(wav_valido(c));c.unlink()

    def test_cancelar_mata_trabajo_no_entrega_audio_y_permite_reiniciar(self):
        stop = threading.Event();fallos=[]
        def trabajo():
            try:self.cliente.sintetizar('lento', stop)
            except BaseException as error:fallos.append(error)
        hilo = threading.Thread(target=trabajo);hilo.start()
        limite=time.monotonic()+4
        while not self.cliente._proceso and time.monotonic()<limite:time.sleep(.01)
        proceso=self.cliente._proceso
        self.assertIsNotNone(proceso)
        stop.set();hilo.join(6)
        self.assertFalse(hilo.is_alive());self.assertIsInstance(fallos[0],InterruptedError)
        self.assertIsNotNone(proceso.poll())
        self.assertFalse(list((self.base/'cache').glob('*.wav')))
        salida=self.cliente.sintetizar('Luego de cancelar',threading.Event())
        self.assertTrue(wav_valido(salida));salida.unlink()

    def test_cancelar_en_cola_no_interrumpe_al_otro_solicitante(self):
        self.cliente._turno.acquire();stop=threading.Event();fallos=[]
        def trabajo():
            try:self.cliente.sintetizar('En cola',stop)
            except BaseException as error:fallos.append(error)
        hilo=threading.Thread(target=trabajo);hilo.start();stop.set();hilo.join(2)
        self.cliente._turno.release()
        self.assertFalse(hilo.is_alive());self.assertIsInstance(fallos[0],InterruptedError)
        self.assertIsNone(self.cliente._proceso)

    def test_cambio_de_perfil_invalida_cache(self):
        stop=threading.Event();a=self.cliente.sintetizar('Una frase',stop);a.unlink()
        anterior=self.cliente._proceso
        (self.base/'perfil.safetensors').write_text('otra voz')
        b=self.cliente.sintetizar('Una frase',stop);b.unlink()
        self.assertIsNot(self.cliente._proceso,anterior)
        self.assertEqual(len(list((self.base/'cache').glob('*.wav'))),2)

    def test_cierre_atrasado_no_mata_motor_nuevo(self):
        a=self.cliente.sintetizar('Primera',threading.Event());a.unlink()
        pendientes=[]
        class Diferido:
            def __init__(self,target,args=(),**kw):pendientes.append((target,args))
            def start(self):pass
        with patch('voz_local.threading.Thread',Diferido):self.cliente.cerrar()
        (self.base/'perfil.safetensors').write_text('perfil nuevo')
        b=self.cliente.sintetizar('Segunda',threading.Event());b.unlink()
        nuevo=self.cliente._proceso
        for funcion,args in pendientes:funcion(*args)
        self.assertIsNone(nuevo.poll())
        c=self.cliente.sintetizar('Tercera',threading.Event());c.unlink()
        self.assertIs(self.cliente._proceso,nuevo)

    def test_libera_motor_inactivo_y_conserva_audio_guardado(self):
        self.cliente.espera_inactiva=.15
        a=self.cliente.sintetizar('Persistente',threading.Event());a.unlink()
        proceso=self.cliente._proceso;limite=time.monotonic()+4
        while proceso.poll() is None and time.monotonic()<limite:time.sleep(.02)
        self.assertIsNotNone(proceso.poll())
        b=self.cliente.sintetizar('Persistente',threading.Event());b.unlink()
        self.assertIsNone(self.cliente._proceso)

    def test_ritmo_cambia_duracion_y_conserva_tono(self):
        import numpy as np
        origen=self.base/'onda.wav';wav(origen,2)
        rapido=ajustar_velocidad(origen,1.5);self.addCleanup(lambda:rapido.unlink(missing_ok=True))
        self.assertTrue(wav_valido(rapido))
        with wave.open(str(rapido),'rb') as f:
            self.assertAlmostEqual(f.getnframes()/24000,2/1.5,delta=.06)
            a=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        frecuencia=np.fft.rfftfreq(len(a),1/24000)[np.argmax(abs(np.fft.rfft(a)))]
        self.assertAlmostEqual(frecuencia,240,delta=3)
        self.assertTrue(wav_valido(origen))

    def test_fragmentos_conservan_texto_y_no_cortan_respuesta_corta(self):
        corto="Hey, I'm Capri! Tell me what you want to do, and let's make it happen."
        self.assertEqual(fragmentar(corto),[corto])
        largo=('One sentence with several words. '*30).strip()
        partes=fragmentar(largo)
        self.assertEqual(' '.join(partes),largo)
        self.assertTrue(all(len(p)<=220 for p in partes))


class RutaDeVoz(unittest.TestCase):
    def test_ingles_usa_local_y_no_sustituye_por_edge_o_windows(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'voz.wav';wav(p,.1)
            motor=Mock();motor.sintetizar.return_value=p
            v=Voz(Mock());v.idioma='en';v.ingles_local=True
            with patch('voz_local.cliente',return_value=motor),patch.object(v,'_reproducir_archivo',return_value=True) as reproducir,patch('edge_tts.Communicate') as edge:
                v._hablar('Hello, choom.',True,v.generacion,v.cancelar)
            self.assertEqual(v.ultima_voz_usada,'capri-ingles-local-v2')
            motor.sintetizar.assert_called_once();edge.assert_not_called();reproducir.assert_called_once()
            self.assertFalse(v.preparando_local);self.assertFalse(p.exists())

    def test_otro_idioma_o_invitado_conserva_su_voz(self):
        class Sintesis:
            def __init__(self,*a,**kw):pass
            async def stream(self):yield {'type':'audio','data':b'audio fixture'}
        for idioma,invitado in [('es',None),('en','d')]:
            v=Voz(Mock());v.idioma=idioma;v.ingles_local=True
            with patch('voz_local.cliente') as local,patch('edge_tts.Communicate',Sintesis),patch.object(v,'_reproducir_archivo',return_value=True):
                v._hablar('Una frase.',True,v.generacion,v.cancelar,invitado=invitado)
            local.assert_not_called()

    def test_error_local_no_cambia_silenciosamente_la_voz(self):
        v=Voz(Mock());v.idioma='en';v.ingles_local=True
        with patch('voz_local.cliente',side_effect=RuntimeError()),patch('edge_tts.Communicate') as edge,patch.object(v,'_reproducir_windows') as windows:
            v._hablar('Hello.',True,v.generacion,v.cancelar)
        edge.assert_not_called();windows.assert_not_called()
        self.assertEqual(v.ultimo_error_voz['fase'],'voz_local')

    def test_preparacion_hereda_eleccion_y_no_se_reproduce_sola(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'voz.wav';wav(p,.1)
            motor=Mock();motor.sintetizar.return_value=p
            v=Voz(Mock());v.idioma='en';v.ingles_local=True
            with patch('voz_local.cliente',return_value=motor):
                preparado=v.preparar('Hello.')
                self.assertTrue(preparado.listo.wait(3));self.assertTrue(preparado.archivo.exists())
                self.assertTrue(preparado.sintetizador.ingles_local)
                v.ingles_local=False
                self.assertNotEqual(preparado.clave,v.clave_audio('Hello.'))
                preparado.descartar()


if __name__=='__main__':unittest.main()
