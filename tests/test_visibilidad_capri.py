import time
from unittest.mock import Mock,patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from tema_ui import tk
from visibilidad import VisibilidadCapri

class Visibilidad(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_minimizar_y_recuperar_conserva_voz_y_preferencias(self):
        with self.capri() as (c,_),patch('ventanas.traer_al_frente') as traer:
            c.abrir_chat();c.root.update();preferencias=dict(c.cfg);vigilar=c.valorant.config.copy()
            c.minimizar_capri();c.root.update()
            self.assertTrue(c.visibilidad.oculta);self.assertEqual(c.root.state(),'withdrawn')
            self.assertEqual(c.panel.state(),'withdrawn');self.assertEqual(c.cfg,preferencias);self.assertEqual(c.valorant.config,vigilar)
            c.visibilidad.mostrar();c.root.update()
            self.assertFalse(c.visibilidad.oculta);self.assertEqual(c.panel.state(),'withdrawn');self.assertTrue(c.root.overrideredirect())
            traer.assert_not_called()
            c.abrir_chat();c.root.update();self.assertEqual(c.panel.state(),'normal')

    def test_minimizado_bloquea_avisos_y_recupera_solo_avatar(self):
        root=tk.Tk();root.overrideredirect(True);panel=tk.Toplevel(root);root.update()
        control=VisibilidadCapri(root)
        try:
            control.ocultar();root.update();nuevo=tk.Toplevel(root);root.update()
            self.assertTrue(control.oculta);self.assertEqual(nuevo.state(),'withdrawn')
            root.deiconify();root.update()
            self.assertFalse(control.oculta);self.assertTrue(root.overrideredirect())
            self.assertEqual(panel.state(),'withdrawn');self.assertEqual(nuevo.state(),'withdrawn')
        finally:root.destroy()

    def test_atajo_revela_desde_otro_programa_y_minimiza_desde_capri(self):
        root=tk.Tk();root.overrideredirect(True);control=VisibilidadCapri(root,al_mostrar=Mock())
        try:
            with patch('ventanas.primer_plano_propio',return_value=False):control.alternar();self.assertFalse(control.oculta)
            with patch('ventanas.primer_plano_propio',return_value=True):control.alternar();self.assertTrue(control.oculta)
            with patch('ventanas.primer_plano_propio',return_value=False):control.alternar();self.assertFalse(control.oculta)
        finally:root.destroy()

    def test_recuperar_cierra_desplegable_y_permite_abrirlo_de_nuevo(self):
        from ajustes_ui import SelectorCyber
        root=tk.Tk();root.overrideredirect(True)
        selector=SelectorCyber(root,values=('LoL','Valorant'));selector.pack();root.update()
        control=VisibilidadCapri(root)
        try:
            for minimizar in (False,True):
                selector.abrir();root.update();popup=selector.popup
                self.assertEqual(root.grab_current(),popup)
                if minimizar:control.ocultar();root.update()
                control.mostrar();root.update()
                self.assertIsNone(selector.popup);self.assertIsNone(root.grab_current())
                self.assertFalse(popup.winfo_exists())
                selector.abrir();root.update();self.assertTrue(selector.popup.winfo_viewable())
                selector.cerrar_popup()
        finally:root.destroy()

    def test_juego_elegido_busca_desde_chat_con_valorant_en_segundo_plano(self):
        with self.capri() as (c,ruta),patch('escritorio.valorant_en_primer_plano',return_value=False),patch.object(c.valorant,'ejecutar',return_value='Listo') as valorant,patch.object(c.lol,'ejecutar',return_value='Listo') as lol:
            c.abrir_chat();c.juego_combo.current(2);c.juego_combo.event_generate('<<ComboboxSelected>>')
            c.panel.geometry('420x490');c.root.update()
            self.assertTrue(c.entrada.winfo_viewable())
            self.assertLess(c.entrada.winfo_rooty()+c.entrada.winfo_height(),c.panel.winfo_rooty()+c.panel.winfo_height()-15)
            self.assertEqual(c.cfg['juego_busqueda'],'valorant')
            c.enviar('busca partida');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(valorant.call_args.args[0],'valorant_buscar');lol.assert_not_called()
            c.enviar('busca partida en lol');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(lol.call_args.args[0],'lol_buscar')
            self.assertEqual(c.cfg['juego_busqueda'],'lol')
            c.enviar('busca partida en valorant');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(c.cfg['juego_busqueda'],'valorant');self.assertEqual(valorant.call_args.args[0],'valorant_buscar')
            for texto,tipo in (('pon la cola','valorant_buscar'),('sal de la cola','valorant_cancelar'),
                               ('tira partida','valorant_buscar'),('inicia la búsqueda','valorant_buscar'),
                               ('ponme en cola en Valorant','valorant_buscar'),('selecciona mi personaje','valorant_elegir')):
                c.enviar(texto);limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertEqual(valorant.call_args.args[0],tipo)

    def test_ajustes_y_menus_de_juego_tras_restaurar(self):
        from types import SimpleNamespace
        with self.capri() as (c,_),patch('ventanas.traer_al_frente',return_value=True):
            c.abrir_chat();c.root.update();c.minimizar_capri();c.root.update()
            c.visibilidad.mostrar();c.root.update()
            c.configurar();c.root.update();self.assertTrue(c.ajustes.winfo_viewable())
            c.ajustes.destroy()
            from lol_ui import PanelLoL
            from valorant_ui import PanelValorant
            for nombre,modulo,constructor,atributo in (('League of Legends','lol_ui.PanelLoL',PanelLoL,'lol_panel'),('Valorant','valorant_ui.PanelValorant',PanelValorant,'valorant_panel')):
                c.abrir_menu_radial(SimpleNamespace(x_root=800,y_root=500));c.root.update()
                radial=c.radial;radial.ejecutar(next(i for i,(n,_) in enumerate(radial.opciones) if n=='Más'))
                with patch(modulo,side_effect=lambda *a,**kw:constructor(*a,**kw,consultar=False)) as panel:
                    radial.ejecutar(next(i for i,(n,_) in enumerate(radial.opciones) if n==nombre))
                    panel.assert_called_once()
                self.assertIsNone(c.root.grab_current());self.assertIsNone(c.radial)
                c.root.update();juego=getattr(c,atributo)
                self.assertTrue(juego.ventana.winfo_viewable())
                self.assertTrue(juego.ventana.attributes('-topmost'))
                c.minimizar_capri();c.root.update();c.visibilidad.mostrar();c.root.update()
                self.assertFalse(juego.ventana.winfo_viewable())
                getattr(c,'abrir_lol' if atributo=='lol_panel' else 'abrir_valorant')()
                c.root.update();self.assertTrue(juego.ventana.winfo_viewable())
                juego.cerrar()

    def test_abrir_panel_selecciona_destino_y_no_inicia_partida(self):
        with self.capri() as (c,_),patch('valorant_ui.PanelValorant') as panel,patch.object(c.valorant,'ejecutar') as ejecutar:
            c.abrir_valorant();self.assertEqual(c.cfg['juego_busqueda'],'valorant')
            panel.assert_called_once();self.assertEqual(panel.call_args.kwargs['ocultar'],c.minimizar_capri)
            ejecutar.assert_not_called()

    def test_minimizada_sigue_ejecutando_ordenes_sin_reaparecer(self):
        with self.capri() as (c,_),patch.object(c.valorant,'ejecutar',return_value='Listo') as ejecutar:
            c.guardar('juego_busqueda','valorant');c.minimizar_capri();c.root.update()
            c.enviar('busca partida',origen='voz');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();c.root.update();time.sleep(.005)
            self.assertEqual(ejecutar.call_args.args[0],'valorant_buscar')
            self.assertTrue(c.visibilidad.oculta);self.assertEqual(c.root.state(),'withdrawn')

    def test_abrir_de_nuevo_recupera_avatar_sin_abrir_chat_ni_ocultarlo_en_otra_apertura(self):
        import os,uuid
        from instancia import InstanciaCapri
        if os.name!='nt':self.skipTest('Eventos locales de Windows')
        nombre='Local\\CapriVisibilidadPrueba-'+uuid.uuid4().hex
        with self.capri() as (c,_),InstanciaCapri(nombre) as receptor,InstanciaCapri(nombre) as emisor:
            c.instancia=receptor;c.minimizar_capri();c.root.update();antes=dict(c.cfg)
            self.assertTrue(c.visibilidad.oculta)
            for _ in range(2):
                emisor.solicitar_mostrar();c.poll();c.root.update()
                self.assertFalse(c.visibilidad.oculta);self.assertEqual(c.root.state(),'normal');self.assertIsNone(c.panel)
                self.assertEqual(c.cfg,antes)

    def test_orden_de_valorant_informa_error_del_controlador_sin_pedir_vision_a_la_ia(self):
        from valorant import MENSAJES
        with self.capri() as (c,_),patch.object(c.valorant,'ejecutar',return_value=MENSAJES['cliente']) as ejecutar,patch.object(c.ia,'conversar') as conversar,patch.object(c.interprete,'resolver') as resolver:
            c.cfg['ia']=True
            for frase in ('Capri, tira partida en Valorant','Capri, ponme en cola en Valorant'):
                c.enviar(frase,origen='voz');limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertEqual(ejecutar.call_args.args[0],'valorant_buscar')
                self.assertEqual(c.historial[-1],('Capri',MENSAJES['cliente']))
            conversar.assert_not_called();resolver.assert_not_called()
