from unittest.mock import Mock,patch
from tema_ui import tk
from test_capri import PruebasTk
from fortnite_avisos_ui import AjustesAvisosFortnite,TEXTOS
from idiomas import catalogo,ui


class AvisosUI(PruebasTk):
    def test_todas_las_secciones_caben_en_el_tamano_minimo(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_):
            c.configurar();c.ajustes.geometry('720x560');c.ajustes.update();p=c.panel_ajustes
            for boton in p.botones.values():
                self.assertTrue(boton.winfo_ismapped());self.assertLessEqual(boton.winfo_y()+boton.winfo_height(),p.lateral.winfo_height())
            p.botones['Permisos'].invoke();c.root.update();self.assertEqual(p.actual,'Permisos')

    def test_opciones_sin_red_y_catalogo_completo(self):
        r=tk.Tk();r.withdraw();f=tk.Frame(r);f.pack();guardar=Mock();m=Mock()
        m.copia.return_value={'datos':{},'errores':{},'consultando':False,'actualizado':None}
        try:
            p=AjustesAvisosFortnite(f,{},guardar,m);r.update()
            self.assertFalse(any(v.get() for v in p.variables.values()));m.actualizar.assert_not_called()
            p.cambiar('fundador',True);p.cambiar('pavos',True)
            self.assertEqual(guardar.call_args.args,('fortnite_avisos',{'tienda':False,'pavos':True,'fundador':True}))
            p.boton.invoke();m.actualizar.assert_called_once()
            for t in TEXTOS:
                self.assertIn(t,catalogo())
                for idioma in ('en','pt','ja'):self.assertTrue(ui(t,idioma))
        finally:r.destroy()

    def test_app_guarda_opciones_y_avisos_esperan_la_conversacion(self):
        import test_companera_control as fixtures
        from test_fortnite_avisos import AHORA,misiones,html
        from fortnite_avisos import leer_misiones
        with fixtures.ModoPersonaje.capri(self) as (c,ruta):
            c.finalizar_intro();c.configurar();c.panel_ajustes.mostrar('Juegos');c.ajustes_juegos.mostrar('fortnite','Avisos');c.root.update()
            c.guardar('fortnite_avisos',{'pavos':True,'fundador':True});self.assertTrue(c.cfg['fortnite_avisos']['fundador'])
            self.assertIsNone(c.fortnite_avisos.hilo)
            c.ajustes.destroy();c.ajustes=None;c.skins_runtime=True;m=c.fortnite_avisos;m.reloj=lambda:AHORA.timestamp()
            m._preparar('pavos',leer_misiones(html(misiones()),AHORA),m.version)
            with patch.object(c,'ejemplo_skin',return_value=True) as decir:
                c.ocupada=True;c.mantener_skins_y_avisos();decir.assert_not_called();self.assertIsNotNone(m.siguiente())
                c.ocupada=False;c.mantener_skins_y_avisos();decir.assert_called_once();self.assertIsNone(m.siguiente())


if __name__=='__main__':__import__('unittest').main()
