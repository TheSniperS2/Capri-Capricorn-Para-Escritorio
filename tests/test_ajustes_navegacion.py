import json
import threading
from types import SimpleNamespace
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures


class AjustesNavegacion(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_lecturas_manuales_no_acumulan_ciclos_de_actualizacion(self):
        with self.capri() as (c,_):
            for _ in range(12):c.poll()
            pendientes=c.root.tk.splitlist(c.root.tk.call('after','info'))
            callbacks=[str(c.root.tk.call('after','info',identificador)[0]) for identificador in pendientes]
            self.assertEqual(sum(v.endswith('poll') for v in callbacks),1)

    def test_cinco_juegos_en_la_misma_ventana_y_volver_conserva_la_pagina(self):
        with self.capri() as (c,_),patch('lol_ui.PanelLoL._consultar'),patch('valorant_ui.PanelValorant._consultar'):
            c.configurar();c.panel_ajustes.mostrar('Juegos');ventana=c.ajustes
            cantidad=len(c.visibilidad.ventanas())
            for juego in ('lol','valorant','fortnite','cs2','roblox'):
                c.ajustes_juegos.mostrar(juego,'Partidas')
                c.botones_juegos[juego].invoke();c.root.update()
                panel=getattr(c,juego+'_panel')
                self.assertIs(c.ajustes,ventana);self.assertIs(panel.ventana.winfo_toplevel(),ventana)
                self.assertEqual(len(c.visibilidad.ventanas()),cantidad)
                self.assertTrue(panel.ventana.winfo_viewable())
                c.volver_juegos_boton.invoke();c.root.update()
                self.assertTrue(panel.cerrado)
                self.assertEqual(c.panel_ajustes.actual,'Juegos');self.assertEqual(c.ajustes_juegos.actual,juego)
                self.assertTrue(c.ajustes_base.winfo_ismapped())
            c.abrir_lol();panel=c.lol_panel
            c.root.update();antes=c.panel_ajustes.vistas['Juegos'][1].yview()
            panel.scroll.event_generate('<MouseWheel>',delta=-120);c.root.update()
            self.assertGreater(panel.scroll.yview()[0],0)
            self.assertEqual(c.panel_ajustes.vistas['Juegos'][1].yview(),antes)
            panel.abrir_selector('pick',0)
            self.assertEqual(str(panel.selector.transient()),str(c.ajustes))
            panel.selector.destroy()
            c.ajustes.destroy()
            self.assertTrue(panel.cerrado);self.assertTrue(panel._stop.is_set())
            c.configurar();c.root.update();self.assertTrue(c.ajustes.winfo_exists())

    def test_lol_construye_oculto_y_muestra_todos_los_picks_y_baneos_al_cambiar_de_vista(self):
        from lol_ui import PanelLoL
        from lol_seleccion import normalizar
        with self.capri() as (c,_),patch('lol_ui.PanelLoL._consultar'):
            c.configurar();c.root.update();config=normalizar({})
            config['roles']['TOP']['pick']=[86,103,61];config['roles']['TOP']['ban']=[53,157,25]
            c.cfg['lol_seleccion']=config
            def construir(*a,**kw):
                self.assertTrue(c.ajustes_base.winfo_ismapped())
                self.assertFalse(c.vista_juego.winfo_ismapped())
                p=PanelLoL(*a,**kw)
                self.assertTrue(c.ajustes_base.winfo_ismapped())
                self.assertFalse(c.vista_juego.winfo_ismapped())
                return p
            with patch('lol_ui.PanelLoL',side_effect=construir):c.abrir_lol()
            self.assertFalse(c.ajustes_base.winfo_ismapped());self.assertTrue(c.vista_juego.winfo_ismapped())
            for cv in c.lol_panel.slots.values():
                self.assertTrue(cv.find_all());self.assertIn('image',[cv.type(i) for i in cv.find_all()])

    def test_modelo_se_cambia_y_se_precarga_solo_al_confirmar(self):
        with self.capri() as (c,base),patch.object(c.ia,'modelos',return_value=['qwen:2b','llama:3b']):
            c.guardar('modelo','qwen:2b');c.configurar()
            c.modelo_combo.configure(values=('qwen:2b','llama:3b'))
            antes=(base/'ajustes.json').read_bytes();caliente=threading.Event()
            with patch.object(c,'preparar_ia',side_effect=caliente.set):
                c.elegir_modelo_ia('llama:3b')
                self.assertEqual(c.cfg['modelo'],'qwen:2b');self.assertFalse(caliente.is_set())
                c.confirmacion_ajustes.cancelar()
                self.assertEqual((base/'ajustes.json').read_bytes(),antes)
                c.elegir_modelo_ia('llama:3b');c.confirmacion_ajustes.aceptar()
                self.assertTrue(caliente.wait(1));self.assertEqual(c.cfg['modelo'],'llama:3b')
                self.assertEqual(json.loads((base/'ajustes.json').read_text(encoding='utf8'))['modelo'],'llama:3b')

    def test_reconocimiento_conserva_opciones_al_cancelar_y_aplica_al_confirmar(self):
        with self.capri() as (c,_):
            c.configurar()
            c.elegir_reconocimiento('rapido','base')
            self.assertEqual(c.cfg['reconocimiento'],'mixto')
            c.confirmacion_ajustes.cancelar();self.assertEqual(c.motor_reconocimiento_combo.current(),0)
            c.elegir_reconocimiento('rapido','base');c.confirmacion_ajustes.aceptar()
            self.assertEqual(c.cfg['reconocimiento'],'rapido')
            c.elegir_reconocimiento('mixto','small')
            self.assertEqual(c.cfg['modelo_whisper'],'base')
            c.confirmacion_ajustes.aceptar()
            self.assertEqual(c.cfg['modelo_whisper'],'small');self.assertEqual(c.micro.modelo_whisper,'small')
            self.assertEqual(c.cfg['reconocimiento'],'mixto')

    def test_instalacion_de_ia_no_se_abre_al_cancelar_y_bromas_antiguas_quedan_apagadas(self):
        with self.capri({'bromas_ventanas':True}) as (c,_),patch('app.subprocess.Popen') as abrir:
            self.assertFalse(c.cfg['bromas_ventanas'])
            c.configurar();c.activar_ia();abrir.assert_not_called()
            c.confirmacion_ajustes.cancelar();abrir.assert_not_called()
            c.activar_ia();c.confirmacion_ajustes.aceptar();abrir.assert_called_once()

    def test_redimensionar_desde_ambos_lados_respeta_minimo(self):
        with self.capri() as (c,_),patch('companera.area_trabajo',return_value=(0,0,1920,1080)):
            c.configurar();p=c.ajustes;p.geometry('800x740+100+100');p.update()
            marco=c.marco_ajustes
            marco.iniciar(SimpleNamespace(x=3,y=200,x_root=103,y_root=300))
            marco.mover(SimpleNamespace(x_root=2000,y_root=300));p.update()
            self.assertEqual(p.winfo_width(),720);self.assertEqual(p.winfo_x()+p.winfo_width(),900)
            marco.iniciar(SimpleNamespace(x=p.winfo_width()-2,y=200,x_root=898,y_root=300))
            marco.mover(SimpleNamespace(x_root=1100,y_root=300));p.update()
            self.assertGreater(p.winfo_width(),720)
