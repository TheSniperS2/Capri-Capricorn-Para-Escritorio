import json
import time
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from playlists import cargar,vincular
from playlists_ui import TEXTOS
from PIL import Image
from playlists_metadata import archivo_portada


class PlaylistsUI(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def setUp(self):
        super().setUp()
        self.metadata=patch('playlists_ui.consultar_playlist',return_value='');self.metadata.start()
        self.addCleanup(self.metadata.stop)

    def test_validar_guardar_y_confirmar_sin_reemplazar_otras_listas(self):
        with self.capri() as (c,base):
            vincular('Otra lista','spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV',base)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertIsNone(d.ventana.grab_current())
            d.guardar();self.assertTrue(d.estado.get());self.assertFalse(d.guardado)
            d.nombre.set('Capricorn');d.enlace.set('https://example.com/playlist/1234567890123456789012')
            d.guardar();self.assertTrue(d.estado.get());self.assertNotIn('capricorn',cargar(base))
            with patch.object(d.ventana,'clipboard_get',return_value='https://open.spotify.com/playlist/1234567890123456789012?si=prueba'):
                d.pegar()
            d.guardar();c.root.update()
            self.assertTrue(d.guardado);self.assertIn('Capricorn',d.frase.get())
            self.assertTrue(d.confirmacion.winfo_ismapped());self.assertTrue(d.formulario.winfo_ismapped())
            self.assertIn('capricorn',d.tarjetas)
            self.assertEqual(d.tarjetas['capricorn'].nombre.cget('text'),'Capricorn')
            self.assertEqual(cargar(base),{'otra lista':'spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV','capricorn':'spotify:playlist:1234567890123456789012'})
            d.reiniciar();self.assertFalse(d.guardado);self.assertEqual(d.nombre.get(),'')
            d.cerrar();self.assertIsNone(c.root.grab_current())

    def test_reabrir_recupera_nombre_elegido_y_permiso_de_editar_sin_perder_otras(self):
        with self.capri() as (c,base):
            vincular('Música de Noche','spotify:playlist:1234567890123456789012',base)
            vincular('Otra lista','spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV',base)
            c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertEqual(d.tarjetas['musica de noche'].nombre.cget('text'),'Música de Noche')
            d.editar('musica de noche');d.nombre.set('Para jugar');d.guardar();c.root.update()
            self.assertEqual(set(d.tarjetas),{'para jugar','otra lista'})
            d.cerrar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertEqual(d.tarjetas['para jugar'].nombre.cget('text'),'Para jugar')
            self.assertEqual(cargar(base)['para jugar'],'spotify:playlist:1234567890123456789012')

    def test_quitar_vinculo_requiere_el_boton_final_y_no_toca_otras_playlists(self):
        with self.capri() as (c,base):
            vincular('Noche','spotify:playlist:1234567890123456789012',base)
            vincular('Día','spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV',base)
            c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            d.confirmar_quitar('noche');c.root.update();self.assertIn('noche',cargar(base))
            d.pintar_guardadas();self.assertIn('noche',cargar(base))
            d.quitar('noche');c.root.update();self.assertEqual(set(cargar(base)),{'dia'})

    def test_error_de_guardado_conserva_formulario_y_archivo(self):
        with self.capri() as (c,base):
            vincular('Noche','spotify:playlist:1234567890123456789012',base)
            c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            antes=(base/'playlists.json').read_bytes()
            d.nombre.set('Otra');d.enlace.set('spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV')
            with patch('playlists.os.replace',side_effect=OSError('Sin espacio')):d.guardar()
            self.assertFalse(d.guardado);self.assertTrue(d.estado.get())
            self.assertEqual(d.nombre.get(),'Otra');self.assertEqual((base/'playlists.json').read_bytes(),antes)

    def test_campos_y_pegar_completos_en_compacto_y_una_lista_no_desplaza(self):
        with self.capri() as (c,base):
            vincular('Para jugar','spotify:playlist:1234567890123456789012',base)
            # Este caso verifica una tarjeta que cabe; la ayuda de portada
            # ausente puede necesitar scroll en pantallas más bajas.
            portada=archivo_portada('spotify:playlist:1234567890123456789012',base)
            portada.parent.mkdir(parents=True,exist_ok=True)
            Image.new('RGB',(88,88),'#6a2354').save(portada)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;d.ventana.geometry('820x680+40+40');c.root.update()
            self.assertEqual(d.lista.lienzo.yview(),(0.,1.));self.assertFalse(d.lista.barra.winfo_manager())
            self.assertGreater(d.entrada_enlace.winfo_width(),200)
            self.assertLessEqual(d.pegar_boton.winfo_rooty()+d.pegar_boton.winfo_height(),d.bordes['enlace'].winfo_rooty())
            for w in (d.boton_guardar,d.error):
                self.assertLessEqual(w.winfo_rooty()+w.winfo_height(),d.pie.winfo_rooty())
            d.filtro.set('no existe');c.root.update()
            self.assertEqual(d.tarjetas,{});self.assertEqual(d.lista.lienzo.yview(),(0.,1.))

    def test_titulo_en_segundo_plano_y_nombre_elegido_se_conservan_al_reabrir(self):
        with self.capri() as (c,base),patch('playlists_ui.consultar_playlist',return_value='ＮＩＧＨＴ ２０７７ ✨'):
            vincular('Para jugar','spotify:playlist:1234567890123456789012',base)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;limite=time.monotonic()+2
            while time.monotonic()<limite:
                c.root.update()
                if d.tarjetas['para jugar'].titulo.cget('text')=='ＮＩＧＨＴ ２０７７ ✨':break
                time.sleep(.02)
            self.assertEqual(d.tarjetas['para jugar'].titulo.cget('text'),'ＮＩＧＨＴ ２０７７ ✨')
            d.cerrar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertEqual(d.tarjetas['para jugar'].nombre.cget('text'),'Para jugar')
            self.assertEqual(d.tarjetas['para jugar'].titulo.cget('text'),'ＮＩＧＨＴ ２０７７ ✨')

    def test_una_tarjeta_larga_permite_llegar_a_sus_acciones_en_pantalla_baja(self):
        with self.capri() as (c,base),patch('ventanas.area_trabajo',return_value=(0,0,1024,720)):
            nombre='Una playlist con un nombre muy largo para comprobar toda su información '*2
            vincular(nombre,'spotify:playlist:1234567890123456789012',base)
            c.vincular_playlist();d=c.playlist_dialogo;d.ventana.geometry('840x620+24+24');c.root.update()
            self.assertGreater(d.lista.interior.winfo_reqheight(),d.lista.lienzo.winfo_height())
            self.assertTrue(d.lista.barra.winfo_manager())
            d.lista.lienzo.yview_moveto(1);c.root.update()
            self.assertEqual(d.lista.lienzo.yview()[1],1.)
            limite=d.lista.lienzo.winfo_rooty()+d.lista.lienzo.winfo_height()
            for boton in next(iter(d.tarjetas.values())).botones.values():
                self.assertLessEqual(boton.winfo_rooty()+boton.winfo_height(),limite)

    def test_clic_y_escritura_no_se_bloquean_al_refrescar_la_biblioteca(self):
        with self.capri() as (c,base):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertEqual(d.entrada_nombre.winfo_children(),[])
            d.bordes['nombre'].event_generate('<ButtonPress-1>',x=15,y=25);c.root.update()
            self.assertIs(d.ventana.focus_get(),d.entrada_nombre)
            for letra in 'capri':
                d.entrada_nombre.event_generate('<KeyPress-'+letra+'>');d.refrescar();c.root.update()
            self.assertEqual(d.nombre.get(),'capri')
            d.entrada_nombre.event_generate('<ButtonPress-1>',x=5,y=5);c.root.update()
            self.assertIs(d.ventana.focus_get(),d.entrada_nombre)

    def test_ctrl_v_pega_una_vez_y_respeta_la_seleccion_en_ambos_campos(self):
        with self.capri() as (c,base):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            enlace='https://open.spotify.com/playlist/1234567890123456789012'
            d.enlace.set('reemplazar');d.entrada_enlace.focus_force();d.entrada_enlace.selection_range(0,'end')
            with patch.object(d.entrada_enlace,'clipboard_get',return_value=enlace):
                d.entrada_enlace.event_generate('<Control-v>');c.root.update()
            self.assertEqual(d.enlace.get(),enlace)
            d.nombre.set('anterior');d.entrada_nombre.focus_force();d.entrada_nombre.selection_range(0,'end')
            with patch.object(d.entrada_nombre,'clipboard_get',return_value='Música de Noche'):
                d.entrada_nombre.event_generate('<<Paste>>');c.root.update()
            self.assertEqual(d.nombre.get(),'Música de Noche')

    def test_cancelar_no_guarda_y_no_abre_dialogos_duplicados(self):
        with self.capri() as (c,base):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo
            c.vincular_playlist();self.assertIs(c.playlist_dialogo,d)
            d.nombre.set('Sin guardar');d.enlace.set('spotify:playlist:1234567890123456789012')
            d.cerrar();self.assertFalse((base/'playlists.json').exists())
            c.vincular_playlist();self.assertIsNot(c.playlist_dialogo,d)
            c.ajustes.destroy();self.assertFalse(c.playlist_dialogo.cerrado)
            self.assertTrue(c.playlist_dialogo.ventana.winfo_exists())
            c.playlist_dialogo.nombre.set('Sigo abierta');c.root.update()
            self.assertEqual(c.playlist_dialogo.entrada_nombre.get(),'Sigo abierta')
            self.assertIsNone(c.root.grab_current())
            from idiomas import catalogo
            for texto in TEXTOS:self.assertTrue(texto in catalogo(),texto)

    def test_portada_privada_se_guarda_y_reaparece_sin_solicitar_una_captura_nueva(self):
        with self.capri() as (c,base):
            uri='spotify:playlist:1234567890123456789012';vincular('Noche',uri,base)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertIsNotNone(d.tarjetas['noche'].ayuda_portada)
            self.assertIn('pantallazo',d.tarjetas['noche'].ayuda_portada.cget('text'))
            with patch('portadas_ui.os.startfile'):
                d.capturar_portada(uri);c.root.update()
            d.captura.finalizar(Image.new('RGB',(200,200),'#123456'));c.root.update()
            self.assertTrue(archivo_portada(uri,base).is_file());self.assertIn(uri,d.fotos)
            self.assertTrue(d.ventana.winfo_viewable());self.assertEqual(float(d.ventana.attributes('-alpha')),1.)
            self.assertIsNone(c.root.grab_current());self.assertIsNone(d.tarjetas['noche'].ayuda_portada)
            d.cerrar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertIn(uri,d.fotos);self.assertIsNone(d.captura);self.assertIsNone(d.tarjetas['noche'].ayuda_portada)

    def test_cerrar_la_aplicacion_durante_captura_no_deja_ventanas_ni_callbacks(self):
        with self.capri() as (c,base):
            vincular('Noche','spotify:playlist:1234567890123456789012',base)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            with patch('portadas_ui.os.startfile'):d.capturar_portada(d.registros[0]['uri']);c.root.update()
            c.cerrar_inmediato();self.assertTrue(d.cerrado);self.assertTrue(d.captura.cerrado)

    def test_pantalla_baja_conserva_guardar_y_mensajes_en_todos_los_idiomas(self):
        from idiomas import activar,idioma_actual
        original=idioma_actual();self.addCleanup(lambda:activar(original))
        with self.capri() as (c,base):
            c.configurar();c.root.update()
            for lengua in ('es','en','pt','ja'):
                activar(lengua)
                with patch('ventanas.area_trabajo',return_value=(0,0,1280,680)):c.vincular_playlist()
                d=c.playlist_dialogo;d.nombre.set('Capri de noche');d.enlace.set('invalido');d.guardar();c.root.update()
                for w in (d.boton_guardar,d.error):
                    self.assertTrue(w.winfo_ismapped(),(lengua,str(w),d.ventana.geometry(),w.winfo_y(),w.winfo_reqheight(),d.formulario.winfo_reqheight(),d.pie.winfo_y()))
                    self.assertLessEqual(w.winfo_rooty()+w.winfo_height(),d.pie.winfo_rooty(),lengua)
                d.cerrar()
