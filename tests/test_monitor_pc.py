import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from test_capri import PruebasTk
from monitor_pc import uso_cpu, uso_gpu
from monitor_ui import PanelMonitor
from tema_ui import tk
import test_companera_control as fixtures


class Calculos(unittest.TestCase):
    def test_panel_de_animacion_incluye_recursos_sin_cambiar_imagen_del_avatar(self):
        from PIL import Image
        from avatar import panel_pantalla
        vista=Image.new('RGBA',(320,210),'#21d588')
        normal=panel_pantalla(vista,'visor',con_entrada=True)
        recursos=panel_pantalla(vista,'visor',con_entrada=True,monitor={'cpu':20,'ram':40,'gpu':10,'vram':1024**3})
        self.assertEqual(normal.size,(1080,1014));self.assertEqual(recursos.size,(1080,1146))
        foto=(60,165,1020,795)
        self.assertEqual(normal.crop(foto).tobytes(),recursos.crop(foto).tobytes())

    def test_cpu_kernel_incluye_tiempo_inactivo(self):
        self.assertIsNone(uso_cpu(None,(1,2,3)))
        self.assertAlmostEqual(uso_cpu((10,20,20),(30,70,70)),80)
        self.assertIsNone(uso_cpu((1,2,3),(1,2,3)))

    def test_gpu_suma_procesos_del_mismo_motor_y_toma_el_mas_ocupado(self):
        self.assertEqual(uso_gpu([
            ('pid_1_luid_0x0_0x123_phys_0_eng_0_engtype_3D',40),
            ('pid_2_luid_0x0_0x123_phys_0_eng_0_engtype_3D',30),
            ('pid_1_luid_0x0_0x123_phys_0_eng_1_engtype_Copy',55)]),70)
        self.assertIsNone(uso_gpu([]))
        self.assertIsNone(uso_gpu([('invalid',100)]))


