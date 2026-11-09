import json,time
from unittest.mock import Mock,patch
from tema_ui import tk
from test_capri import PruebasTk
from counter_strike import ControlCS2
from counter_strike_ui import PanelCS2,TEXTOS


class Panel(PruebasTk):
    def test_mapa_guardado_filtro_y_acciones_sin_abrir_juego(self):
        r=tk.Tk();r.withdraw();guardar=Mock();enviar=Mock(return_value=False);c=ControlCS2()
        with patch('counter_strike_vision.VistaCS2') as vista:
            p=PanelCS2(r,{},guardar,enviar,c)
            try:
                r.update();vista.assert_not_called();self.assertEqual(p.config['mapas'],[])
                self.assertEqual(p.acciones['Buscar partida'].cget('state'),'disabled')
                p.tarjetas['Mirage'].command();p.tarjetas['Dust II'].command();self.assertEqual(p.config['mapas'],['Mirage','Dust II'])
                self.assertEqual(guardar.call_args.args,('cs2',p.config));enviar.assert_not_called()
                p.filtro.set('dust');r.update();self.assertEqual(set(p.tarjetas),{'Dust II'})
                self.assertEqual(p.limpiar(),'break');r.update();self.assertGreater(len(p.tarjetas),5)
                p.acciones['Aplicar mapas sin buscar'].invoke();self.assertEqual(enviar.call_args.args[0],'aplica mis mapas en cs2')
                self.assertEqual(p.ventana.state(),'normal');enviar.return_value=None;p.acciones['Buscar partida'].invoke();self.assertEqual(p.ventana.state(),'withdrawn')
                p.ventana.deiconify();p.ventana.geometry('680x540');r.update();self.assertEqual(p._columnas,2)
                c.estado='No pude leer todas las casillas de mapas. Deja completa la selección de Competitivo visible; no inicié la búsqueda.'
                p.ventana.after_cancel(p._after);p.refrescar();r.update();self.assertGreaterEqual(p.lista.winfo_height(),86)
                for t in TEXTOS:
                    from idiomas import catalogo
                    self.assertIn(t,catalogo())
            finally:p.cerrar();c.cerrar();r.destroy()

    def test_app_guarda_reabre_y_rutea_sin_confundir_lol(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,ruta),patch.object(c.cs2,'ejecutar',return_value='Listo') as ejecutar,patch.object(c.lol,'ejecutar',return_value='Listo') as lol,patch.object(c.ia,'conversar') as ia:
            c.abrir_cs2();p=c.cs2_panel;c.root.update();p.elegir('Mirage')
            self.assertEqual(json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['cs2']['mapas'],['Mirage'])
            for texto,tipo in (('busca partida en counter strike','cs2_buscar'),('cancela la cola','cs2_cancelar'),('aplica mis mapas en cs2','cs2_preparar'),('acepta la partida','cs2_aceptar')):
                c.enviar(texto);limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertEqual(ejecutar.call_args.args[0],tipo);self.assertFalse(c.ocupada)
            lol.assert_not_called();ia.assert_not_called()
            c.enviar('busca partida en lol');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(lol.call_args.args[0],'lol_buscar')
            c.minimizar_capri();c.abrir_cs2();c.root.update();self.assertIs(c.cs2_panel,p);self.assertEqual(p.ventana.state(),'normal')

    def test_voz_automatica_y_lectura_actualiza_panel(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.cs2,'ejecutar',return_value='Listo') as ejecutar,patch('escritorio.cs2_en_primer_plano',return_value=True),patch('escritorio.valorant_en_primer_plano',return_value=False),patch('escritorio.fortnite_en_primer_plano',return_value=False),patch('roblox_vision.en_primer_plano',return_value=False):
            c.guardar('juego_busqueda','auto');c.enviar('Capri, busca partida',origen='voz');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(ejecutar.call_args.args[0],'cs2_buscar')
            c.eventos.put(('cs2_mapas',(c.peticion-1,('Cache',))));c.poll();self.assertIsNone(c.cs2_panel)
            c.cs2.catalogo=('Mirage','Stronghold');c.eventos.put(('cs2_mapas',(c.peticion,c.cs2.catalogo)));c.poll();c.root.update()
            self.assertEqual(set(c.cs2_panel.tarjetas),{'Mirage','Stronghold'});self.assertEqual(c.cfg['cs2']['mapas'],[])


if __name__=='__main__':__import__('unittest').main()
