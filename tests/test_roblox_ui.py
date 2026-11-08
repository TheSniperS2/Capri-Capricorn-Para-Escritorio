import contextlib,json,time
from unittest.mock import Mock,patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from roblox import agregar_favorito
from recordatorios import agregar

def informacion(lugar,forzar=False):
    return {'lugar':str(lugar),'universo':'456','nombre':'La casa de prueba','descripcion':'A horror adventure with doors.',
            'genero':'Survival','subgenero':'Escape','genero_original':'Adventure','creador':'Creador de prueba','perfil':'terror'}

class RobloxUI(PruebasTk):
    @contextlib.contextmanager
    def capri(self):
        with patch('roblox.ClientePublico.detalles_lugar',side_effect=informacion),patch('roblox.ClientePublico.icono_experiencia',return_value=None),patch('roblox.ClientePublico.miniatura',return_value=None),fixtures.ModoPersonaje.capri(self) as datos:
            errores=[];datos[0].root.report_callback_exception=lambda tipo,valor,traza:errores.append(str(valor))
            yield datos
            self.assertEqual(errores,[])
    def esperar(self,c,condicion=None):
        fin=time.monotonic()+4
        while time.monotonic()<fin:
            c.poll();c.root.update()
            if (condicion() if condicion else not c.ocupada):return
            time.sleep(.01)
        self.fail('No termino la operacion esperada')
    def test_favorito_sin_nombre_recibe_titulo_y_perfil_sin_abrir_el_juego(self):
        with self.capri() as (c,ruta),patch('os.startfile') as abrir:
            c.abrir_roblox();p=c.roblox_panel;p.nuevo_favorito();p.url.insert(0,'123456');p.agregar()
            self.esperar(c,lambda:c.cfg['roblox']['favoritos'][0]['nombre']=='La casa de prueba')
            d=json.loads((ruta/'ajustes.json').read_text(encoding='utf8'))['roblox']
            self.assertEqual(d['favoritos'][0]['nombre'],'La casa de prueba');self.assertEqual(c.roblox.perfil(),'terror')
            self.assertIn('Terror',p.perfil_texto.get());abrir.assert_not_called()
            c.minimizar_capri();c.root.update();c.abrir_roblox();self.assertIs(c.roblox_panel,p)
    def test_apertura_por_voz_conserva_alias_y_no_pasa_por_modelo(self):
        with self.capri() as (c,_),patch('os.startfile') as abrir,patch.object(c.ia,'conversar') as charla,patch.object(c.interprete,'resolver') as interpretar:
            c.guardar('roblox',agregar_favorito({},'Mi aventura','123456'));c.abrir_roblox()
            self.esperar(c,lambda:bool(c.roblox.informacion))
            c.enviar('abre mi aventura en roblox');self.esperar(c)
            abrir.assert_called_once_with('https://www.roblox.com/games/123456');charla.assert_not_called();interpretar.assert_not_called()
            self.assertEqual(c.cfg['roblox']['favoritos'][0]['nombre'],'Mi aventura')
    def test_voz_de_roblox_no_inicia_colas_de_otros_juegos(self):
        with self.capri() as (c,_),patch.object(c.lol,'ejecutar',return_value='Listo') as lol,patch.object(c,'abrir_roblox') as panel:
            c.guardar('juego_busqueda','roblox');c.enviar('busca partida');c.poll();panel.assert_called_once();lol.assert_not_called()
            c.enviar('busca partida en lol');self.esperar(c);lol.assert_called_once()
    def test_recordatorios_sin_juego_se_guardan_y_entregan_solo_una_vez(self):
        with self.capri() as (c,_),patch.object(c,'ejemplo_skin',return_value=True) as decir:
            c.enviar('recuérdame en 5 minutos beber agua')
            self.assertEqual(c.cfg['recordatorios'][0]['texto'],'beber agua');self.assertEqual(c.cfg['roblox']['recordatorios'],[])
            c.guardar('recordatorios',agregar([],'Un descanso',1,ahora=1));c.recordatorios_runtime=True
            with patch.object(c,'puede_reaccionar_skins',return_value=False):c.mantener_recordatorios()
            self.assertEqual(len(c.cfg['recordatorios']),1);decir.assert_not_called()
            with patch.object(c,'puede_reaccionar_skins',return_value=True):
                c.mantener_recordatorios();c.recordatorios_proximo=0;c.mantener_recordatorios()
            self.assertEqual(c.cfg['recordatorios'],[]);decir.assert_called_once()
    def test_panel_general_cancela_un_aviso_sin_tocar_el_otro(self):
        with self.capri() as (c,_):
            lista=agregar(agregar([],'Agua',5),'Una pausa',10);c.guardar('recordatorios',lista)
            c.abrir_recordatorios();p=c.recordatorios_panel;c.root.update();p.cancelar(lista[0]['id'])
            self.assertEqual([r['texto'] for r in c.cfg['recordatorios']],['Una pausa']);self.assertIsNone(c.roblox_panel)
    def test_avatar_comenta_el_accesorio_del_hombro(self):
        a={'usuario':'123','user_id':'123','huella':'123abc','piezas':[{'id':98,'nombre':'Robot de hombro','tipo_id':44,'tipo':'ShoulderAccessory'}],'gusto':0}
        with self.capri() as (c,_),patch.object(c.roblox.cliente,'avatar',return_value=a) as consulta,patch('os.startfile') as abrir:
            c.guardar('roblox',{'usuario':'123'});c.enviar('mira mi avatar en roblox');self.esperar(c)
            consulta.assert_called_once_with('123');abrir.assert_not_called()
            self.assertIn('hombro',c.historial[-1][1]);self.assertIn('Robot de hombro',c.historial[-1][1])
    def test_resultado_ambiguo_pregunta_y_acepta_respuesta_sin_favoritos(self):
        with self.capri() as (c,_),patch.object(c,'ejemplo_skin',return_value=True) as decir,patch('roblox_vision.en_primer_plano',return_value=True),patch.object(c,'puede_reaccionar_skins',return_value=True):
            c.guardar('roblox',{'acompanar':True});c.roblox_runtime=True
            c.cfg['voz']=False;c.escucha_activa.configurar('preguntas')
            c.roblox_aviso_pendiente={'tipo':'evento','evento':'duda','perfil':'clasica','generacion':c.roblox.generacion,'fecha':time.monotonic()}
            c.mantener_roblox();self.assertIn('¿Ganaste',decir.call_args.args[0]);self.assertGreater(c.roblox_duda_hasta,time.monotonic())
            self.assertGreater(c.escucha_activa.hasta,time.monotonic())
            c.enviar('perdí');self.esperar(c)
            self.assertNotIn('Selecciona un favorito',c.historial[-1][1]);self.assertIn('se escapó',c.historial[-1][1])
            self.assertEqual(c.roblox_duda_hasta,0)
    def test_perfil_inferido_reduce_solo_la_voz_del_turno(self):
        with self.capri() as (c,_),patch.object(c.voz,'hablar') as hablar,patch('roblox_vision.en_primer_plano',return_value=True):
            d=agregar_favorito({},'Mi aventura','123456');c.guardar('roblox',d)
            c.roblox.informacion[d['seleccion']]={**informacion('123456'),'perfil':'discreta'}
            c.cfg['voz']=True;c.cfg['volumen_voz']=80;c.narrar_respuesta(c.peticion,'Aquí sigo contigo.',final=True)
            self.assertEqual(hablar.call_args.kwargs['volumen'],48);self.assertEqual(c.cfg['volumen_voz'],80)
    def test_rueda_en_favoritos_no_desplaza_la_descripcion(self):
        with self.capri() as (c,_):
            d={}
            for i in range(24):d=agregar_favorito(d,'Aventura '+str(i),str(12000+i))
            c.guardar('roblox',d);c.abrir_roblox();p=c.roblox_panel;p.ventana.geometry('820x580');c.root.update()
            antes=p.detalle.lienzo.yview();hijo=p.biblioteca.interior.winfo_children()[0].winfo_children()[0]
            hijo.event_generate('<MouseWheel>',delta=-120);c.root.update()
            self.assertGreater(p.biblioteca.lienzo.yview()[0],0);self.assertEqual(p.detalle.lienzo.yview(),antes)
            self.assertTrue(p.agregar_boton.winfo_ismapped())
            self.assertLessEqual(p.agregar_boton.winfo_rooty()+p.agregar_boton.winfo_height(),p.ventana.winfo_rooty()+p.ventana.winfo_height()-25)
            for b in p.botones_pestanas.values():self.assertLessEqual(b.winfo_rootx()+b.winfo_width(),p.ventana.winfo_rootx()+p.ventana.winfo_width())
    def test_filtrar_lista_larga_a_un_favorito_elimina_hueco_y_limpiar_restaura(self):
        with self.capri() as (c,_):
            d=agregar_favorito({},'The Maze','123')
            for i in range(20):d=agregar_favorito(d,'Aventura '+str(i),str(12000+i))
            c.guardar('roblox',d);c.abrir_roblox();p=c.roblox_panel;c.root.update()
            p.biblioteca.mover(100);c.root.update();self.assertGreater(p.biblioteca.lienzo.canvasy(0),0)
            p.filtro_entrada.insert(0,'The Maze');c.root.update()
            self.assertEqual(len(p.biblioteca.interior.winfo_children()),1)
            for sentido in (-3,3):
                for _ in range(8):p.biblioteca.mover(sentido)
                c.root.update();self.assertEqual(p.biblioteca.lienzo.canvasy(0),0)
            p.limpiar_filtro();c.root.update()
            self.assertEqual(p.filtro.get(),'');self.assertEqual(len(p.biblioteca.interior.winfo_children()),21)
            p.filtro.set('Maze');p.filtro_entrada.event_generate('<Escape>');c.root.update()
            self.assertTrue(p.ventana.winfo_exists());self.assertEqual(p.filtro.get(),'')

    def test_volver_a_una_experiencia_recupera_su_icono_inmediatamente(self):
        from PIL import Image
        with self.capri() as (c,_):
            d=agregar_favorito(agregar_favorito({},'Primera','123'),'Segunda','124');d['seleccion']=d['favoritos'][0]['id']
            def datos(lugar,forzar=False):return {**informacion(lugar),'universo':str(int(lugar)+1000)}
            def icono(universo,**kw):return Image.new('RGB',(150,150),'red' if universo=='1123' else 'blue')
            with patch.object(c.roblox.cliente,'detalles_lugar',side_effect=datos),patch.object(c.roblox.cliente,'icono_experiencia',side_effect=icono):
                c.guardar('roblox',d);c.abrir_roblox();p=c.roblox_panel
                self.esperar(c,lambda:p.foto_juego is not None);primera=p.foto_juego
                p.seleccionar(d['favoritos'][1]['id']);self.esperar(c,lambda:p.foto_juego is not None)
                self.assertIsNot(p.foto_juego,primera)
                p.seleccionar(d['favoritos'][0]['id'])
                self.assertIs(p.foto_juego,primera)
                self.assertEqual(tuple(p.ventana.tk.call(str(p.foto_juego),'get',10,10)),(255,0,0))
    def test_icono_que_termina_mientras_miras_otro_favorito_no_se_descarta(self):
        import threading
        from PIL import Image
        with self.capri() as (c,_):
            d=agregar_favorito(agregar_favorito({},'Primera','123'),'Segunda','124');d['seleccion']=d['favoritos'][0]['id']
            bloqueado=threading.Event();soltar=threading.Event();self.addCleanup(soltar.set)
            def datos(lugar,forzar=False):return {**informacion(lugar),'universo':str(int(lugar)+1000)}
            def icono(universo,**kw):
                if universo=='1123':bloqueado.set();soltar.wait(3)
                return Image.new('RGB',(150,150),'red' if universo=='1123' else 'blue')
            with patch.object(c.roblox.cliente,'detalles_lugar',side_effect=datos),patch.object(c.roblox.cliente,'icono_experiencia',side_effect=icono):
                c.guardar('roblox',d);c.abrir_roblox();p=c.roblox_panel;self.esperar(c,bloqueado.is_set)
                p.seleccionar(d['favoritos'][1]['id']);self.esperar(c,lambda:p.foto_juego is not None)
                segunda=p.foto_juego;soltar.set();self.esperar(c,lambda:'1123' in p._fotos_juegos)
                self.assertIs(p.foto_juego,segunda)
                p.seleccionar(d['favoritos'][0]['id']);self.assertIsNotNone(p.foto_juego)
                self.assertEqual(tuple(p.ventana.tk.call(str(p.foto_juego),'get',10,10)),(255,0,0))
    def test_icono_y_datos_en_disco_se_muestran_al_recrear_el_controlador(self):
        from PIL import Image
        from roblox import ControlRoblox
        from test_roblox_cache import info
        with fixtures.ModoPersonaje.capri(self) as (c,ruta):
            carpeta=ruta/'cache/roblox';c.roblox.cliente.cache.guardar_info(info())
            c.roblox.cliente.cache.guardar_icono('456',Image.new('RGB',(150,150),'red'))
            c.roblox=ControlRoblox(iniciar=False,cache=carpeta)
            with patch.object(c.roblox.cliente,'json',side_effect=AssertionError('Debe recuperar la cache sin red')) as red:
                c.guardar('roblox',agregar_favorito({},'The Maze','123'));c.abrir_roblox();p=c.roblox_panel
                self.assertIsNotNone(p.foto_juego);self.assertEqual(p.titulo.get(),'The Maze')
                c.root.update();red.assert_not_called()
    def test_textos_de_ambos_paneles_tienen_traducciones(self):
        from roblox_ui import TEXTOS
        from recordatorios_ui import TEXTOS as avisos
        from idiomas import catalogo,ui
        for t in TEXTOS+avisos:
            self.assertIn(t,catalogo(),t)
            for idioma in ('en','pt','ja'):self.assertTrue(ui(t,idioma).strip())

if __name__=='__main__':__import__('unittest').main()
