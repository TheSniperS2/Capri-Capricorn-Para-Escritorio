import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from playlists import cargar,vincular,listar_vinculadas,quitar_vinculo,actualizar_titulo
from playlists_metadata import consultar

A='spotify:playlist:1234567890123456789012'
B='spotify:playlist:ABCDEFGHIJKLMNOPQRSTUV'


class PlaylistsGuardadas(unittest.TestCase):
    def test_lee_formato_anterior_sin_reescribir_y_migra_al_guardar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p=Path(carpeta);f=p/'playlists.json';f.write_text(json.dumps({'anterior':A}),encoding='utf8');antes=f.read_bytes()
            self.assertEqual(cargar(p),{'anterior':A});self.assertEqual(listar_vinculadas(p)[0]['nombre'],'anterior')
            self.assertEqual(f.read_bytes(),antes)
            vincular('Música de Noche',B,p)
            self.assertEqual(cargar(p),{'anterior':A,'musica de noche':B})
            registros={r['clave']:r for r in listar_vinculadas(p)}
            self.assertEqual(registros['musica de noche']['nombre'],'Música de Noche')
            self.assertTrue(registros['musica de noche']['guardada'])

    def test_los_nombres_y_enlaces_se_recuperan_en_otro_proceso(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p=Path(carpeta);vincular('Capri de Noche',A,p)
            codigo='import json,sys; from pathlib import Path; from playlists import listar_vinculadas; print(json.dumps(listar_vinculadas(Path(sys.argv[1]))))'
            r=subprocess.run([sys.executable,'-c',codigo,carpeta],capture_output=True,text=True,check=True)
            registro=json.loads(r.stdout)[0]
            self.assertEqual(registro['nombre'],'Capri de Noche');self.assertEqual(registro['uri'],A)

    def test_escritura_atomica_y_json_invalido_no_se_sobrescribe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p=Path(carpeta);vincular('Noche',A,p);antes=(p/'playlists.json').read_bytes()
            with patch('playlists.os.replace',side_effect=OSError('Sin espacio')):
                with self.assertRaises(OSError):vincular('Día',B,p)
            self.assertEqual((p/'playlists.json').read_bytes(),antes)
            self.assertFalse(list(p.glob('.playlists-*.tmp')))
            (p/'playlists.json').write_text('{no es json',encoding='utf8')
            with self.assertRaises(ValueError):vincular('Día',B,p)
            self.assertEqual((p/'playlists.json').read_text(encoding='utf8'),'{no es json')

    def test_editar_conflictos_y_metadatos_tardios_no_pierden_registros(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p=Path(carpeta);vincular('Noche',A,p);vincular('Día',B,p)
            actualizar_titulo(A,'Playlist con nombre difícil ✨',p)
            vincular('Para jugar',A,p,anterior='noche')
            self.assertEqual(set(cargar(p)),{'para jugar','dia'})
            self.assertEqual(next(r for r in listar_vinculadas(p) if r['clave']=='para jugar')['titulo'],'Playlist con nombre difícil ✨')
            with self.assertRaises(ValueError):vincular('Día',A,p,anterior='para jugar')
            quitar_vinculo('Para jugar',p);actualizar_titulo(A,'Resultado tardío',p)
            self.assertEqual(cargar(p),{'dia':B})

    def test_metadatos_opcionales_no_usan_html_ni_imagenes_de_otro_sitio(self):
        with tempfile.TemporaryDirectory() as carpeta:
            respuesta=io.BytesIO(json.dumps({'title':'  Música  de noche ','html':'<script>no ejecutar</script>',
                'thumbnail_url':'http://127.0.0.1/secreto'}).encode())
            with patch('playlists_metadata.urlopen',return_value=respuesta) as abrir:
                self.assertEqual(consultar(A,Path(carpeta)),'Música de noche')
                self.assertEqual(abrir.call_count,1)
            self.assertFalse(list(Path(carpeta).rglob('*.png')))
