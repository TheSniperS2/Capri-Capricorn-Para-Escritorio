from pathlib import Path
import time
import unittest
from unittest.mock import Mock,patch
from PIL import Image
from fortnite import ErrorFortnite,Texto
from skins_vision import VistaValorantSkins


class VisionSkins(unittest.TestCase):
    def test_4k_conserva_coordenadas_y_detalle_no_elimina_contexto(self):
        from fortnite import Pantalla
        from skins_vision import VistaSkins
        v=VistaSkins.__new__(VistaSkins);v._ventana=Mock(return_value=123);v._validar=Mock()
        im=Image.new('RGB',(3840,2160));v._imagen=Mock(return_value=(im,(0,0,3840,2160),time.monotonic()))
        def ocr(ruta):
            with Image.open(ruta) as i:self.assertLessEqual(max(i.size),2500)
            return (Texto('ATUENDO',(100,100,200,30)),)
        with patch('skins_vision.leer_imagen',side_effect=ocr):
            p=v.capturar();self.assertAlmostEqual(p.textos[0].rect[0],153.6)
            v.regiones_ficha=Mock(return_value=[(0,0,500,500)])
            p=Pantalla(123,(0,0,3840,2160),(*p.textos,Texto('EDITAR ESTILO',(3000,1900,300,30))),p.momento)
            with patch('PIL.ImageGrab.grab',return_value=im):detalle=v.leer_ficha(p)
        self.assertIn('EDITAR ESTILO',[t.texto for t in detalle.textos])
        v._validar.side_effect=ErrorFortnite('Foco perdido')
        with self.assertRaises(ErrorFortnite):v.leer_ficha(p)

    def test_cache_visual_se_invalida_al_cambiar_nombre_y_cada_cuatro_segundos(self):
        v=VistaValorantSkins.__new__(VistaValorantSkins)
        v._ventana=Mock(return_value=123);v._validar=Mock();v.a=Mock()
        im=Image.new('RGB',(800,600));v._imagen=Mock(side_effect=lambda *a,**k:(im,(0,0,800,600),time.monotonic()))
        with patch('skins_vision.leer_imagen',return_value=(Texto('Nombre',(20,400,100,30)),)) as ocr:
            v.capturar();v.capturar();self.assertEqual(ocr.call_count,1)
            im.putpixel((20,400),(255,255,255));v.capturar();self.assertEqual(ocr.call_count,2)
            v._leida-=5;v.capturar();self.assertEqual(ocr.call_count,3)

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
