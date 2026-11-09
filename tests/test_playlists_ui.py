import json
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from playlists import cargar,vincular
from playlists_ui import TEXTOS


class PlaylistsUI(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_validar_guardar_y_confirmar_sin_reemplazar_otras_listas(self):
        with self.capri() as (c,base):
            vincular('Otra lista','spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV',base)
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.assertIs(d.ventana.grab_current(),d.ventana)
            d.guardar();self.assertTrue(d.estado.get());self.assertFalse(d.guardado)
            d.nombre.set('Capricorn');d.enlace.set('https://example.com/playlist/1234567890123456789012')
            d.guardar();self.assertTrue(d.estado.get());self.assertNotIn('capricorn',cargar(base))
            with patch.object(d.ventana,'clipboard_get',return_value='https://open.spotify.com/playlist/1234567890123456789012?si=prueba'):
                d.pegar()
            d.guardar();c.root.update()
            self.assertTrue(d.guardado);self.assertIn('Capricorn',d.frase.get())
            self.assertTrue(d.confirmacion.winfo_ismapped());self.assertFalse(d.formulario.winfo_ismapped())
            self.assertEqual(cargar(base),{'otra lista':'spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV','capricorn':'spotify:playlist:1234567890123456789012'})
            d.reiniciar();self.assertFalse(d.guardado);self.assertEqual(d.nombre.get(),'')
            d.cerrar();self.assertIsNone(c.root.grab_current())

    def test_cancelar_no_guarda_y_no_abre_dialogos_duplicados(self):
        with self.capri() as (c,base):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo
            c.vincular_playlist();self.assertIs(c.playlist_dialogo,d)
            d.nombre.set('Sin guardar');d.enlace.set('spotify:playlist:1234567890123456789012')
            d.cerrar();self.assertFalse((base/'playlists.json').exists())
            c.vincular_playlist();self.assertIsNot(c.playlist_dialogo,d)
            c.ajustes.destroy();self.assertTrue(c.playlist_dialogo.cerrado)
            self.assertIsNone(c.root.grab_current())
            from idiomas import catalogo
            for texto in TEXTOS:self.assertIn(texto,catalogo())
