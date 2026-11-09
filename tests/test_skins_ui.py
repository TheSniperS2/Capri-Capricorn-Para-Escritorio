import json
import time
from unittest.mock import Mock,patch
from tema_ui import tk
from test_capri import PruebasTk
from reacciones_skins import Lectura,MonitorSkins,catalogo,normalizar
from skins_ui import AjustesSkins,TEXTOS


class ReaccionesUI(PruebasTk):
    def test_cambio_descarta_voz_automatica_pero_no_una_narracion_nueva(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.voz,'parar') as parar:
            c.skin_narracion=(1,('anterior',),c.voz.generacion,c.peticion);c.voz_ticket=c.peticion
            c.cambiar_skin_observada(1,('nueva',));parar.assert_called_once();self.assertIsNone(c.voz_ticket)
            parar.reset_mock();c.skin_narracion=(1,('anterior',),c.voz.generacion-1,c.peticion)
            c.cambiar_skin_observada(1,('nueva',));parar.assert_not_called()

    def test_panel_catalogo_preferencias_demo_y_traducciones_sin_lecturas(self):
        from idiomas import catalogo as traducciones,ui
        root=tk.Tk();root.withdraw();f=tk.Frame(root);f.pack();guardar=Mock();enviar=Mock();ejemplo=Mock();fuente=Mock()
        m=MonitorSkins(Mock(),fuente);p=AjustesSkins(f,{},guardar,enviar,ejemplo,m)
        try:
            root.update();self.assertFalse(p.activo.get());self.assertGreaterEqual(len(p.opciones),15)
            p.cambiar('activo',True);p.cambiar('frecuencia','entusiasta')
            self.assertEqual(guardar.call_args.args,('reacciones_skins',normalizar({'activo':True,'frecuencia':'entusiasta'})))
            p.escuchar.invoke();self.assertEqual(ejemplo.call_args.args[0],p.texto.get());fuente.leer.assert_not_called()
            p.juego.current(1);p.llenar();self.assertGreater(len(p.opciones),23);self.assertLess(len(p.opciones),32)
            self.assertTrue(any(s['nombres']['en']=='Goku Black' for s in p.opciones))
            p.mirar.invoke();self.assertEqual(enviar.call_args.args[0],'mira mi skin en fortnite')
            for texto in TEXTOS:
                self.assertIn(texto,traducciones())
                for idioma in ('en','pt','ja'):self.assertTrue(ui(texto,idioma))
        finally:m.cerrar();root.destroy()

    def test_app_guarda_configuracion_y_abrir_ajustes_no_observa_juegos(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,ruta),patch.object(c.skins,'_fuentes') as fuente:
            c.configurar();c.panel_ajustes.mostrar('Reacciones');c.root.update()
            self.assertIn('Reacciones',c.panel_ajustes.secciones)
            c.ajustes_skins.cambiar('activo',True)
            self.assertTrue(c.cfg['reacciones_skins']['activo']);self.assertIsNone(c.skins.hilo)
            self.assertTrue(json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['reacciones_skins']['activo'])
            fuente.assert_not_called()
            for idioma in ('en','ja','es'):c.guardar('idioma',idioma);c.root.update()

    def test_orden_manual_pasa_al_controlador_sin_ia_y_sin_retraducir_frase_lista(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.skins,'opinar',return_value='A lovely design.') as opinar,patch.object(c.ia,'conversar') as ia,patch.object(c,'localizar_respuesta') as traducir:
            c.guardar('idioma','en');c.enviar('mira mi skin en fortnite');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertFalse(c.ocupada);self.assertEqual(opinar.call_args.args,('fortnite',))
            self.assertEqual(opinar.call_args.kwargs['idioma'],'en');ia.assert_not_called();traducir.assert_not_called()
            self.assertEqual(c.historial[-1][1],'A lovely design.')

    def test_evento_automatico_sonrie_y_respeta_respuesta_en_curso(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c,'decir_juego') as decir,patch.object(c.avatar,'sonreir') as sonrisa:
            c.finalizar_intro();fuente=Mock();fuente.primer_plano.return_value='fortnite';c.skins.fuentes=fuente
            c.skins.configurar({'activo':True},iniciar=False);c.skins.permitir(True)
            s=next(s for s in catalogo() if s['perfil']=='fry' and s['juego']=='fortnite');l=Lectura('fortnite','ficha',(s,))
            c.skins.motor.observar(l);p=c.skins.motor.observar(l)
            c.eventos.put(('skin_reaccion',(c.skins._version,p)));c.poll()
            decir.assert_called_once_with(p.texto);sonrisa.assert_called_once()
            decir.reset_mock();c.ocupada=True;c.eventos.put(('skin_reaccion',(c.skins._version,p)));c.poll()
            decir.assert_not_called();c.ocupada=False

    def test_mirar_fortnite_desde_ajustes_no_deja_la_ficha_tapada(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.skins,'opinar',return_value='Fry tiene estilo.') as opinar:
            c.configurar();c.panel_ajustes.mostrar('Reacciones');c.root.update()
            c.ajustes_skins.juego.current(1);c.ajustes_skins.llenar();c.ajustes_skins.mirar.invoke()
            limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertIsNone(c.ajustes);self.assertFalse(c.ocupada)
            self.assertEqual(opinar.call_args.args,('fortnite',))


if __name__=='__main__':__import__('unittest').main()
