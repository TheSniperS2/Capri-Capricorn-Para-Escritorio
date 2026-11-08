import json
import time
from unittest.mock import Mock,patch
from test_capri import PruebasTk
from tema_ui import tk
from fortnite import ControlFortnite,normalizar
from fortnite_ui import PanelFortnite,TEXTOS


class Panel(PruebasTk):
    def test_tarjetas_guardan_localmente_sin_abrir_juego_y_acciones_explicitas(self):
        root=tk.Tk();root.withdraw();guardar=Mock();enviar=Mock(return_value=False);control=ControlFortnite()
        with patch('fortnite_vision.VistaFortnite') as vista:
            p=PanelFortnite(root,{},guardar,enviar,control)
            try:
                root.update();vista.assert_not_called()
                for modo in ('br','cero','actual'):p.tarjetas['modo',modo].command()
                for equipo in ('solo','duo','trio','squad'):p.tarjetas['equipo',equipo].command()
                self.assertEqual(p.config,{'modo':'actual','equipo':'squad'})
                self.assertEqual(guardar.call_args.args,('fortnite',p.config));enviar.assert_not_called()
                for b in p.acciones.values():b.invoke()
                self.assertEqual([a.args[0] for a in enviar.call_args_list],['busca partida en fortnite','cancela la cola en fortnite','aplica mis opciones en fortnite'])
                self.assertEqual(p.ventana.state(),'normal')
                enviar.return_value=None;p.acciones['Buscar partida'].invoke();root.update()
                self.assertEqual(p.ventana.state(),'withdrawn')
                p.ventana.deiconify();p.ventana.geometry('680x560');root.update()
                self.assertGreater(p.scroll.bbox('all')[3],p.scroll.winfo_height())
                self.assertEqual(set(p.acciones),{'Buscar partida','Cancelar búsqueda','Aplicar en Fortnite'})
            finally:p.cerrar();control.cerrar();root.destroy()

    def test_textos_traducidos(self):
        from idiomas import ui,catalogo
        for texto in TEXTOS:
            self.assertIn(texto,catalogo())
            for idioma in ('en','pt','ja'):self.assertTrue(ui(texto,idioma).strip())

    def test_configuracion_app_y_reapertura_sin_ejecutar(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,ruta),patch.object(c.fortnite,'ejecutar') as ejecutar:
            c.abrir_fortnite();p=c.fortnite_panel;c.root.update()
            p.elegir('modo','cero');p.elegir('equipo','trio')
            self.assertEqual(c.fortnite.config,{'modo':'cero','equipo':'trio'})
            self.assertEqual(json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['fortnite'],c.fortnite.config)
            c.minimizar_capri();c.root.update();c.abrir_fortnite();c.root.update()
            self.assertIs(c.fortnite_panel,p);self.assertEqual(p.ventana.state(),'normal');ejecutar.assert_not_called()

    def test_ordenes_de_fortnite_y_lol_explicito_no_se_mezclan(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.fortnite,'ejecutar',return_value='Listo') as ejecutar,patch.object(c.lol,'ejecutar',return_value='Listo') as lol,patch('app.ejecutar') as generico,patch.object(c.ia,'conversar') as ia:
            for texto,tipo in (('busca partida en fortnite','fortnite_buscar'),('cancela la cola','fortnite_cancelar'),('aplica mis opciones en fortnite','fortnite_preparar')):
                c.enviar(texto);limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertFalse(c.ocupada);self.assertEqual(ejecutar.call_args.args[0],tipo)
            generico.assert_not_called();ia.assert_not_called()
            c.enviar('busca partida en lol');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(lol.call_args.args[0],'lol_buscar')

    def test_voz_en_fortnite_automatico_sin_chat_ni_selecciones_sobre_otros_juegos(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch('escritorio.fortnite_en_primer_plano',return_value=True),patch('escritorio.valorant_en_primer_plano',return_value=False),patch.object(c.fortnite,'ejecutar',return_value='Listo') as ejecutar,patch.object(c.valorant,'ejecutar',return_value='Listo') as valorant,patch.object(c,'abrir_chat') as abrir:
            c.guardar('juego_busqueda','auto');c.enviar('Capri, busca partida.',origen='voz');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(ejecutar.call_args.args[0],'fortnite_buscar');abrir.assert_not_called()
            c.enviar('busca partida en valorant',origen='voz');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(valorant.call_args.args[0],'valorant_buscar')


if __name__=='__main__':__import__('unittest').main()