class Panel(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_intro_y_ambas_transformaciones_incluyen_monitor_sin_tick_posterior(self):
        from avatar import tamano_panel
        from retrato_intro import plan_transicion
        with self.capri() as (a,_),patch.object(a.monitor_pc.monitor,'activar'),patch('intro.Transformacion') as transformar:
            transformar.return_value.fotos=[]
            a.root.deiconify();a.root.update_idletasks()
            a.cfg['monitor_pc']=True
            a.monitor_pc.monitor.datos={'cpu':25,'ram':40,'gpu':30,'vram':2*1024**3,'fecha':time.monotonic()}
            a.iniciar_intro();b=a.bienvenida
            self.assertEqual(b.destino_tamano,tamano_panel(1,True))
            centro=plan_transicion(b,1)['marco_centro']
            self.assertAlmostEqual(centro[0],b.fin[0]);self.assertAlmostEqual(centro[1],b.fin[1])
            self.assertFalse(a.monitor_pc.visible)
            a.inicio_intro=time.monotonic()-.34
            a.animar_intro()
            self.assertTrue(a.intro_monitor_actualizado)
            a.finalizar_intro();a.root.update_idletasks()
            self.assertTrue(a.monitor_pc.visible)
            self.assertEqual(a.root.winfo_height(),tamano_panel(1,True)[1])
            for modo in ('personaje','pantalla'):
                a.guardar('modo_visual',modo)
                panel=transformar.call_args.kwargs['panel']
                self.assertEqual(panel.size,(1080,1146))
                self.assertFalse(a.monitor_pc.visible)
                a.finalizar_transito();a.root.update_idletasks()
                self.assertEqual(a.monitor_pc.visible,modo=='pantalla')
            a.guardar('monitor_pc',False)
            a.iniciar_intro();self.assertEqual(a.bienvenida.destino_tamano,tamano_panel(1,False))
            a.finalizar_intro();self.assertFalse(a.monitor_pc.visible)

    def test_opcion_guardada_conserva_tamano_del_visor_y_no_crea_ventana_separada(self):
        with self.capri() as (a,ruta):
            a.root.deiconify();a.root.update()
            self.assertFalse(a.cfg['monitor_pc'])
            original=a.canvas.winfo_height()
            a.guardar('monitor_pc',True);a.root.update()
            self.assertTrue(a.monitor_pc.visible)
            self.assertTrue(a.entrada_compacta.unida)
            a.entrada_compacta.señal(.4,True,False)
            from disenos_pantalla import DISENOS
            for aspecto in DISENOS:
                a.guardar('aspecto_pantalla',aspecto);a.animar();a.root.update()
                a.entrada_compacta.señal(.5,False,True)
            orden=a.root.pack_slaves()
            self.assertLess(orden.index(a.canvas),orden.index(a.monitor_pc.marco))
            self.assertLess(orden.index(a.monitor_pc.marco),orden.index(a.entrada_compacta))
            self.assertEqual(a.canvas.winfo_height(),original-18)
            self.assertGreater(a.canvas.winfo_height(),265)
            self.assertEqual(a.monitor_pc.marco.winfo_toplevel(),a.root)
            a.guardar('escala_avatar',1.3);a.root.update()
            self.assertEqual(a.canvas.winfo_height(),round(274*1.3))
            a.guardar('monitor_pc',False);a.root.update()
            self.assertFalse(a.monitor_pc.visible)
            self.assertFalse(a.entrada_compacta.unida)
            self.assertEqual(a.canvas.winfo_height(),round(292*1.3))
            import json
            self.assertFalse(json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['monitor_pc'])

    def test_panel_sigue_visor_pausa_oculto_y_respeta_modo_intro_y_cierre(self):
        root=tk.Tk();root.geometry('360x338+120+300');root.update()
        a=SimpleNamespace(root=root,cfg={},escala_avatar=1,intro_activa=False,saliendo=False,
                          cerrado=False,transito=None,visibilidad=SimpleNamespace(oculta=False),
                          es_personaje=lambda:False,menu=lambda e:None,guardar=lambda k,v:a.cfg.update({k:v}),
                          _inicio_arrastre=lambda e:None,_arrastrar=lambda e:None)
        a.canvas=tk.Canvas(root,height=292);a.canvas.pack(fill='both',expand=True)
        from entrada import Entrada
        a.entrada_compacta=Entrada(root,lambda texto:None,lambda e:None);a.entrada_compacta.pack(fill='x')
        def escala():
            root.geometry(f'{round(360*a.escala_avatar)}x{round(292*a.escala_avatar)+46+(p.alto if p.visible else 0)}')
        a.aplicar_escala=escala
        with patch('monitor_ui.MonitorPC') as factory:
            monitor=factory.return_value
            monitor.datos={'cpu':35,'ram':50,'gpu':20,'vram':3*1024**3,'shared':1024**3,
                           'ram_used':8*1024**3,'ram_total':16*1024**3,'fecha':time.monotonic()}
            p=PanelMonitor(a)
            try:
                root.after_cancel(p.tarea);p.actualizar();root.update()
                self.assertFalse(p.visible);self.assertIsNone(p.marco)
                monitor.activar.assert_called_with(False)
                a.cfg['monitor_pc']=True;p.actualizar();root.update()
                self.assertTrue(p.visible)
                self.assertIs(p.marco.master,root)
                for tamano in (.75,1,1.6):
                    a.escala_avatar=tamano;p.ajustar();a.aplicar_escala();root.update()
                    self.assertLessEqual(p.canvas.winfo_width(),round(360*tamano))
                    for item in p.canvas.find_all():
                        if p.canvas.type(item)=='text':
                            box=p.canvas.bbox(item)
                            self.assertGreaterEqual(box[0],0)
                            self.assertLessEqual(box[2],p.canvas.winfo_width())
                antes=p.canvas.winfo_rootx();root.geometry('+230+300');root.update()
                # Sin esperar el temporizador ni llamar a actualizar/colocar.
                self.assertEqual(p.canvas.winfo_rootx()-antes,230-120)
                a.visibilidad.oculta=True;p.actualizar();self.assertFalse(p.visible)
                monitor.activar.assert_called_with(False)
                a.visibilidad.oculta=False;a.intro_activa=True;p.actualizar();self.assertFalse(p.visible)
                a.intro_activa=False;a.es_personaje=lambda:True;p.actualizar();self.assertFalse(p.visible)
                a.es_personaje=lambda:False;a.cfg['monitor_pc']=False;p.actualizar();self.assertFalse(p.visible)
                a.cfg['monitor_pc']=True;p.actualizar();self.assertTrue(p.visible)
                p.mostrar_tooltip(1);self.assertIsNotNone(p.tooltip)
                p.ocultar();self.assertIsNone(p.tooltip)
            finally:p.cerrar();root.destroy()
            monitor.cerrar.assert_called()


if __name__=='__main__':unittest.main()
