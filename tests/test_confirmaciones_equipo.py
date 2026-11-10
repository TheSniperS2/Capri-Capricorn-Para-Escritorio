import threading
import time
import unittest
from unittest.mock import patch
from cambios_modelos import GIB,informe_modelo,informe_reconocimiento,informe_activacion
from idiomas import activar
from test_capri import PruebasTk
from tema_ui import tk
from confirmaciones_ui import ConfirmarCambio


class RecomendacionesEquipo(unittest.TestCase):
    def setUp(self):
        activar('es')
        self.modelos={'pequeno':{'size':1.5*GIB,'details':{'parameter_size':'2B'}},
                      'grande':{'size':5*GIB,'details':{'parameter_size':'8B'}}}
        self.amplio=dict(cpu='CPU de prueba',hilos=16,ram_total=32*GIB,ram_libre=24*GIB,gpus=[])

    def test_el_mismo_cambio_se_recomienda_o_desaconseja_segun_la_ram(self):
        bueno=informe_modelo('pequeno','grande',self.modelos,self.amplio)
        limitado=informe_modelo('pequeno','grande',self.modelos,dict(self.amplio,ram_total=4*GIB,ram_libre=GIB))
        ocupado=informe_modelo('pequeno','grande',self.modelos,dict(self.amplio,ram_libre=GIB))
        self.assertEqual(bueno['estado'],'recomendado');self.assertEqual(limitado['estado'],'limitado')
        self.assertEqual(ocupado['estado'],'precaucion');self.assertIn('ahora',ocupado['titulo'])
        self.assertIn('complejas',bueno['ganas']);self.assertIn('más memoria',bueno['coste'])

    def test_no_deduce_memoria_del_nombre_ni_suma_vram_de_varias_tarjetas(self):
        sin=informe_modelo('x','llama:200b',{},self.amplio)
        self.assertEqual(sin['estado'],'desconocido')
        e=dict(self.amplio,ram_total=4*GIB,ram_libre=GIB,gpus=[{'dedicada':6*GIB},{'dedicada':6*GIB}])
        self.assertEqual(informe_modelo('pequeno','grande',self.modelos,e)['estado'],'limitado')
        potente=informe_modelo('pequeno','grande',self.modelos,dict(e,gpus=[{'dedicada':24*GIB}]))
        self.assertEqual(potente['estado'],'precaucion');self.assertIn('24.0',potente['recomendacion'])
        self.assertIn('No confirmé',potente['recomendacion'])
        self.assertEqual(informe_modelo('pequeno','grande',self.modelos,{})['estado'],'desconocido')

    def test_modelo_menor_explicita_beneficio_y_coste_sin_promesa_de_calidad(self):
        informe=informe_modelo('grande','pequeno',self.modelos,self.amplio)
        self.assertEqual(informe['estado'],'recomendado')
        self.assertIn('responder antes',informe['ganas']);self.assertIn('perder detalle',informe['coste'])
        self.assertIn('cuantización',informe['nota'])

    def test_small_en_cpu_no_se_acelera_por_tener_una_gpu_potente(self):
        lento=dict(self.amplio,hilos=2,gpus=[{'nombre':'GPU potente','dedicada':24*GIB}])
        informe=informe_reconocimiento('mixto','base','mixto','small',lento)
        self.assertEqual(informe['estado'],'precaucion');self.assertIn('CPU',informe['coste'])
        self.assertIn('GPU no lo acelera',informe['detalle']);self.assertIn('Base',informe['recomendacion'])
        self.assertEqual(informe_reconocimiento('mixto','base','mixto','small',self.amplio)['estado'],'recomendado')

    def test_vosk_es_la_alternativa_ligera_incluso_con_pocos_recursos(self):
        e=dict(self.amplio,hilos=2,ram_total=2*GIB,ram_libre=.8*GIB)
        informe=informe_reconocimiento('mixto','small','rapido','base',e)
        self.assertIn('más ligera',informe['titulo']);self.assertIn('fallar',informe['coste'])
        sin_cpu=informe_reconocimiento('rapido','base','mixto','base',dict(self.amplio,hilos=None))
        self.assertNotEqual(sin_cpu['estado'],'recomendado');self.assertIn('No pude leer',sin_cpu['recomendacion'])

    def test_activar_no_es_una_promesa_de_que_cualquier_modelo_funcione(self):
        informe=informe_activacion(self.amplio)
        self.assertEqual(informe['estado'],'recomendado');self.assertIn('general',informe['nota'])

    def test_los_informes_se_traducen_sin_cambiar_el_hardware_ni_el_veredicto(self):
        original=informe_modelo('pequeno','grande',self.modelos,self.amplio)
        try:
            for idioma in ('en','pt','ja'):
                activar(idioma);traducido=informe_modelo('pequeno','grande',self.modelos,self.amplio)
                self.assertEqual(traducido['estado'],original['estado'])
                for campo in ('titulo','recomendacion','ganas','coste','detalle','nota','resumen','consejo_breve'):
                    with self.subTest(idioma=idioma,campo=campo):self.assertNotEqual(traducido[campo],original[campo])
        finally:activar('es')

    def test_resumen_corto_distingue_la_direccion_del_cambio(self):
        pequeno=informe_modelo('grande','pequeno',self.modelos,self.amplio)
        grande=informe_modelo('pequeno','grande',self.modelos,self.amplio)
        small=informe_reconocimiento('mixto','base','mixto','small',self.amplio)
        base=informe_reconocimiento('mixto','small','mixto','base',self.amplio)
        self.assertIn('más rápido',pequeno['resumen']);self.assertIn('menos detalle',pequeno['resumen'])
        self.assertIn('más completas',grande['resumen']);self.assertIn('más espera',grande['resumen'])
        self.assertIn('mejor',small['resumen']);self.assertIn('tarda más',small['resumen'])
        self.assertIn('más rápido',base['resumen']);self.assertIn('menos de precisión',base['resumen'])
        for informe in (pequeno,grande,small,base,informe_activacion(self.amplio)):
            self.assertLess(len(informe['resumen']),100);self.assertLess(len(informe['consejo_breve']),90)


