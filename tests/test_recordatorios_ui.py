import datetime
import time
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from recordatorios import agregar
from idiomas import catalogo
from recordatorios_ui import TEXTOS


class AgendaUI(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_crear_por_horas_y_cancelar_conserva_los_otros_avisos(self):
        with self.capri() as (c,_):
            ahora=time.time();c.guardar('recordatorios',agregar([],'Otro aviso',30,ahora=ahora))
            c.abrir_recordatorios();p=c.recordatorios_panel;c.root.update()
            p.texto.insert('1.0','Estirar las piernas')
            p.elegir_plazo(60)
            with patch('recordatorios.time.time',return_value=ahora):p.crear()
            filas=c.cfg['recordatorios']
            self.assertEqual(len(filas),2)
            nuevo=next(r for r in filas if r['texto']=='Estirar las piernas')
            self.assertEqual(nuevo['vence'],ahora+3600)
            self.assertEqual(p.texto.get('1.0','end-1c'),'')
            p.cancelar(nuevo['id'])
            self.assertEqual([r['texto'] for r in c.cfg['recordatorios']],['Otro aviso'])

    def test_estado_vacio_validacion_y_contenido_del_usuario_en_otro_idioma(self):
        with self.capri() as (c,_):
            c.abrir_recordatorios();p=c.recordatorios_panel;c.root.update()
            self.assertTrue(p.vacio.winfo_ismapped())
            p.crear();self.assertEqual(c.cfg['recordatorios'],[]);self.assertTrue(p.estado.get())
            p.texto.insert('1.0','Recordatorios');p.minutos.delete(0,'end');p.minutos.insert(0,'0')
            p.crear();self.assertEqual(c.cfg['recordatorios'],[])
            p.elegir_plazo(5);p.crear();c.guardar('idioma','en');p.refrescar_datos();c.root.update()
            self.assertFalse(p.vacio.winfo_ismapped())
            def etiquetas(w):
                for h in w.winfo_children():
                    if getattr(h,'_capri_contenido_usuario',False):yield h
                    yield from etiquetas(h)
            self.assertEqual([w.cget('text') for w in etiquetas(p.lista)],['Recordatorios'])
            for texto in TEXTOS:self.assertIn(texto,catalogo())

    def test_muchas_tarjetas_tienen_scroll_y_el_formulario_cabe_en_el_minimo(self):
        with self.capri() as (c,_):
            filas=[]
            for i in range(12):filas=agregar(filas,'Un aviso suficientemente largo para comprobar el ajuste del texto '+str(i),5+i*90)
            c.guardar('recordatorios',filas);c.abrir_recordatorios();p=c.recordatorios_panel
            p.ventana.geometry('720x660');c.root.update()
            self.assertEqual(len(p.tarjetas),12)
            p.lista.mover(4);c.root.update()
            self.assertGreater(p.lista.lienzo.yview()[0],0)
            self.assertTrue(p.boton_crear.winfo_ismapped())
            self.assertTrue(p.etiqueta_estado.winfo_ismapped())
            self.assertLessEqual(p.boton_crear.winfo_rooty()+p.boton_crear.winfo_height(),p.ventana.winfo_rooty()+p.ventana.winfo_height()-20)
            p.cerrar();self.assertIsNone(p._after)
