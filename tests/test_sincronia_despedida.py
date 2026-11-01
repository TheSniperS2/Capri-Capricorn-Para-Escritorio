import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
import wave
import numpy as np
from sincronia import actividad_boca,boca_en_posicion
from voz import Voz


class SincroniaDespedida(unittest.TestCase):
    def test_primer_sonido_abre_antes_de_la_primera_consulta_de_posicion(self):
        eventos=[];v=Voz(eventos.append)
        def mci(comando,resultado=None,longitud=0):
            if comando.endswith(' length'):resultado.value='500'
            self.assertFalse(comando.endswith(' position'))
            return 0
        def antes_de_esperar(intervalo):
            self.assertTrue(v.boca_despedida(v.generacion))
            return True
        with patch('sincronia.actividad_boca',return_value=(True,)*25),patch('voz.time.monotonic',return_value=100.),patch.object(v,'_mci',side_effect=mci),patch.object(v.cancelar,'wait',side_effect=antes_de_esperar):
            v._reproducir_archivo_base(Path('simulado.wav'),v.generacion,v.cancelar,texto="I'll see you around, choom.")
            avances=[e[1][2] for e in eventos if isinstance(e,tuple) and e[0]=='avance_voz']
            self.assertTrue(avances[0])
            self.assertFalse(v.boca_despedida(v.generacion))

    def test_reloj_visual_avanza_sin_eventos_y_no_reutiliza_generacion_anterior(self):
        v=Voz(Mock());v._reloj_boca=(v.generacion,(True,False,True),100.)
        for tiempo,estado in ((100.001,True),(100.021,False),(100.041,True)):
            with patch('voz.time.monotonic',return_value=tiempo):
                self.assertIs(v.boca_despedida(v.generacion),estado)
        self.assertIsNone(v.boca_despedida(v.generacion+1))
        v.parar();self.assertIsNone(v.boca_despedida(v.generacion))

    def test_audio_real_con_silencios_y_choom_sin_modificar_archivo(self):
        sr=16000
        def tono(largo,volumen=.2):
            return np.sin(2*np.pi*230*np.arange(round(largo*sr))/sr)*volumen
        pcm=np.concatenate((np.zeros(1280),tono(.12),np.zeros(1280),tono(.1),np.zeros(8320),tono(.1,.04)))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'frase.wav'
            with wave.open(str(p),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
                w.writeframes(np.rint(pcm*32767).astype('<i2').tobytes())
            antes=hashlib.sha256(p.read_bytes()).digest()
            actividad=actividad_boca(p)
            self.assertEqual(hashlib.sha256(p.read_bytes()).digest(),antes)
        for t in (.01,.23,.45,.65,.87,1.1,-.01):
            self.assertFalse(boca_en_posicion(actividad,t),t)
        for t in (.11,.17,.31,.35,.93,.97):
            self.assertTrue(boca_en_posicion(actividad,t),t)

    def reproducir_simulado(self,texto,actividad,marcas=()):
        eventos=[];v=Voz(eventos.append);indice=0
        posiciones=(0,20,40,60)
        def mci(comando,resultado=None,longitud=0):
            nonlocal indice
            if comando.endswith(' length'):resultado.value='80'
            elif comando.endswith(' mode'):resultado.value='playing' if indice<len(posiciones) else 'stopped'
            elif comando.endswith(' position'):
                resultado.value=str(posiciones[indice]);indice+=1
            return 0
        with patch('sincronia.actividad_boca',side_effect=actividad if isinstance(actividad,Exception) else None,return_value=actividad) as medir,patch.object(v,'_mci',side_effect=mci),patch.object(v.cancelar,'wait',return_value=False):
            self.assertTrue(v._reproducir_archivo_base(Path('simulado.wav'),v.generacion,v.cancelar,texto=texto,marcas=marcas))
        return [e[1][2] for e in eventos if isinstance(e,tuple) and e[0]=='avance_voz'],medir

    def test_apertura_sigue_posicion_de_audio_incluso_dentro_de_misma_palabra(self):
        estados,medir=self.reproducir_simulado("I'll see you around, choom.",(False,True,False,True),[(0,10,0,1)])
        self.assertEqual(estados,[False,False,True,False,True,False])
        medir.assert_called_once()

    def test_error_de_decodificacion_conserva_marcas_como_respaldo(self):
        estados,_=self.reproducir_simulado("I'll see you around, choom.",ValueError('audio'),[(.02,.02,0,1)])
        self.assertIn(True,estados)
        self.assertFalse(estados[-1])

    def test_otros_dialogos_conservan_comportamiento_y_no_miden_audio(self):
        estados,medir=self.reproducir_simulado('Hola.',(False,False,False,False))
        medir.assert_not_called()
        self.assertIn(True,estados)
