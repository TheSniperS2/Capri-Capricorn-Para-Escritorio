from pathlib import Path
import tempfile
import io
import json
import unittest
from unittest.mock import patch
from PIL import Image
from test_capri import PruebasTk
from tema_ui import tk
from portadas_ui import CapturaPortada,recortar_portada
from playlists_metadata import guardar_portada,archivo_portada,consultar

URI='spotify:playlist:1234567890123456789012'


class PortadasLocales(unittest.TestCase):
    def test_publica_sin_thumbnail_recupera_imagen_del_embed_de_la_misma_playlist(self):
        imagen=io.BytesIO();Image.new('RGB',(300,300),'#123456').save(imagen,'PNG')
        entidad={'uri':URI,'visualIdentity':{'image':[{'maxWidth':640,'url':'https://i.scdn.co/image/ejemplo'}]}}
        estado={'props':{'pageProps':{'state':{'data':{'entity':entidad}}}}}
        html=('<script id="__NEXT_DATA__" type="application/json">'+json.dumps(estado)+'</script>').encode()
        respuestas=[io.BytesIO(b'{"title":"Publica"}'),io.BytesIO(html),io.BytesIO(imagen.getvalue())]
        with tempfile.TemporaryDirectory() as carpeta,patch('playlists_metadata.urlopen',side_effect=respuestas) as abrir:
            self.assertEqual(consultar(URI,carpeta),'Publica')
            self.assertEqual(abrir.call_count,3);self.assertTrue(archivo_portada(URI,carpeta).is_file())

    def test_recorte_limitado_y_seleccion_invertida(self):
        imagen=Image.new('RGB',(200,100),'#124567')
        self.assertEqual(recortar_portada(imagen,(80,75),(20,25)).size,(60,50))
        self.assertEqual(recortar_portada(imagen,(-10,-10),(900,900)).size,imagen.size)
        with self.assertRaises(ValueError):recortar_portada(imagen,(20,20),(25,25))

    def test_portada_se_conserva_y_una_descarga_tardia_no_la_reemplaza(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p=Path(carpeta)
            guardar_portada(Image.new('RGB',(300,300),'#123456'),URI,p)
            guardar_portada(Image.new('RGB',(300,300),'#ffffff'),URI,p,solo_si_falta=True)
            with Image.open(archivo_portada(URI,p)) as imagen:
                self.assertEqual(imagen.size,(256,256));self.assertEqual(imagen.getpixel((100,100)),(18,52,86))


class CapturaPrivadaUI(PruebasTk):
    def setUp(self):
        super().setUp();self.root=tk.Tk();self.root.withdraw();self.padre=tk.Toplevel(self.root)
        self.padre.geometry('500x400+40+40');self.root.update();self.padre.grab_set()
        self.imagenes=[];self.canceladas=[];self.captura=None

    def tearDown(self):
        if self.captura and not self.captura.cerrado:self.captura.cancelar()
        self.root.destroy();super().tearDown()

    def crear(self):
        with patch('portadas_ui.os.startfile') as abrir:
            self.captura=CapturaPortada(self.padre,URI,self.imagenes.append,lambda:self.canceladas.append(True))
            self.root.update();abrir.assert_called_once_with(URI)
        return self.captura

    def test_cancelar_restaura_ventanas_y_modal_sin_guardar_imagen(self):
        c=self.crear();self.assertEqual(self.padre.state(),'withdrawn');self.assertIsNone(self.root.grab_current())
        c.cancelar();self.root.update()
        self.assertEqual(self.padre.state(),'normal');self.assertEqual(float(self.padre.attributes('-alpha')),1.)
        self.assertIs(self.root.grab_current(),self.padre);self.assertEqual(self.imagenes,[]);self.assertEqual(self.canceladas,[True])

    def test_seleccion_solo_entrega_el_recorte_y_restaura_la_interfaz(self):
        c=self.crear()
        with patch('portadas_ui.ImageGrab.grab',return_value=Image.new('RGB',(800,600),'#123456')):
            c.seleccionar();self.root.update()
            c.canvas.event_generate('<ButtonPress-1>',x=100,y=100)
            c.canvas.event_generate('<B1-Motion>',x=228,y=228)
            c.canvas.event_generate('<ButtonRelease-1>',x=228,y=228);self.root.update()
        self.assertTrue(c.cerrado);self.assertEqual(len(self.imagenes),1)
        self.assertEqual(self.imagenes[0].size,(128,128));self.assertEqual(self.canceladas,[])
        self.assertIsNone(c.imagen);self.assertIsNone(c.foto)
        self.assertIs(self.root.grab_current(),self.padre);self.assertEqual(self.padre.state(),'normal')
