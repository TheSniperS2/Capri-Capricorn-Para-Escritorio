import unittest
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from despedida_camara import GrabacionDespedida


class AperturaDespedida(unittest.TestCase):
    def test_boca_abierta_se_distingue_y_retoque_no_altera_resto_del_retrato(self):
        assets=Path(__file__).resolve().parents[1]/'assets'
        with Image.open(assets/'capri-despedida-expresiones-v11.png') as antes, Image.open(assets/'capri-despedida-expresiones-v12.png') as ahora:
            antes=antes.convert('RGB');ahora=ahora.convert('RGB')
            cambio=ImageChops.difference(antes,ahora)
            self.assertIsNotNone(cambio.getbbox())
            d=ImageDraw.Draw(cambio)
            for fila,col in ((0,0),(0,1),(1,0),(1,1)):
                d.rectangle((col*1672+700,fila*941+410,col*1672+1019,fila*941+649),fill=0)
            self.assertIsNone(cambio.getbbox())
            def superficie(col,fila):
                boca=ahora.crop((col*1672+770,fila*941+542,col*1672+925,fila*941+630))
                pixeles=boca.load()
                return sum(min(pixeles[x,y])>195 for y in range(boca.height) for x in range(boca.width))
            self.assertGreater(superficie(1,0),0)
            self.assertGreater(superficie(0,1),superficie(1,0)*6)
            self.assertGreater(superficie(1,1),superficie(1,0)*6)

    def test_apertura_sigue_audio_sin_intercalar_cierres_por_reloj_visual(self):
        cam=GrabacionDespedida.__new__(GrabacionDespedida)
        for t in (0,.14,.28,.44,.52,.58,.72,1.02):
            self.assertEqual(cam.expresion(t,True,True),2)
            self.assertEqual(cam.expresion(t,True,False),1)
        self.assertEqual(cam.expresion(.1,True,True,True),3)
