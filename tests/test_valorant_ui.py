import json
from pathlib import Path
from unittest.mock import Mock,patch
from test_capri import PruebasTk
from tema_ui import tk
from valorant import ControlValorant,normalizar,cargar_catalogo
from valorant_ui import PanelValorant,TEXTOS

class Panel(PruebasTk):
    def test_prioridades_busqueda_guardado_comandos_y_tamano_pequeno(self):
        from fuentes import cargar
        cargar(Path(__file__).resolve().parents[1]);root=tk.Tk();root.withdraw()
        guardar=Mock();enviar=Mock();control=ControlValorant()
        with patch.object(control,'consultar') as consultar:
            p=PanelValorant(root,{},guardar,enviar,control,consultar=False)
            try:
                root.update();self.assertEqual(len(p.slots),3);self.assertGreaterEqual(len(p.botones),25)
                ids=list(p.catalogo.agentes)[:3]
                for i,id in enumerate(ids):p.activar(i);p.botones[id].invoke()
                self.assertEqual(p.config['preferencias'],ids);self.assertFalse(p.config['auto_pick'])
                self.assertEqual(json.loads(json.dumps(guardar.call_args.args[1])),p.config)
                p.activar(1);p.elegir(ids[0]);self.assertEqual(p.config['preferencias'],['',ids[0],ids[2]])
                p.elegir('');self.assertEqual(p.config['preferencias'][1],'')
                nombre=p.catalogo.agentes[ids[2]]['name'];p.busqueda.set(nombre);root.update();self.assertEqual(len(p.botones),1)
                p.campo_busqueda.limpiar();root.update();self.assertEqual(p.busqueda.get(),'')
                self.assertGreaterEqual(len(p.botones),25)
                for b in p.acciones.values():b.invoke()
                self.assertEqual([a.args[0] for a in enviar.call_args_list],['busca partida en valorant','cancela la cola en valorant','confirma mi agente en valorant'])
                consultar.assert_not_called();p.ventana.geometry('800x620');root.update()
                self.assertGreater(p.scroll.bbox('all')[3],p.scroll.winfo_height());p.scroll.yview_moveto(1);root.update();self.assertGreater(p.scroll.yview()[0],0)
            finally:p.cerrar();control.cerrar();root.destroy()

    def test_catalogo_imagenes_y_traducciones(self):
        from idiomas import ui,catalogo
        from PIL import Image
        from valorant import carpeta_catalogo
        datos=cargar_catalogo();self.assertGreaterEqual(len(datos['agents']),25)
        with Image.open(carpeta_catalogo()/'agentes.png') as im:
            for a in datos['agents']:
                self.assertLessEqual(a['image']['x']+a['image']['w'],im.width)
                self.assertLessEqual(a['image']['y']+a['image']['h'],im.height)
        for texto in TEXTOS:
            self.assertIn(texto,catalogo())
            for idioma in ('en','pt','ja'):self.assertTrue(ui(texto,idioma).strip())

    def test_aplicacion_guarda_preferencias_sin_iniciar_busqueda(self):
        import test_companera_control as fixtures
        import app
        with fixtures.ModoPersonaje.capri(self) as (c,ruta),patch.object(c.valorant,'configurar') as configurar,patch.object(c.valorant,'ejecutar') as ejecutar:
            config=normalizar({'preferencias':[cargar_catalogo()['agents'][0]['id']]})
            c.guardar('valorant',config);configurar.assert_called_once_with(config);ejecutar.assert_not_called()
            self.assertEqual(json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['valorant'],config)

    def test_ordenes_del_panel_ejecutan_valorant_sin_ia_ni_busqueda_web(self):
        import time
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch.object(c.valorant,'ejecutar',return_value='Listo') as ejecutar,patch('app.ejecutar') as generico,patch.object(c.ia,'conversar') as ia:
            for orden,tipo in (('busca partida en valorant','valorant_buscar'),('cancela la cola en valorant','valorant_cancelar'),
                               ('confirma mi agente en valorant','valorant_elegir')):
                c.enviar(orden);limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertFalse(c.ocupada);self.assertEqual(ejecutar.call_args.args[0],tipo)
            generico.assert_not_called();ia.assert_not_called()

    def test_voz_desde_valorant_ejecuta_busqueda_generica_sin_cambiar_foco(self):
        import time
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_),patch('escritorio.valorant_en_primer_plano',return_value=True),patch.object(c.valorant,'ejecutar',return_value='Listo') as ejecutar,patch.object(c.lol,'ejecutar',return_value='Listo') as lol,patch.object(c,'abrir_chat') as abrir:
            for texto,tipo in (('Capri, busca partida.','valorant_buscar'),('cancela la cola','valorant_cancelar')):
                c.enviar(texto,origen='voz');limite=time.monotonic()+3
                while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
                self.assertEqual(ejecutar.call_args.args[0],tipo)
            lol.assert_not_called();abrir.assert_not_called()
            c.enviar('busca partida en lol',origen='voz');limite=time.monotonic()+3
            while c.ocupada and time.monotonic()<limite:c.poll();time.sleep(.005)
            self.assertEqual(lol.call_args.args[0],'lol_buscar')

    def test_ajustes_abiertos_no_pausan_escucha_con_valorant_en_primer_plano(self):
        import test_companera_control as fixtures
        with fixtures.ModoPersonaje.capri(self) as (c,_), \
             patch('escritorio.fortnite_en_primer_plano',return_value=False), \
             patch('escritorio.cs2_en_primer_plano',return_value=False):
            c.activacion_permitida=True;c.cfg['activacion_voz']=True;c.ajustes=tk.Toplevel(c.root)
            with patch('escritorio.valorant_en_primer_plano',return_value=False),patch('app.threading.Thread') as hilo:
                c.mantener_activacion();hilo.assert_not_called()
            with patch('escritorio.valorant_en_primer_plano',return_value=True),patch('app.threading.Thread') as hilo:
                c.mantener_activacion();hilo.return_value.start.assert_called_once()
            c.activacion_hilo=None;c.activacion_permitida=False

if __name__=='__main__':__import__('unittest').main()
