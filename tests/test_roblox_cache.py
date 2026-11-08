import json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from roblox import ClientePublico,ControlRoblox,agregar_favorito,ErrorRoblox
from roblox_cache import CacheRoblox

def info(lugar='123'):
    return {'lugar':lugar,'universo':'456','nombre':'The Maze','descripcion':'A horror game','genero':'Survival',
            'subgenero':'Escape','genero_original':'Adventure','creador':'Creador','perfil':'terror'}

class Cache(unittest.TestCase):
    def test_datos_e_iconos_sobreviven_a_otro_cliente_sin_consultas(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=ClientePublico(tmp);im=Image.new('RGB',(150,150),'red')
            with patch.object(c,'_consultar_lugar',return_value=info()) as red,patch.object(c,'json',return_value={}),patch.object(c,'_imagen_miniatura',return_value=im):
                c.detalles_lugar('123');c.icono_experiencia('456')
            otro=ClientePublico(tmp)
            with patch.object(otro,'json',side_effect=AssertionError('No debe ir a la red')),patch.object(otro,'_consultar_lugar',side_effect=AssertionError('No debe consultar detalles')):
                self.assertEqual(otro.detalles_lugar('123')['nombre'],'The Maze')
                self.assertEqual(otro.icono_experiencia('456').getpixel((1,1)),(255,0,0))
            d=agregar_favorito({},'Mi Maze','123');control=ControlRoblox(iniciar=False,cache=tmp);control.configurar(d)
            self.assertEqual(control.informacion_guardada(d['favoritos'][0])['perfil'],'terror')
    def test_sin_red_recupera_datos_caducados_y_no_pierde_icono(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=CacheRoblox(tmp);cache.guardar_info(info());cache.guardar_icono('456',Image.new('RGB',(150,150),'blue'))
            p=Path(tmp)/'experiencia-123.json';d=json.loads(p.read_text(encoding='utf8'));d['guardado']=time.time()-90000;p.write_text(json.dumps(d),encoding='utf8')
            c=ClientePublico(tmp)
            with patch.object(c,'_consultar_lugar',side_effect=ErrorRoblox('Sin red')),patch.object(c,'json',side_effect=ErrorRoblox('Sin red')):
                self.assertEqual(c.detalles_lugar('123')['nombre'],'The Maze')
                self.assertEqual(c.icono_experiencia('456',forzar=True).getpixel((0,0)),(0,0,255))
    def test_cache_incompleta_o_corrupta_se_descarta_y_solo_guarda_campos_publicos(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=CacheRoblox(tmp);c.guardar_info({**info(),'url':'https://www.roblox.com/games/123?privateServerLinkCode=privado','cookie':'no debe guardarse'})
            guardado=(Path(tmp)/'experiencia-123.json').read_text(encoding='utf8')
            self.assertNotIn('privado',guardado);self.assertNotIn('cookie',guardado)
            (Path(tmp)/'icono-456.png').write_bytes(b'No es una imagen')
            self.assertIsNone(c.leer_icono('456'))
            (Path(tmp)/'experiencia-123.json').write_text('{no es JSON',encoding='utf8');self.assertIsNone(c.leer_info('123'))
            self.assertIsNone(c.leer_info('../ajustes'));self.assertIsNone(c.leer_icono('../ajustes'))
    def test_icono_pendiente_no_se_guarda_como_un_resultado_vacio(self):
        c=ClientePublico();im=Image.new('RGB',(150,150),'green')
        with patch.object(c,'json',return_value={}) as red,patch.object(c,'_imagen_miniatura',side_effect=[None,im]):
            self.assertIsNone(c.icono_experiencia('456'));self.assertIsNotNone(c.icono_experiencia('456'))
            self.assertIsNotNone(c.icono_experiencia('456'));self.assertEqual(red.call_count,2)

if __name__=='__main__':unittest.main()
