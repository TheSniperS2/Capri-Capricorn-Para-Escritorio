import array,json,threading,types,unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock,patch
import activacion,voz
from escucha_activa import EscuchaActiva,es_pregunta,normalizar

RESPUESTA_CON_PREGUNTA=('¡Me encantan tanto a mis amigos felinos como mi compañero Capri!  '
    'Pero, ¿quieres que narro una historia sobre cómo un perro y un gato se conocieron '
    'en la oficina de trabajo hace dos años? ¡Espero tu interés! ✨')


class Turnos(unittest.TestCase):
    def test_pregunta_seguida_de_otra_frase_abre_escucha_con_ejemplo_real(self):
        self.assertTrue(es_pregunta(RESPUESTA_CON_PREGUNTA))
        reloj=Mock(return_value=0);m=EscuchaActiva('preguntas',reloj)
        m.preparar(9,RESPUESTA_CON_PREGUNTA,True)
        reloj.return_value=30;m.fin_voz(9);reloj.return_value=30.5
        self.assertEqual(m.tipo(),'preguntas');self.assertGreater(m.espera(),14)

    def test_opcional_y_solo_preguntas_reales_abren_turno(self):
        self.assertEqual(normalizar(None),'nombre');self.assertEqual(normalizar(True),'nombre')
        for texto in ('¿Qué te gustaría escuchar?','Do you want more?','Quer continuar?','どうする？','¿Quieres «Capricorn»? 😊',
                      'Want a story? I can tell you one.','Quer uma história? Vou esperar sua resposta.',
                      'お話を聞きたい？返事を待ってるよ。'):
            self.assertTrue(es_pregunta(texto),texto)
        for texto in ('Listo.','Me preguntaste «¿qué hora es?».','Ejemplo: ```¿seguimos?```',
                      'Consulta https://ejemplo.invalid/?q=capri para ver la ayuda.',
                      'El operador `x ? y : z` elige un valor.'):
            self.assertFalse(es_pregunta(texto),texto)
        m=EscuchaActiva();m.preparar(1,'¿Seguimos?',False);self.assertEqual(m.tipo(),'nombre')

    def test_espera_empieza_al_terminar_audio_no_al_generar_pregunta(self):
        reloj=Mock(return_value=0);m=EscuchaActiva('preguntas',reloj)
        m.preparar(7,'¿Cuál prefieres?',True);reloj.return_value=40
        self.assertEqual(m.tipo(),'nombre');m.fin_voz(6);self.assertEqual(m.tipo(),None)
        m.fin_voz(7);reloj.return_value=40.5;self.assertEqual(m.tipo(),'preguntas');self.assertAlmostEqual(m.espera(),14.9)
        reloj.return_value=56;self.assertEqual(m.tipo(),'nombre')

    def test_respuesta_sin_voz_pausa_y_nuevo_turno_no_usan_pregunta_vieja(self):
        reloj=Mock(return_value=1);m=EscuchaActiva('preguntas',reloj)
        m.preparar(1,'¿Seguimos?',False);reloj.return_value=2;self.assertEqual(m.tipo(),'preguntas')
        m.preparar(2,'Listo.',False);reloj.return_value=3;self.assertEqual(m.tipo(),'nombre')
        m.preparar(3,'¿Ahora?',True);m.pausar();m.fin_voz(3);reloj.return_value=4;self.assertEqual(m.tipo(),'nombre')
        m.configurar('continua');self.assertEqual(m.tipo(),'continua');m.pausar();self.assertEqual(m.tipo(),'nombre')
        m.reanudar();self.assertEqual(m.tipo(),'continua')


class Captura(unittest.TestCase):
    def capturar(self,*,motor='mixto',habla=True,espera=3,texto='abre spotify'):
        detener=threading.Event();posicion=[0];tiempo=[0.];avisos=Mock();cerrada=[]
        class Reconocedor:
            def AcceptWaveform(self,b):
                posicion[0]+=1;tiempo[0]+=.2
                return posicion[0]==3
            def Result(self):return json.dumps({'text':texto})
            def PartialResult(self):return json.dumps({'partial':texto if posicion[0]<3 else ''})
            def FinalResult(self):return '{"text":""}'
        @contextmanager
        def entrada(indice,datos,recibir,stop,intentos):
            for i in range(20):recibir(array.array('h',[1200 if habla and i<2 else 0]*3200).tobytes(),3200,None,None)
            try:yield 16000
            finally:cerrada.append(True)
        sd=types.SimpleNamespace(query_devices=lambda *a,**k:{'name':'USB'})
        vosk=types.SimpleNamespace(Model=Mock(),SetLogLevel=lambda x:None,KaldiRecognizer=lambda *a:Reconocedor())
        micro=types.SimpleNamespace(modelo=object(),carpeta=Path('.'),modelo_whisper='base')
        with patch.dict('sys.modules',{'sounddevice':sd,'vosk':vosk}),patch.object(voz,'resolver_microfono',return_value=23),patch.object(voz,'_abrir_entrada',entrada),patch.object(activacion,'DetectorVoz',return_value=types.SimpleNamespace(analizar=lambda b,t:bool(any(b)))),patch.object(activacion.time,'monotonic',side_effect=lambda:tiempo[0]),patch('reconocimiento.disponible',return_value=True),patch('reconocimiento.transcribir',side_effect=lambda *a: ('Abre Spotify' if cerrada else self.fail('ASR antes de cerrar entrada'))) as transcribir:
            resultado=activacion.esperar(micro,detener,avisos,motor=motor,sin_nombre=True,espera=espera)
        return resultado,avisos,transcribir

    def test_whisper_acepta_respuesta_sin_nombre_y_conserva_comienzo(self):
        resultado,aviso,transcribir=self.capturar()
        self.assertEqual(resultado,'Abre Spotify');aviso.assert_called_once();transcribir.assert_called_once()
        self.assertTrue(transcribir.call_args.args[1].startswith(array.array('h',[1200]*3200).tobytes()))

    def test_vosk_sin_whisper_acepta_frase_sin_relajar_el_modo_normal(self):
        resultado,aviso,convertir=self.capturar(motor='rapido')
        self.assertEqual(resultado,'abre spotify');aviso.assert_called_once();convertir.assert_not_called()

    def test_silencio_aunque_vosk_invente_texto_no_transcribe_ni_activa(self):
        resultado,aviso,convertir=self.capturar(habla=False,espera=1)
        self.assertIsNone(resultado);aviso.assert_not_called();convertir.assert_not_called()


if __name__=='__main__':unittest.main()
