import json
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import Mock,patch
import test_voz_local as fixtures
from voz_local import cargar_config,clave_audio,wav_valido
from voz_rapida import fragmentos
from voz import Voz


class VozRapida(unittest.TestCase):
    def setUp(self):
        fixtures.MotorLocal.setUp(self)
        d=json.loads(self.config.read_text())
        d['rapida']={'codigo':'.','config':'perfil.safetensors','pesos':'perfil.safetensors','perfil':'perfil.safetensors'}
        self.config.write_text(json.dumps(d))
        self.motor.write_text('''import sys,json,wave,time
from pathlib import Path
def wav(p,n=2400):
 with wave.open(str(p),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\\x00\\x00'*n)
for linea in sys.stdin:
 d=json.loads(linea);p=Path(d['destino']);p.parent.mkdir(exist_ok=True)
 job=p.parent/'trabajos'/d['id'];job.mkdir(parents=True,exist_ok=True)
 mitad=len(d['texto'])//2
 for i,(a,b) in enumerate([(0,mitad),(mitad,len(d['texto']))]):
  clip=job/(str(i)+'.wav');wav(clip)
  print(json.dumps({'id':d['id'],'tipo':'fragmento','archivo':str(clip),'inicio':a,'fin':b}),flush=True)
  time.sleep(.3)
 wav(p,4800)
 print(json.dumps({'id':d['id'],'ok':True,'archivo':str(p)}),flush=True)
''',encoding='utf8')

    def test_entrega_primer_audio_sin_esperar_final_y_limpia_fragmentos(self):
        inicio=time.monotonic();it=self.cliente.iterar('Una frase nueva para reproducir',threading.Event())
        p,a,b=next(it);primero=time.monotonic()-inicio
        self.assertEqual(a,0);self.assertTrue(wav_valido(p));p.unlink()
        restantes=list(it)
        self.assertEqual(len(restantes),1)
        self.assertGreater(time.monotonic()-inicio,primero+.25)
        for p,a,b in restantes:p.unlink()
        self.assertFalse(list((self.base/'cache/trabajos').glob('*')))
        self.assertEqual(len(list((self.base/'cache').glob('*.wav'))),1)

    def test_cancelar_tras_primer_fragmento_no_entrega_el_segundo(self):
        stop=threading.Event();it=self.cliente.iterar('Otra respuesta nueva para cancelar',stop)
        p,_,_=next(it);p.unlink();stop.set()
        with self.assertRaises(InterruptedError):next(it)
        self.assertFalse(list((self.base/'cache').glob('*.wav')))
        self.assertIsNone(self.cliente._proceso)

    def test_cache_distingue_modos_y_perfil_de_conversion(self):
        c=cargar_config(self.config);a=clave_audio(c,'Hello','rapida')
        self.assertNotEqual(a,clave_audio(c,'Hello','local'))
        (self.base/'perfil.safetensors').write_text('perfil cambiado')
        self.assertNotEqual(a,clave_audio(cargar_config(self.config),'Hello','rapida'))

    def test_fragmentos_no_pierden_palabras_y_primero_es_corto(self):
        texto='This is the first sentence. '+('Another phrase with several words. '*25)
        rangos=list(fragmentos(texto))
        self.assertEqual(''.join(texto[a:b] for a,b in rangos),texto)
        self.assertLessEqual(rangos[0][1],100)
        self.assertTrue(all(b-a<=210 for a,b in rangos[1:]))

    def test_voz_reproduce_fragmentos_con_progreso_continuo(self):
        original='Hello there. How are you?'
        archivos=[]
        for i in range(2):
            p=self.base/f'clip-{i}.wav';fixtures.wav(p,.1);archivos.append(p)
        servicio=Mock();servicio.iterar.return_value=iter([(archivos[0],0,13),(archivos[1],13,len(original))])
        eventos=[];v=Voz(eventos.append);v.idioma='en';v.ingles_local=True;v.modo_ingles='rapida'
        with patch('voz_local.cliente',return_value=servicio),patch.object(v,'_reproducir_archivo',return_value=True) as play:
            v._hablar(original,True,v.generacion,v.cancelar)
        self.assertEqual(play.call_count,2)
        primero,segundo=play.call_args_list
        self.assertEqual(primero.kwargs['rango'][0],0)
        self.assertEqual(primero.kwargs['rango'][1],segundo.kwargs['rango'][0])
        self.assertEqual(segundo.kwargs['rango'][1],len(original))
        self.assertEqual(sum(e is False for e in eventos),1)
        self.assertTrue(all(not p.exists() for p in archivos))
        self.assertEqual(v.ultima_voz_usada,'capri-ingles-rapida-v2')

    def test_rapida_no_envia_texto_si_voz_por_internet_desactivada(self):
        v=Voz(Mock());v.idioma='en';v.ingles_local=True;v.modo_ingles='rapida'
        with patch('voz_local.cliente') as cliente:
            v._hablar('Hello.',False,v.generacion,v.cancelar)
        cliente.assert_not_called()

    def test_voz_unica_no_cambia_por_idioma_o_acento_anterior(self):
        for idioma in ('es','en','pt','ja'):
            with self.subTest(idioma=idioma):
                p=self.base/f'voz-{idioma}.wav';fixtures.wav(p,.1)
                servicio=Mock();servicio.iterar.return_value=iter([(p,0,6)])
                v=Voz(Mock());v.idioma=idioma;v.acento='es-CL'
                v.ingles_local=True;v.modo_ingles='rapida';v.rapida_unica=True;v.solo_internet=True
                with patch('voz_local.cliente',return_value=servicio),patch.object(v,'_reproducir_archivo',return_value=True),patch('edge_tts.Communicate') as edge:
                    v._hablar('Hello.',True,v.generacion,v.cancelar)
                servicio.iterar.assert_called_once();edge.assert_not_called()
                self.assertEqual(v.ultima_voz_usada,'capri-ingles-rapida-v2')

    def test_fallo_de_internet_no_sustituye_por_voz_de_windows(self):
        v=Voz(Mock());v.solo_internet=True;v.natural_no_hasta=time.monotonic()+99
        with patch('edge_tts.Communicate',side_effect=RuntimeError('offline')) as edge,patch('voz.subprocess.Popen') as windows:
            v._hablar('Hello.',True,v.generacion,v.cancelar)
        edge.assert_called_once();windows.assert_not_called()

    def test_preparado_conserva_voz_fija_y_privacidad(self):
        v=Voz(Mock());v.rapida_unica=True;v.solo_internet=True
        with patch.object(Voz,'_hablar'):
            preparado=v.preparar('Hello.')
            self.assertTrue(preparado.listo.wait(2))
        self.assertTrue(preparado.sintetizador.rapida_unica)
        self.assertTrue(preparado.sintetizador.solo_internet)
        antes=preparado.clave;v.rapida_unica=False
        self.assertNotEqual(antes,v.clave_audio('Hello.'))
        preparado.descartar()

    def test_reloj_de_clip_respeta_rango_de_texto(self):
        p=self.base/'clip.wav';fixtures.wav(p,.1)
        eventos=[];v=Voz(eventos.append)
        def mci(cmd,buffer=None,*a):
            if buffer is not None:buffer.value='100' if cmd.endswith(' length') else 'stopped'
            return 0
        with patch.object(v,'_mci',side_effect=mci):
            v._reproducir_archivo_base(p,v.generacion,v.cancelar,texto='First. Second. Third.',rango=(7,14))
        avances=[e[1][1] for e in eventos if isinstance(e,tuple) and e[0]=='avance_voz']
        self.assertEqual(avances,[7,14])
