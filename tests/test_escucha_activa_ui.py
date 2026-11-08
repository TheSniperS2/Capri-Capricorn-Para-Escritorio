import json,threading,time
from unittest.mock import Mock,patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from escucha_activa import EscuchaActiva,TEXTOS
from test_escucha_activa import RESPUESTA_CON_PREGUNTA
import app


class EscuchaUI(PruebasTk):
    def test_respuesta_no_se_cancela_al_pasarla_a_whisper(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.ia,'conversar',return_value='Me contaste que prefieres los gatos.') as conversar:
            reloj=Mock(return_value=0);c.escucha_activa=EscuchaActiva('preguntas',reloj)
            c.escucha_activa.preparar(c.peticion,'¿Prefieres perros o gatos?',False);reloj.return_value=1
            reconociendo=threading.Event();terminar=threading.Event()
            def escuchar(stop,detectada,**k):
                k['lista']();detectada();k['estado']('Reconociendo la frase…');reconociendo.set()
                terminar.wait(2);return 'Prefiero los gatos.'
            with patch.object(c.micro,'escuchar_activamente',side_effect=escuchar),patch.object(c.micro,'esperar_activacion') as nombre:
                c.activacion_permitida=True;c.mantener_activacion();hilo=c.activacion_hilo
                try:
                    self.assertTrue(reconociendo.wait(1));ticket=c.activacion_ticket;c.poll()
                    self.assertFalse(c.activacion_stop.is_set(),'Se canceló la respuesta mientras Whisper la reconocía')
                    self.assertEqual(c.activacion_ticket,ticket);nombre.assert_not_called()
                    c.animar();self.assertEqual(c.entrada_compacta.texto_placeholder,'Reconociendo la frase…')
                    terminar.set();hilo.join(1);c.activacion_permitida=False;c.poll()
                    limite=time.monotonic()+3
                    while (c.ocupada or not conversar.called) and time.monotonic()<limite:c.poll();time.sleep(.005)
                    conversar.assert_called_once();self.assertEqual(conversar.call_args.args[0],'Prefiero los gatos.')
                    self.assertEqual(conversar.call_args.kwargs['origen'],'voz')
                    self.assertEqual(c.historial[-1],('Capri','Me contaste que prefieres los gatos.'))
                finally:
                    terminar.set();hilo.join(1);c.activacion_permitida=False

    def test_pregunta_con_cierre_adicional_permite_contestar_sin_nombre(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.voz,'hablar'),patch.object(c,'enviar') as enviar:
            reloj=Mock(return_value=0);c.escucha_activa=EscuchaActiva('preguntas',reloj);c.cfg['voz']=True
            c.eventos.put(('respuesta',(c.peticion,RESPUESTA_CON_PREGUNTA)));c.poll()
            self.assertEqual(c.escucha_activa.ticket,c.peticion)
            c.eventos.put(('voz',True));c.poll();reloj.return_value=30
            self.assertEqual(c.escucha_activa.hasta,0)
            c.eventos.put(('voz',False));c.poll();reloj.return_value=30.5
            c.activacion_permitida=True
            with patch('app.threading.Thread') as hilo:
                c.mantener_activacion();trabajar=hilo.call_args.kwargs['target'];c.activacion_hilo=None
            def escuchar(stop,detectada,**k):k['lista']();detectada();return 'Sí, cuéntamela.'
            with patch.object(c.micro,'escuchar_activamente',side_effect=escuchar) as micro:
                trabajar();c.activacion_permitida=False;c.poll()
            self.assertGreater(micro.call_args.kwargs['espera'],14)
            enviar.assert_called_once_with('Sí, cuéntamela.',origen='voz')
            self.assertIsNone(c.panel)

    def test_panel_opcional_guarda_modo_y_traducciones_sin_abrir_microfono(self):
        from idiomas import catalogo,ui
        with fixtures.ModoPersonaje.capri(self) as (c,p),patch.object(c.micro,'escuchar_activamente') as micro:
            self.assertEqual(c.cfg['modo_escucha'],'nombre');c.configurar();c.root.update()
            c.escucha_combo.current(2);c.escucha_combo.event_generate('<<ComboboxSelected>>');c.root.update()
            self.assertEqual(c.escucha_activa.modo,'continua')
            self.assertEqual(json.loads((p/'ajustes.json').read_text(encoding='utf8'))['modo_escucha'],'continua')
            micro.assert_not_called()
            for t in TEXTOS:
                self.assertIn(t,catalogo())
                for idioma in ('en','pt','ja'):self.assertTrue(ui(t,idioma))

    def test_pregunta_hablada_espera_fin_real_no_false_de_preparacion(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.voz,'hablar'):
            reloj=Mock(return_value=0);c.escucha_activa=EscuchaActiva('preguntas',reloj);c.cfg['voz']=True
            c.eventos.put(('respuesta',(c.peticion,'¿Qué canción quieres?')));c.poll()
            ticket=c.peticion;self.assertEqual(c.escucha_activa.ticket,ticket)
            c.hablando=True  # Puede quedar la bandera de la voz anterior.
            c.eventos.put(('voz',False));c.poll();self.assertEqual(c.escucha_activa.hasta,0)
            c.eventos.put(('voz',True));c.poll();reloj.return_value=30
            c.eventos.put(('voz',False));c.poll();reloj.return_value=30.5
            self.assertEqual(c.escucha_activa.tipo(),'preguntas');self.assertGreater(c.escucha_activa.espera(),14)
            self.assertIsNone(c.panel)

    def test_continua_funciona_sin_activacion_por_nombre_y_entrega_una_frase(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c,'enviar') as enviar:
            c.cfg.update(modo_escucha='continua',activacion_voz=False);c.escucha_activa.configurar('continua');c.activacion_permitida=True
            def escuchar(stop,detectada,**k):k['lista']();detectada();return 'Pon Capricorn'
            with patch.object(c.micro,'escuchar_activamente',side_effect=escuchar) as micro,patch.object(c.micro,'esperar_activacion') as nombre,patch('app.threading.Thread') as hilo:
                c.mantener_activacion();trabajar=hilo.call_args.kwargs['target'];c.activacion_hilo=None
                trabajar();c.activacion_permitida=False;c.poll()
            micro.assert_called_once();nombre.assert_not_called();enviar.assert_called_once_with('Pon Capricorn',origen='voz')

    def test_pausa_esc_descarta_lecturas_viejas_y_f8_reanuda(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c,'enviar') as enviar,patch('app.threading.Thread'):
            c.cfg['modo_escucha']='continua';c.escucha_activa.configurar('continua');c.activacion_tipo='continua'
            c.activacion_en_curso=True
            anterior=c.activacion_ticket;c.interrumpir()
            c.eventos.put(('activacion_resultado',(anterior,'busca partida en fortnite',None)));c.poll()
            enviar.assert_not_called();self.assertTrue(c.escucha_activa.pausada)
            self.assertFalse(c.activacion_en_curso)
            c.hablar();self.assertFalse(c.escucha_activa.pausada);self.assertTrue(c.escuchando)

    def test_no_captura_durante_voz_ajustes_o_escritura_y_no_acepta_evento_tardio(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch('app.threading.Thread') as hilo,patch.object(c,'recibir_dictado') as recibir:
            c.escucha_activa.configurar('continua');c.activacion_permitida=True
            c.voz_ticket=c.peticion;c.mantener_activacion();hilo.assert_not_called();c.voz_ticket=None
            c.activacion_tipo='continua';ticket=c.activacion_ticket
            with patch.object(c,'escribiendo',return_value=True):
                c.mantener_activacion();hilo.assert_not_called()
                c.eventos.put(('activacion_resultado',(ticket,'borra una foto',None)));c.poll();recibir.assert_not_called()
            c.activacion_permitida=False

    def test_silencio_sin_mensajes_y_dictado_dudoso_se_revisa(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c,'enviar') as enviar:
            c.escucha_activa.configurar('continua');c.activacion_tipo='continua'
            c.eventos.put(('activacion_resultado',(c.activacion_ticket,None,None)));c.poll()
            self.assertEqual(c.historial,[]);enviar.assert_not_called()
            c.micro.confianza_baja=True;c.recibir_dictado('abre spotify')
            enviar.assert_not_called();self.assertTrue(c.escucha_activa.pausada)

    def test_campo_vacio_con_foco_permite_responder_y_texto_pendiente_pausa(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_):
            entrada=c.entrada_compacta.entrada
            with patch.object(c.root,'focus_get',return_value=entrada):
                self.assertFalse(c.bloqueada_escucha_activa())
                c.entrada_compacta.placeholder=False;entrada.delete(0,'end');entrada.insert(0,'Escribiendo una frase')
                self.assertTrue(c.bloqueada_escucha_activa())
                entrada.delete(0,'end');self.assertFalse(c.bloqueada_escucha_activa())

    def test_pregunta_sin_voz_abre_ventana_limitada_y_silencio_la_cierra(self):
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch('app.threading.Thread') as hilo:
            reloj=Mock(return_value=0);c.escucha_activa=EscuchaActiva('preguntas',reloj)
            c.cfg['activacion_voz']=False;c.eventos.put(('respuesta',(c.peticion,'¿Qué prefieres?')));c.poll()
            reloj.return_value=1;c.activacion_permitida=True;c.mantener_activacion()
            trabajar=hilo.call_args.kwargs['target'];c.activacion_hilo=None
            with patch.object(c.micro,'escuchar_activamente',return_value=None) as micro:
                trabajar();c.activacion_permitida=False;c.poll()
            self.assertGreater(micro.call_args.kwargs['espera'],14)
            self.assertEqual(c.escucha_activa.tipo(),'nombre')
            self.assertEqual(len(c.historial),1)


if __name__=='__main__':__import__('unittest').main()
