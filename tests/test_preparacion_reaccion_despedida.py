import tempfile,time,threading
from pathlib import Path
from unittest.mock import Mock,patch
import tkinter as tk
from test_capri import PruebasTk
import test_companera_control as fixtures
from voz import Voz
from ventanas import apoyo_propio_permitido,registrar_apoyo,APOYOS_PROPIOS


class ReaccionYDespedida(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_preparacion_guarda_audio_sin_reproducir_y_hablar_no_repite_sintesis(self):
        peticiones=[]
        class Sintesis:
            def __init__(self,texto,nombre,**kw):peticiones.append(texto)
            async def stream(self):yield {'type':'audio','data':b'fixture audio'}
        v=Voz(Mock())
        with patch('edge_tts.Communicate',Sintesis),patch.object(v,'_reproducir_archivo',return_value=True) as reproducir:
            audio=v.preparar('Texto preparado.');self.assertTrue(audio.listo.wait(2))
            ruta=audio.archivo;self.assertTrue(ruta.exists());reproducir.assert_not_called()
            v.hablar('Texto preparado.',preparado=audio)
            limite=time.monotonic()+2
            while ruta.exists() and time.monotonic()<limite:time.sleep(.01)
            self.assertTrue(audio.cancelada);self.assertEqual(peticiones,['Texto preparado.'])
            reproducir.assert_called_once();self.assertFalse(ruta.exists())

    def test_comentario_se_prepara_desde_aviso_y_se_reproduce_desde_cache(self):
        original=tk.Toplevel
        class Oculta(original):
            def deiconify(self):pass
            def lift(self,*a):pass
        with self.capri() as (c,_),patch('llamadas.tk.Toplevel',Oculta),patch.object(c.voz,'hablar') as hablar,patch.object(c.voz,'preparar',return_value=Mock()) as preparar:
            c.cfg['voz']=True;c.llamar_capri(invitado='d')
            preparar.assert_called_once();hablar.assert_not_called();audio=c.audio_reaccion
            c.llamada_ui.aceptar();preparar.assert_called_once()
            c.revisar_interacciones();c.eventos.put(('voz',(c.voz.generacion,True)));c.poll()
            # Verificar el plazo con reloj fijo evita restas con redondeo binario en CI.
            with patch('app.time.monotonic',return_value=1234.):
                c.eventos.put(('voz',(c.voz.generacion,False)));c.poll()
            self.assertEqual(c.reaccion_pendiente[0],1234.+.24)
            c.reaccion_pendiente=(0,c.reaccion_pendiente[1]);c.revisar_interacciones()
            self.assertIs(hablar.call_args.kwargs['preparado'],audio);self.assertIsNone(c.audio_reaccion)

    def test_ajustes_publicos_no_exponen_simulaciones_ni_pruebas(self):
        with self.capri() as (c,_):
            with patch.object(c.micro,'probar') as grabar,patch.object(c.voz,'hablar') as hablar:
                c.configurar();textos=[]
                def recorrer(w):
                    texto=getattr(w,'texto',None)
                    if texto:textos.append(texto)
                    if 'text' in w.keys():textos.append(str(w.cget('text')))
                    for hijo in w.winfo_children():recorrer(hijo)
                recorrer(c.ajustes)
                for texto in ('Simular llamada','Simular asomo','Vista previa del apagado','Escuchar prueba','Grabar prueba · 5 s','Prueba de micrófono'):
                    self.assertNotIn(texto,textos)
                self.assertFalse(hasattr(c,'panel_prueba'))
                self.assertTrue(c.sensibilidad_microfono.winfo_exists())
                self.assertIn('Sensibilidad del micrófono',textos)
                self.assertIn('Llamadas ocasionales',textos)
                grabar.assert_not_called();hablar.assert_not_called()

    def test_propias_permitidas_excluyen_mascota_y_globo(self):
        for titulo in ('Capri · Ajustes','Capri // Aspectos','Capri · Conversación'):
            self.assertTrue(apoyo_propio_permitido(titulo))
        for titulo in ('Capri','Capri · Enlace','Tk','CAPRI CALL'):
            self.assertFalse(apoyo_propio_permitido(titulo))
        with self.capri() as (c,_),patch('companera.visibles',return_value=[]) as visibles:
            c.companera.refrescar(c.companera.ultimo+1);visibles.assert_called_once_with(incluir_propias=True)

    def test_despedida_habla_con_rostro_y_luego_forma_la_mano(self):
        from despedida import DURACION
        from despedida_camara import TRASLADO
        with self.capri() as (c,_),patch.object(c.voz,'hablar') as hablar,patch.object(c.voz,'preparar',return_value=Mock(archivo=Path('fixture.mp3'))) as preparar:
            preparar.return_value.listo.is_set.return_value=True
            c.cfg.update(voz=True,nombre_despedida='');c.iniciar_despedida();hablar.assert_not_called()
            self.assertEqual(float(c.root.attributes('-alpha')),1.)
            self.assertFalse(hasattr(c,'intro_alpha'))
            self.assertTrue(c.canvas.find_withtag('fragmento_viaje'))
            c.inicio_salida=time.monotonic()-TRASLADO*.5;c.pintar_despedida()
            hablar.assert_not_called();self.assertTrue(c.canvas.find_withtag('fragmento_viaje'))
            c.inicio_salida=time.monotonic()-TRASLADO-DURACION*.35;c.pintar_despedida()
            hablar.assert_called_once();self.assertEqual(hablar.call_args.args[0],'Cuídate mucho, choom.')
            self.assertTrue(c.canvas.find_withtag('rostro_despedida'))
            self.assertFalse(c.canvas.find_withtag('mano_despedida'))
            self.assertEqual(hablar.call_args.kwargs['perfil'],c.cfg.get('voz_perfil','capri'))
            c.inicio_salida=time.monotonic()-TRASLADO-DURACION*1.5;c.pintar_despedida()
            self.assertFalse(c.canvas.find_withtag('punta_estrella'));self.assertFalse(c.cerrado)
            c.eventos.put(('voz',(c.voz.generacion,True)));c.poll()
            c.eventos.put(('voz',(c.voz.generacion,False)));c.poll();c.pintar_despedida()
            self.assertTrue(c.salida_voz_terminada)
            c.salida_sonrisa_hasta=0
            c.salida_reanudar=time.monotonic()-DURACION*.5;c.pintar_despedida()
            self.assertTrue(c.canvas.find_withtag('mano_despedida'))
            c.salida_reanudar=time.monotonic()-DURACION*.82;c.pintar_despedida()
            self.assertTrue(c.canvas.find_withtag('punta_estrella'))

    def test_registro_de_apoyo_no_depende_del_idioma_y_se_retira_al_cerrar(self):
        import os
        if os.name!='nt':self.skipTest('Windows')
        root=tk.Tk();root.withdraw();v=tk.Toplevel(root);v.withdraw();v.title('Capri // Settings')
        try:
            antes=set(APOYOS_PROPIOS);registrar_apoyo(v)
            nuevos=APOYOS_PROPIOS-antes;self.assertEqual(len(nuevos),1)
            v.destroy();self.assertFalse(nuevos&APOYOS_PROPIOS)
        finally:root.destroy()
