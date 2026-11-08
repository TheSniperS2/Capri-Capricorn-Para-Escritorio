import os,subprocess,sys,unittest,uuid
from pathlib import Path
from unittest.mock import Mock,patch
from instancia import InstanciaCapri

@unittest.skipUnless(os.name=='nt','Eventos locales de Windows')
class Instancia(unittest.TestCase):
    def nombre(self):return 'Local\\CapriPrueba-'+uuid.uuid4().hex
    def test_segunda_apertura_envia_una_peticion_y_no_toma_la_instancia(self):
        nombre=self.nombre()
        with InstanciaCapri(nombre) as primera:
            self.assertTrue(primera.primera);self.assertFalse(primera.recibir())
            # El nombre de prueba evita cualquier señal a la Capri del usuario.
            with InstanciaCapri(nombre) as segunda:
                self.assertFalse(segunda.primera);self.assertTrue(segunda.solicitar_mostrar())
                self.assertTrue(primera.recibir());self.assertFalse(primera.recibir())
        self.assertIsNone(primera.mutex);self.assertIsNone(primera.evento)
    def test_peticion_real_desde_otro_proceso_se_recibe_una_sola_vez(self):
        nombre=self.nombre()
        with InstanciaCapri(nombre) as primera:
            codigo='from instancia import InstanciaCapri; import sys\nwith InstanciaCapri(sys.argv[1]) as c:\n assert not c.primera\n assert c.solicitar_mostrar()\n'
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src'))
            r=subprocess.run([sys.executable,'-c',codigo,nombre],env=env,capture_output=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr.decode(errors='replace'))
            self.assertTrue(primera.recibir());self.assertFalse(primera.recibir())
    def test_main_reutiliza_la_instancia_sin_crear_otra_interfaz_ni_mensaje(self):
        import app
        existente=Mock();existente.primera=False
        with patch('instancia.InstanciaCapri') as clase,patch.object(app,'Capri') as crear,patch.object(app.messagebox,'showinfo') as aviso:
            clase.return_value.__enter__.return_value=existente
            app.main();existente.solicitar_mostrar.assert_called_once();crear.assert_not_called();aviso.assert_not_called()

if __name__=='__main__':unittest.main()
