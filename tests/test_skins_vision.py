from pathlib import Path
import time
import unittest
from unittest.mock import Mock,patch
from PIL import Image
from fortnite import ErrorFortnite,Texto
from skins_vision import VistaValorantSkins


class VisionSkins(unittest.TestCase):
    def test_lectura_valorant_no_roba_foco_ni_envia_entradas_y_limpia_temporal(self):
        v=VistaValorantSkins.__new__(VistaValorantSkins)
        v._ventana=Mock(return_value=123);v._activar=Mock();v._validar=Mock();v.a=Mock()
        v._imagen=Mock(return_value=(Image.new('RGB',(800,600)),(0,0,800,600),time.monotonic()))
        rutas=[]
        def leer(ruta):
            rutas.append(Path(ruta));self.assertTrue(Path(ruta).is_file())
            return (Texto('VANDAL',(300,100,200,35)),)
        with patch('skins_vision.leer_imagen',side_effect=leer):p=v.capturar()
        self.assertEqual(p.ventana,123);self.assertEqual(p.textos[0].texto,'VANDAL')
        v._activar.assert_not_called();v.a.mouse_event.assert_not_called();v.a.keybd_event.assert_not_called()
        self.assertFalse(rutas[0].exists())

    def test_fallo_de_lectura_limpia_temporal_e_informa_el_juego_correcto(self):
        v=VistaValorantSkins.__new__(VistaValorantSkins)
        v._ventana=Mock(return_value=123);v._activar=Mock(return_value=True)
        v._imagen=Mock(return_value=(Image.new('RGB',(800,600)),(0,0,800,600),time.monotonic()))
        rutas=[]
        def leer(ruta):
            rutas.append(Path(ruta));raise ErrorFortnite('No pude leer Fortnite.')
        with patch('skins_vision.leer_imagen',side_effect=leer):
            with self.assertRaisesRegex(ErrorFortnite,'No pude leer Valorant'):v.capturar(activar=True)
        self.assertFalse(rutas[0].exists());v._activar.assert_called_once_with(123)
        self.assertEqual(v.NOMBRES,{'valorant-win64-shipping.exe'})


if __name__=='__main__':unittest.main()
