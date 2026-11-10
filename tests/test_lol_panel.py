import copy
import json
from unittest.mock import Mock,patch
from test_capri import PruebasTk
from tema_ui import tk
from lol_ui import PanelLoL,TEXTOS
from lol_seleccion import ControlSeleccion,normalizar
from league import ControlLoL


class Panel(PruebasTk):
    def test_perfiles_independientes_selector_busqueda_y_ordenes(self):
        from fuentes import cargar
        from pathlib import Path
        cargar(Path(__file__).resolve().parents[1])
        root=tk.Tk();root.withdraw();guardar=Mock();enviar=Mock();control=ControlLoL();seleccion=ControlSeleccion()
        with patch('lol_ui.ClienteLCU') as cliente:
            p=PanelLoL(root,{},guardar,enviar,control,seleccion,consultar=False)
            try:
                root.update();self.assertEqual(len(p.roles),5);self.assertEqual(len(p.slots),6)
                p.elegir_rol('MIDDLE');p.elegir('pick',0,103);p.elegir('pick',1,61)
                p.elegir_rol('TOP');self.assertEqual(p.config['roles']['TOP']['pick'],[0,0,0])
                p.elegir('pick',0,86);p.elegir_rol('MIDDLE');self.assertEqual(p.config['roles']['MIDDLE']['pick'],[103,61,0])
                p.elegir('pick',2,103);self.assertEqual(p.config['roles']['MIDDLE']['pick'],[0,61,103])
                self.assertFalse(p.config['auto_pick']);self.assertFalse(p.config['auto_ban'])
                persistido=json.loads(json.dumps(guardar.call_args.args[1]));self.assertEqual(persistido,p.config)
                p.abrir_selector('ban',0);p.busqueda.set('ahri');root.update()
                self.assertEqual(p.busqueda.get(),'ahri');self.assertTrue(p.selector.winfo_exists());p.selector.destroy()
                for b in p.acciones.values():b.invoke()
                self.assertEqual([c.args[0] for c in enviar.call_args_list],['busca partida en lol','busca partida en lol y acepta por mi','acepta partida en lol','cancela la cola en lol'])
                cliente.assert_not_called()
                p.ventana.geometry('850x670');root.update()
                self.assertGreater(p.scroll.bbox('all')[3],p.scroll.winfo_height())
                p.scroll.yview_moveto(1);root.update();self.assertGreater(p.scroll.yview()[0],0)
            finally:p.cerrar();root.destroy()

    def test_nuevos_textos_tienen_idiomas(self):
        from idiomas import ui,catalogo
        for texto in TEXTOS:
            for idioma in ('en','pt','ja'):
                with self.subTest(texto=texto,idioma=idioma):
                    self.assertIn(texto,catalogo());self.assertTrue(ui(texto,idioma).strip())

    def test_cambiar_una_prioridad_conserva_el_dibujo_de_las_otras_tarjetas(self):
        root=tk.Tk();root.withdraw()
        p=PanelLoL(root,{},Mock(),Mock(),ControlLoL(),ControlSeleccion(),consultar=False)
        try:
            root.update();antes={k:cv.find_all() for k,cv in p.slots.items()}
            self.assertTrue(all(antes.values()))
            p.elegir('pick',0,86);root.update()
            self.assertNotEqual(p.slots['pick',0].find_all(),antes['pick',0])
            for llave,cv in p.slots.items():
                if llave!=('pick',0):self.assertEqual(cv.find_all(),antes[llave])
        finally:p.cerrar();root.destroy()

    def test_app_guarda_perfiles_y_limpia_monitor_al_cerrar(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_):
            with patch.object(c.lol_seleccion,'configurar') as configurar:
                cfg=normalizar({});cfg['roles']['UTILITY']['ban']=[53,0,0]
                c.guardar('lol_seleccion',cfg)
                configurar.assert_called_once_with(cfg)
                self.assertEqual(json.loads((__import__('app').BASE/'ajustes.json').read_text(encoding='utf8'))['lol_seleccion'],cfg)


if __name__=='__main__':__import__('unittest').main()
