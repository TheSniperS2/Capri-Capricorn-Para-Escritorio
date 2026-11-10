import ctypes
from ctypes import wintypes as w
from types import SimpleNamespace
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from ventanas import hwnd_propio


class PintadoVentanas(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def opaca(self,v):
        u=ctypes.windll.user32
        u.GetWindowLongPtrW.argtypes=[w.HWND,ctypes.c_int];u.GetWindowLongPtrW.restype=ctypes.c_ssize_t
        self.assertEqual(v.attributes('-transparentcolor'),'')
        self.assertEqual(float(v.attributes('-alpha')),1.)
        self.assertFalse(u.GetWindowLongPtrW(hwnd_propio(v),-20)&0x80000)

    def test_cambios_de_juego_desde_tamano_pequeno_terminan_con_todas_las_tarjetas_y_ventana_opaca(self):
        with self.capri() as (c,_),patch('lol_ui.PanelLoL._consultar'),patch('valorant_ui.PanelValorant._consultar'):
            c.configurar();c.ajustes.geometry('720x560+40+40');c.root.update()
            for juego,n in (('lol',6),('valorant',3),('lol',6),('valorant',3)):
                c.abrir_juego_integrado(juego)
                # Comprobar al volver de abrir: un update del test ocultaba
                # la primera presentación con el tamaño de la vista anterior.
                rect=w.RECT();u=ctypes.windll.user32
                u.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
                self.assertTrue(u.GetWindowRect(hwnd_propio(c.ajustes),ctypes.byref(rect)))
                self.assertEqual((rect.right-rect.left,rect.bottom-rect.top),
                                 (c.ajustes.winfo_width(),c.ajustes.winfo_height()))
                p=getattr(c,juego+'_panel');slots=p.slots.values() if isinstance(p.slots,dict) else p.slots
                self.assertEqual(len(p.slots),n);self.assertTrue(all(cv.find_all() for cv in slots))
                self.assertTrue(c.vista_juego.winfo_viewable());self.opaca(c.ajustes)
            c.volver_de_juego();c.root.update();self.assertTrue(c.ajustes_base.winfo_viewable());self.opaca(c.ajustes)

    def test_contorno_nativo_se_adapta_al_redimensionar_y_spotify_no_depende_de_ajustes(self):
        u=ctypes.windll.user32;g=ctypes.windll.gdi32
        g.CreateRectRgn.argtypes=[ctypes.c_int]*4;g.CreateRectRgn.restype=w.HRGN
        u.GetWindowRgn.argtypes=[w.HWND,w.HRGN];g.PtInRegion.argtypes=[w.HRGN,ctypes.c_int,ctypes.c_int]
        g.DeleteObject.argtypes=[w.HGDIOBJ]
        with self.capri() as (c,base),patch('playlists_ui.consultar_playlist',return_value=''):
            c.configurar();c.vincular_playlist();d=c.playlist_dialogo;c.root.update()
            self.opaca(d.ventana)
            for ancho,alto in ((1060,780),(840,700),(980,760)):
                d.ventana.geometry(f'{ancho}x{alto}+40+40');c.root.update();r=g.CreateRectRgn(0,0,0,0)
                try:
                    self.assertGreater(u.GetWindowRgn(hwnd_propio(d.ventana),r),0)
                    self.assertFalse(g.PtInRegion(r,0,0));self.assertTrue(g.PtInRegion(r,ancho//2,alto//2))
                    self.assertTrue(g.PtInRegion(r,ancho-3,alto//2))
                finally:g.DeleteObject(r)
            c.ajustes.destroy();c.root.update();self.assertTrue(d.ventana.winfo_viewable())
            c.vincular_playlist();self.assertIs(c.playlist_dialogo,d);self.opaca(d.ventana)

    def test_menu_mas_abre_el_mismo_panel_spotify_sin_necesitar_ajustes(self):
        with self.capri() as (c,_),patch('playlists_ui.consultar_playlist',return_value=''):
            with patch('menu_radial.MenuRadial') as menu:
                c.abrir_menu_radial(SimpleNamespace(x_root=300,y_root=300))
                opciones=menu.call_args.args[3];mas=dict(opciones)['Más']
                dict(mas)['Playlists de Spotify']()
            d=c.playlist_dialogo;self.assertTrue(d.ventana.winfo_exists());self.assertIsNone(c.ajustes)
