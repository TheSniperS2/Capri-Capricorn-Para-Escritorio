import io
import json
import unittest
from unittest.mock import patch
from cambios_modelos import comparar_modelos,parametros,TEXTOS
from idiomas import activar,catalogo
from core import IA


class CambiosModelos(unittest.TestCase):
    def setUp(self):activar('es')

    def test_compara_parametros_sin_asumir_que_llama_consume_mas_que_qwen(self):
        datos={'qwen:4b':{'details':{'parameter_size':'4.0B'}},
               'llama:3b':{'details':{'parameter_size':'3.2B'}}}
        self.assertIn('menos parámetros',comparar_modelos('qwen:4b','llama:3b',datos))
        self.assertIn('más parámetros',comparar_modelos('llama:3b','qwen:4b',datos))
        self.assertIn('no garantiza',comparar_modelos('sin datos','llama:3b',{}))
        self.assertIsNone(parametros({'details':None}))

    def test_catalogo_omite_modelos_remotos_y_conserva_metadata_para_la_alerta(self):
        modelos=[{'name':'local:2b','size':2000,'details':{'parameter_size':'2B'}},
                 {'name':'remote:3b','remote_host':'example.com'},
                 {'name':'cloud:latest'},None]
        respuesta=io.BytesIO(json.dumps({'models':modelos}).encode())
        with patch('core.urllib.request.urlopen',return_value=respuesta):
            ia=IA();self.assertEqual(ia.modelos(),['local:2b'])
        self.assertEqual(ia.detalles_modelos['local:2b']['details']['parameter_size'],'2B')

    def test_traducciones_de_las_confirmaciones(self):
        from confirmaciones_ui import TEXTOS as confirmaciones
        for texto in TEXTOS+confirmaciones:self.assertIn(texto,catalogo())
