import ctypes
from unittest.mock import Mock,patch
import unittest
from test_capri import PruebasTk
import test_companera_control as fixtures
from capturas_intro import captura_solicitada


class Detector(unittest.TestCase):
    def test_atajos_de_captura_no_consumen_teclas_ni_bloquean_windows(self):
        u=Mock()
        with patch('capturas_intro.os.name','nt'),patch('capturas_intro.ctypes.windll.user32',u):
            for teclas in ({0x2c},{0x5b,0x10,0x53},{0x5c,0x10,0x53}):
                u.GetAsyncKeyState.side_effect=lambda k:0x8000 if k in teclas else 0
                self.assertTrue(captura_solicitada())
            u.GetForegroundWindow.return_value=0
            u.GetAsyncKeyState.side_effect=lambda k:0x8000 if k in {0x10,0x53} else 0
            self.assertFalse(captura_solicitada())
            u.BlockInput.assert_not_called();u.RegisterHotKey.assert_not_called()

    def test_detecta_herramienta_ya_abierta_sin_atajo(self):
        u=Mock();u.GetAsyncKeyState.return_value=0;u.GetForegroundWindow.return_value=123
        def pid(hwnd,destino):ctypes.cast(destino,ctypes.POINTER(ctypes.c_ulong))[0]=456
        u.GetWindowThreadProcessId.side_effect=pid
        with patch('capturas_intro.os.name','nt'),patch('capturas_intro.ctypes.windll.user32',u),patch('capturas_intro.proceso_de_recortes',return_value=True) as proceso:
            self.assertTrue(captura_solicitada());proceso.assert_called_once_with(456)


class CapturaDeIntro(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_recorte_congela_el_cuadro_y_el_reloj_y_cede_la_capa(self):
        with self.capri() as (c,_):
            c.iniciar_intro();c.inicio_intro=100
            with patch.object(c.root,'after'),patch('app.time.monotonic',return_value=101):c.animar_intro()
            inicio=c.inicio_intro;anterior=bool(c.root.attributes('-topmost'))
            with patch('capturas_intro.captura_solicitada',return_value=True),patch.object(c.root,'after'),patch.object(c.bienvenida,'dibujar') as dibujar,patch.object(c.root,'focus_force') as foco:
                with patch('app.time.monotonic',return_value=102):c.animar_intro()
                self.assertFalse(bool(c.root.attributes('-topmost')))
                with patch('app.time.monotonic',return_value=110):c.animar_intro()
                dibujar.assert_not_called();foco.assert_not_called();self.assertEqual(c.inicio_intro,inicio)
                self.assertTrue(c.intro_activa)
            with patch('capturas_intro.captura_solicitada',return_value=False),patch.object(c.root,'after'),patch.object(c.bienvenida,'dibujar') as dibujar:
                with patch('app.time.monotonic',return_value=111):c.animar_intro()
                self.assertAlmostEqual(dibujar.call_args.args[1],2.)
                self.assertFalse(bool(c.root.attributes('-topmost')))
                self.assertTrue(hasattr(c,'intro_topmost_captura'))
                self.assertIsNone(c.intro_pausa_captura)
                c.finalizar_intro()
                self.assertEqual(bool(c.root.attributes('-topmost')),anterior)

    def test_cancelar_intro_restaura_la_capa_durante_un_recorte(self):
        with self.capri() as (c,_):
            c.iniciar_intro();anterior=bool(c.root.attributes('-topmost'))
            with patch('capturas_intro.captura_solicitada',return_value=True):
                self.assertTrue(c.pausar_intro_para_captura(200))
            c.finalizar_intro()
            self.assertFalse(c.intro_activa)
            self.assertFalse(hasattr(c,'intro_topmost_captura'))
            self.assertEqual(bool(c.root.attributes('-topmost')),anterior)

    def test_no_recupera_capa_sobre_vista_previa_tardia(self):
        with self.capri() as (c,_):
            c.iniciar_intro();c.inicio_intro=100
            with patch('capturas_intro.captura_solicitada',return_value=True):
                self.assertTrue(c.pausar_intro_para_captura(101))
            with patch('capturas_intro.captura_solicitada',return_value=False),patch.object(c.root,'attributes',wraps=c.root.attributes) as atributos:
                self.assertFalse(c.pausar_intro_para_captura(104))
                self.assertFalse(c.pausar_intro_para_captura(106))
                atributos.assert_not_called()
                self.assertTrue(hasattr(c,'intro_topmost_captura'))

    def test_despedida_deja_ver_recortes_sin_reiniciar_audio_o_cerrar_antes(self):
        with self.capri() as (c,_),patch.object(c.voz,'hablar') as voz,patch.object(c.root,'after'):
            c.cfg['voz']=False
            with patch('capturas_intro.captura_solicitada',return_value=True):c.iniciar_despedida()
            self.assertFalse(bool(c.root.attributes('-topmost')))
            self.assertTrue(hasattr(c,'intro_topmost_captura'))
            with patch('capturas_intro.captura_solicitada',return_value=False),patch.object(c.root,'attributes',wraps=c.root.attributes) as atributos:
                c.inicio_salida-=.4;c.pintar_despedida()
                atributos.assert_not_called();voz.assert_not_called()
                self.assertFalse(c.cerrado);self.assertTrue(c.saliendo)

    def test_cerrar_desde_intro_capturada_no_reimpone_la_ventana(self):
        with self.capri() as (c,_),patch.object(c.root,'after'):
            c.iniciar_intro()
            with patch('capturas_intro.captura_solicitada',return_value=True):c.pausar_intro_para_captura(200)
            with patch('capturas_intro.captura_solicitada',return_value=False),patch.object(c.root,'attributes',wraps=c.root.attributes) as atributos:
                c.iniciar_despedida()
                self.assertNotIn(('-topmost',True),[llamada.args for llamada in atributos.call_args_list])
                self.assertTrue(hasattr(c,'intro_topmost_captura'))
