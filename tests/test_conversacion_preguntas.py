import io,json,threading,unittest
from unittest.mock import Mock,patch
from core import IA,pide_una_pregunta,orientacion_conversacion
from escucha_activa import es_pregunta
from intenciones import Interprete


def respuesta(texto):return io.BytesIO(json.dumps({'message':{'content':texto}}).encode('utf8'))


class Conversacion(unittest.TestCase):
    def test_pedir_una_pregunta_es_charla_sin_acciones_ni_clasificador(self):
        for t in ('tienes alguna pregunta hacia mí?','¿Tienes una pregunta para mí?','Capri, hazme una pregunta','pregúntame algo'):
            self.assertTrue(pide_una_pregunta(t),t)
            with patch('intenciones.urllib.request.urlopen') as red:
                d=Interprete().resolver(t,'modelo')
                self.assertIsNone(d.orden);self.assertEqual(d.pregunta,'');red.assert_not_called()
        for t in ('no me hagas una pregunta','hazme una pregunta y abre Spotify','acepta partida en lol'):
            self.assertFalse(pide_una_pregunta(t),t)

    def test_modelo_que_solo_acepta_reintenta_sin_mostrar_ni_guardar_frase_mala(self):
        ia=IA();recibidos=[]
        with patch('core.urllib.request.urlopen',side_effect=[respuesta('¡Acepta cualquiera!'),respuesta('¿Qué música disfrutas escuchar?')]) as red:
            texto=ia.conversar('tienes alguna pregunta hacia mí?','modelo',al_texto=recibidos.append)
        self.assertEqual(texto,'¿Qué música disfrutas escuchar?');self.assertEqual(recibidos,[texto])
        self.assertNotIn('Acepta',repr(ia.historia));self.assertEqual(red.call_count,2)
        inicial=json.loads(red.call_args_list[0].args[0].data)
        self.assertFalse(inicial['stream']);self.assertIn('UNA pregunta concreta',inicial['messages'][-2]['content'])

    def test_segunda_respuesta_invalida_usa_una_pregunta_real_en_el_idioma_elegido(self):
        ia=IA();ia.idioma='en'
        with patch('core.urllib.request.urlopen',side_effect=[respuesta('Sure!'),respuesta('Anything you like.')]) as red:
            texto=ia.conversar('ask me a question','modelo')
        self.assertTrue(texto.endswith('?'));self.assertIn('free time',texto);self.assertEqual(red.call_count,2)

    def test_si_responde_a_propuesta_anterior_el_modelo_recibe_el_hilo_y_audio_transcrito(self):
        ia=IA();ia.historia=[{'role':'user','content':'Me gustan los gatos.'},
            {'role':'assistant','content':'¿Quieres una historia de un gato? ¡Te leo!'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('Un gato encontró una caja y decidió convertirla en su nave espacial.')) as red:
            ia.conversar('Sí, cuéntamela.','modelo',origen='voz')
        mensajes=json.loads(red.call_args.args[0].data)['messages']
        self.assertEqual(mensajes[-1],{'role':'user','content':'Sí, cuéntamela.'})
        self.assertIn('acepta tu propuesta anterior',mensajes[0]['content'])
        self.assertTrue(any(m['content']=='¿Quieres una historia de un gato? ¡Te leo!' for m in mensajes))
        self.assertTrue(any('YA fue transcrita' in m['content'] for m in mensajes if m['role']=='system'))

    def test_cancelar_durante_correccion_no_guarda_otra_respuesta(self):
        stop=threading.Event();ia=IA();llamadas=[0]
        def generar(*a,**k):
            llamadas[0]+=1
            if llamadas[0]==2:stop.set()
            return respuesta('¡Acepta cualquiera!')
        with patch('core.urllib.request.urlopen',side_effect=generar):
            with self.assertRaises(InterruptedError):ia.conversar('hazme una pregunta','modelo',cancelar=stop)
        self.assertEqual(ia.historia,[])

    def test_correcciones_rechazos_y_respuestas_no_son_el_mismo_tipo_de_turno(self):
        historia=[{'role':'assistant','content':'¿Quieres que te cuente una historia?'}]
        casos={
            'No, me refería a Hike Forever, la canción de Edge Runners 2.':'correccion',
            'Super bien, pero no entiendo muy bien tu pregunta, a qué viene.':'aclaracion',
            'Preferiría que no...':'rechazo',
            'No, gracias.':'rechazo',
            'No.':'rechazo',
            'Sí, cuéntamela.':'aceptacion',
            'Prefiero los gatos.':'',
            'No he escuchado esa canción.':'',
            'No quiero que cambies la canción.':'',
        }
        for texto,tipo in casos.items():
            self.assertEqual(orientacion_conversacion(texto,historia),tipo,texto)
        self.assertEqual(orientacion_conversacion('No.',[{'role':'assistant','content':'¿Conoces esa canción?'}]),'')
        self.assertEqual(orientacion_conversacion('Preferiría que no...',[]),'')

    def test_reporte_completo_no_muestra_ni_guarda_la_cadena_de_preguntas_desviadas(self):
        ia=IA();ia.historia=[{'role':'user','content':'¿Conoces Hike Forever?'},
            {'role':'assistant','content':'¿No escuchaste la música?'}]
        casos=[
            ('No, me refería a Hike Forever, la canción de Edge Runners 2.',
             '¿Entonces no escuchaste nada? ¿Qué tal el volumen en tu equipo hoy? ✨'),
            ('Super bien, pero no entiendo muy bien tu pregunta, a qué viene.',
             '¿Entonces el volumen estaba bajo? ¿Te sentiste sola con la música en silencio hoy? ✨'),
            ('Preferiría que no...',
             '¿Entonces prefieres cambiar el rumbo? ¿Qué tal si contamos una pequeña travesura imaginaria sobre un personaje del anime hoy en día? ✨'),
        ]
        for peticion,mala in casos:
            vistos=[]
            with patch('core.urllib.request.urlopen',return_value=respuesta(mala)) as red:
                buena=ia.conversar(peticion,'modelo',al_texto=vistos.append,origen='voz')
            self.assertFalse(es_pregunta(buena));self.assertNotEqual(buena,mala)
            self.assertEqual(vistos,[buena]);self.assertEqual(ia.historia[-1]['content'],buena)
            cuerpo=json.loads(red.call_args.args[0].data)
            self.assertFalse(cuerpo['stream']);self.assertEqual(cuerpo['messages'][-1]['content'],peticion)
            self.assertEqual([m['role'] for m in cuerpo['messages']].count('system'),1)
        self.assertNotIn('volumen estaba bajo',repr(ia.historia))
        self.assertIn('Hike Forever',repr(ia.historia))

    def test_una_correccion_no_puede_cambiar_el_referente_aunque_no_haga_preguntas(self):
        ia=IA();ia.historia=[{'role':'assistant','content':'¿Te refieres a un libro?'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('Ah, entendí mal: hablabas de la película.')):
            texto=ia.conversar('No, me refería a Hike Forever, la canción de Edge Runners 2.','modelo')
        self.assertIn('Hike Forever',texto);self.assertNotIn('película',texto)

    def test_correccion_con_pregunta_nueva_conserva_la_respuesta_a_esa_pregunta(self):
        ia=IA();ia.historia=[{'role':'assistant','content':'¿Te refieres a otro libro?'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('Frank Herbert escribió la novela.')):
            texto=ia.conversar('No, me refiero a Dune. ¿Quién la escribió?','modelo')
        self.assertEqual(texto,'Frank Herbert escribió la novela.')

    def test_rechazo_tambien_impide_otra_oferta_sin_signo_de_pregunta(self):
        ia=IA();ia.historia=[{'role':'assistant','content':'Podemos inventar una historia.'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('Te propongo hablar de videojuegos.')):
            texto=ia.conversar('Preferiría que no.','modelo')
        self.assertNotIn('videojuegos',texto);self.assertFalse(es_pregunta(texto))

    def test_reparacion_coherente_del_modelo_se_conserva_sin_frase_prefabricada(self):
        ia=IA();ia.historia=[{'role':'assistant','content':'¿Qué tal el volumen?'}]
        buena='Me fui por otro lado: hablabas de una canción y yo interpreté un problema de audio.'
        with patch('core.urllib.request.urlopen',return_value=respuesta(buena)):
            self.assertEqual(ia.conversar('No entiendo a qué viene tu pregunta.','modelo'),buena)

    def test_charla_no_se_duplica_como_prueba_del_ejecutor(self):
        ia=IA();ia.contexto_acciones=[
            {'accion':'','peticion':'Hablemos','resultado':'El volumen está bajo.'},
            {'accion':'spotify_pausa','peticion':'Pausa Spotify','resultado':'Spotify en pausa.'}]
        ia.historia=[{'role':'user','content':'Me gusta la música.'},
            {'role':'assistant','content':'¿Qué género prefieres?'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('El synthwave encaja con ese estilo.')) as red:
            ia.conversar('Synthwave.','modelo')
        mensajes=json.loads(red.call_args.args[0].data)['messages']
        self.assertNotIn('El volumen está bajo',mensajes[0]['content'])
        self.assertIn('Spotify en pausa',mensajes[0]['content'])
        self.assertEqual(mensajes[1:3],ia.historia[:2])
        self.assertNotIn('En este turno:',mensajes[0]['content'])

    def test_conversacion_normal_conserva_streaming_y_preguntas_pertinentes(self):
        ia=IA();fragmentos=['Me gusta ese estilo. ','¿Cuál es tu canción favorita?'];vistos=[]
        stream=io.BytesIO(b'\n'.join(json.dumps({'message':{'content':t}}).encode() for t in fragmentos))
        with patch('core.urllib.request.urlopen',return_value=stream) as red:
            salida=ia.conversar('Me gusta el synthwave.','modelo',al_texto=vistos.append)
        self.assertTrue(json.loads(red.call_args.args[0].data)['stream'])
        self.assertEqual(salida,''.join(fragmentos));self.assertEqual(vistos[-1],salida)

    def test_rechazo_localizado_no_traduce_una_pregunta_mala_antes_de_ocultarla(self):
        ia=IA();ia.idioma='en';ia.historia=[{'role':'assistant','content':'Would you like a story?'}]
        with patch('core.urllib.request.urlopen',return_value=respuesta('Would you like to discuss another topic?')):
            salida=ia.conversar('No thanks.','modelo')
        self.assertFalse(es_pregunta(salida));self.assertIn('leave it there',salida)


if __name__=='__main__':unittest.main()
