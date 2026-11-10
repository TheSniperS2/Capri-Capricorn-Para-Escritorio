from unittest.mock import Mock,patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from confirmaciones_ui import ConfirmarCambio


class VentanasIndependientes(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_ajustes_playlist_y_confirmacion_pueden_moverse_sin_mover_ni_bloquear_las_otras(self):
        with self.capri() as (c,base),patch('playlists_ui.consultar_playlist',return_value=''):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;aplicar=Mock()
            p=ConfirmarCambio(c.ajustes,'Confirmar cambio','Prueba',aplicar,equipo={});c.root.update()
            ventanas=((c.ajustes,c.marco_ajustes),(d.ventana,d.marco),(p.ventana,p.marco))
            self.assertIsNone(c.root.grab_current())
            for v,marco in ventanas:
                v.focus_force();c.root.update()
                antes={str(w):(w.winfo_x(),w.winfo_y()) for w,_ in ventanas}
                x,y=v.winfo_rootx()+200,v.winfo_rooty()+22
                marco.canvas.event_generate('<ButtonPress-1>',x=200,y=22,rootx=x,rooty=y)
                marco.canvas.event_generate('<B1-Motion>',x=215,y=32,rootx=x+15,rooty=y+10,state=256)
                marco.canvas.event_generate('<ButtonRelease-1>',x=215,y=32,rootx=x+15,rooty=y+10)
                c.root.update()
                self.assertNotEqual((v.winfo_x(),v.winfo_y()),antes[str(v)])
                for otra,_ in ventanas:
                    if otra is not v:self.assertEqual((otra.winfo_x(),otra.winfo_y()),antes[str(otra)])
                self.assertIsNone(c.root.grab_current())
            aplicar.assert_not_called();p.cancelar();d.cerrar()