class ConfirmacionEquipoUI(PruebasTk):
    def setUp(self):
        super().setUp();activar('es')
        self.root=tk.Tk();self.root.withdraw();self.padre=tk.Toplevel(self.root);self.padre.geometry('800x740+30+30');self.root.update()
        self.equipo=dict(cpu='Procesador de prueba',hilos=8,ram_total=16*GIB,ram_libre=10*GIB,
                        gpus=[{'nombre':'Tarjeta de 12 GB','dedicada':12*GIB},{'nombre':'Integrada','dedicada':128*1024**2}])
    def tearDown(self):self.root.destroy();super().tearDown()

    def crear(self,**kw):
        return ConfirmarCambio(self.padre,'Cambiar reconocimiento de voz','',kw.pop('aceptar',lambda:None),
            actual='Whisper Base',nuevo='Whisper Small',
            evaluar=lambda e:informe_reconocimiento('mixto','base','mixto','small',e),**kw)

    def test_dialogo_corto_muestra_efecto_y_consejo_sin_ficha_tecnica(self):
        p=self.crear(equipo=self.equipo);self.root.update()
        self.assertTrue(p.analisis_listo);self.assertEqual(p.informe['estado'],'recomendado')
        self.assertIn('tarda más',p.resumen.cget('text'));self.assertIn('Puedes cambiar',p.consejo.cget('text'))
        self.assertFalse(hasattr(p,'recursos'));self.assertFalse(hasattr(p,'detalle'))
        self.assertFalse(hasattr(p,'scroll'))
        self.assertLessEqual(p.ventana.winfo_height(),520)
        for boton in (p.boton_cancelar,p.boton_aceptar):
            self.assertTrue(boton.winfo_ismapped())
            self.assertLess(boton.winfo_rooty()+boton.winfo_height(),p.ventana.winfo_rooty()+p.ventana.winfo_height())
        for etiqueta in (p.resumen,p.consejo):
            self.assertGreaterEqual(etiqueta.winfo_rooty(),p.contenido.winfo_rooty())
            self.assertLessEqual(etiqueta.winfo_rooty()+etiqueta.winfo_height(),p.pie.winfo_rooty())
        p.cancelar()

    def test_la_altura_crece_y_disminuye_con_el_texto_sin_desplazarlo(self):
        p=self.crear(equipo=self.equipo);self.root.update();corto=p.ventana.winfo_height()
        informe=dict(p.informe)
        p.evaluar=lambda e:dict(informe,resumen='Más precisión, pero más espera. '*12)
        p.mostrar_analisis(self.equipo);self.root.update()
        self.assertGreater(p.ventana.winfo_height(),corto)
        for etiqueta in (p.resumen,p.consejo):
            self.assertEqual(etiqueta.winfo_height(),etiqueta.winfo_reqheight())
            self.assertLessEqual(etiqueta.winfo_rooty()+etiqueta.winfo_height(),p.pie.winfo_rooty())
        antes=p.resumen.winfo_rooty();p.resumen.event_generate('<MouseWheel>',delta=-120);self.root.update()
        self.assertEqual(p.resumen.winfo_rooty(),antes)
        p.evaluar=lambda e:informe;p.mostrar_analisis(self.equipo);self.root.update()
        self.assertEqual(p.ventana.winfo_height(),corto);p.cancelar()

    def test_refluye_en_pantalla_baja_y_mantiene_las_acciones_visibles(self):
        with patch('ventanas.area_trabajo',return_value=(0,0,1280,720)):
            p=self.crear(equipo=self.equipo);base=dict(p.informe)
            p.evaluar=lambda e:dict(base,resumen='Más precisión, pero más espera. '*35)
            p.mostrar_analisis(self.equipo);self.root.update()
            self.assertGreater(p.ventana.winfo_width(),680)
            self.assertLessEqual(p.ventana.winfo_y()+p.ventana.winfo_height(),704)
            self.assertEqual(p.resumen.winfo_height(),p.resumen.winfo_reqheight())
            for boton in (p.boton_cancelar,p.boton_aceptar):
                self.assertTrue(boton.winfo_ismapped())
                self.assertLess(boton.winfo_rooty()+boton.winfo_height(),p.ventana.winfo_y()+p.ventana.winfo_height())
            p.cancelar();self.assertIsNone(p._tarea_tamano)

    def test_cancelar_es_idempotente_y_no_aplica_aunque_llegue_lectura_tarde(self):
        liberar=threading.Event();aplicados=[]
        with patch('equipo_pc.leer_equipo',side_effect=lambda:(liberar.wait(1),self.equipo)[1]):
            p=self.crear(aceptar=lambda:aplicados.append(True))
            self.assertEqual(p.boton_aceptar.cget('state'),'disabled')
            p.cancelar();p.cancelar();liberar.set();self.root.update()
            self.assertEqual(aplicados,[]);self.assertIsNone(p._tarea)

    def test_error_de_lectura_muestra_incertidumbre_y_deja_decidir(self):
        with patch('equipo_pc.leer_equipo',side_effect=OSError('No disponible')):
            p=self.crear();limite=time.monotonic()+2
            while not p.analisis_listo and time.monotonic()<limite:self.root.update();time.sleep(.02)
            self.assertEqual(p.informe['estado'],'desconocido')
            self.assertEqual(p.boton_aceptar.cget('state'),'normal')
            self.assertIn('No pude comprobar',p.consejo.cget('text'));p.cancelar()

    def test_confirmar_aplica_solo_una_vez_y_esc_cancela(self):
        aplicados=[];p=self.crear(equipo=self.equipo,aceptar=lambda:aplicados.append(True))
        p.boton_aceptar.invoke();p.aceptar();self.assertEqual(aplicados,[True])
        p=self.crear(equipo=self.equipo,aceptar=lambda:aplicados.append(True))
        p.boton_cancelar.focus_force();self.root.update()
        p.boton_cancelar.event_generate('<Escape>');self.root.update()
        self.assertTrue(p.cerrado);self.assertEqual(aplicados,[True])

    def test_releer_memoria_actualiza_el_consejo_sin_aplicar_el_cambio(self):
        aplicados=[];p=self.crear(equipo=self.equipo,aceptar=lambda:aplicados.append(True))
        poco=dict(self.equipo,ram_libre=.2*GIB)
        with patch('equipo_pc.leer_equipo',return_value=poco):
            p.boton_releer.invoke();limite=time.monotonic()+2
            while not p.analisis_listo and time.monotonic()<limite:self.root.update();time.sleep(.02)
        self.assertEqual(p.informe['estado'],'precaucion')
        self.assertEqual(p.equipo['ram_libre'],poco['ram_libre'])
        self.assertIn('Cierra otras aplicaciones',p.consejo.cget('text'))
        self.assertEqual(aplicados,[]);p.cancelar()
