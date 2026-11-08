import io,json,threading,unittest
from unittest.mock import Mock,patch
from core import interpretar,Orden,IA
from roblox import normalizar,enlace,agregar_favorito,recordar,preparar_local,ClientePublico,ControlRoblox,DetectorEventos,ErrorRoblox
from roblox_dialogos import opinion,reaccion

def config():return agregar_favorito({},'Mi aventura','123456')

class Roblox(unittest.TestCase):
    def test_sin_datos_personales_ni_automatizaciones_por_defecto(self):
        d=normalizar({});self.assertEqual(d['favoritos'],[]);self.assertEqual(d['usuario'],'')
        self.assertEqual(d['recordatorios'],[]);self.assertFalse(d['avatar_auto'])
        self.assertEqual(normalizar(None),d)
    def test_enlaces_se_canonicalizan_y_rechazan_destinos_ajenos(self):
        self.assertEqual(enlace('https://www.roblox.com/games/123456/Una-Aventura'),'https://www.roblox.com/games/123456')
        self.assertEqual(enlace('123456'),'https://www.roblox.com/games/123456')
        self.assertIn('code=abcdefgh',enlace('https://www.roblox.com/share?code=abcdefgh&type=ExperienceDetails'))
        for u in ('http://www.roblox.com/games/12','https://roblox.com.evil.test/games/12','https://roblox.com@evil.test/games/12',
                  'file:///C:/Windows/System32/calc.exe','roblox://placeId=12','https://127.0.0.1/games/12','https://www.roblox.com/games/12?launchData=abc',
                  'https://www.roblox.com:invalid/games/12','https://www.roblox.com/share?code'):
            with self.assertRaises(ErrorRoblox,msg=u):enlace(u)
        privado='https://www.roblox.com/games/12?privateServerLinkCode=abcdefgh'
        self.assertEqual(enlace(privado),privado)
    def test_id_estable_notas_y_privados_no_se_abren_al_guardar(self):
        d=config();f=d['favoritos'][0];d['notas'][f['id']]='Buscar una llave azul.'
        with patch('os.startfile') as abrir:
            nuevo=agregar_favorito(d,'Otra etiqueta','https://www.roblox.com/games/123456')
        self.assertEqual(nuevo['favoritos'][0]['id'],f['id']);self.assertEqual(nuevo['notas'],d['notas']);abrir.assert_not_called()
        self.assertEqual(normalizar(nuevo),nuevo)
        with self.assertRaises(ErrorRoblox):agregar_favorito(nuevo,'Otra etiqueta','987654')
    def test_configuracion_corrupta_no_conserva_redirecciones_ni_recordatorios_invalidos(self):
        d=normalizar({'favoritos':[None,{'nombre':'Malo','url':'https://evil.test'}],
                     'notas':{'id-raro':'no'},'recordatorios':[None,{'id':'a'*32,'texto':'No válido','vence':float('nan')}],
                     'avatar_auto':'true','usuario':'cookie=secreto'})
        self.assertEqual(d,normalizar({}))
    def test_ordenes_literales_de_voz_texto_y_negaciones(self):
        casos=[('Capri, abre mi aventura en roblox',Orden('roblox_abrir','mi aventura')),
               ('abre el panel de roblox',Orden('roblox_panel')),
               ('qué te parece mi avatar de roblox?',Orden('roblox_avatar')),
               ('anota en roblox: Buscar la llave azul.',Orden('roblox_nota_guardar','Buscar la llave azul')),
               ('modo terror en roblox',Orden('roblox_perfil','terror')),
               ('gané en roblox',Orden('roblox_evento','victoria'))]
        for t,o in casos:self.assertEqual(interpretar(t),o,t)
        for t in ('no abras mi aventura en roblox','si digo abre mi aventura en roblox','"abre mi aventura en roblox"'):
            self.assertFalse((interpretar(t) or Orden('')).tipo.startswith('roblox_'),t)
    def test_nota_y_perfil_no_se_comparten_entre_favoritos(self):
        d=config();id1=d['seleccion'];d,r=preparar_local(d,'roblox_nota_guardar','Llave azul.')
        d,r=preparar_local(d,'roblox_perfil','terror')
        d=agregar_favorito(d,'Otro','987654');d,r=preparar_local(d,'roblox_nota_leer','')
        self.assertIn('Todavía',r);self.assertEqual(d['notas'][id1],'Llave azul.')
        self.assertEqual(d['favoritos'][0]['perfil'],'terror');self.assertEqual(d['favoritos'][1]['perfil'],'clasica')
    def test_recordatorios_persisten_tiempo_real_y_no_aceptan_intervalos_invalidos(self):
        d=recordar(config(),'Estirar las piernas',30,ahora=1000)
        copia=normalizar(json.loads(json.dumps(d)))
        self.assertEqual(copia['recordatorios'][0]['vence'],2800)
        self.assertEqual(copia['recordatorios'][0]['juego'],'Mi aventura')
        for m in (0,-1,10081,float('nan')):
            with self.assertRaises(ErrorRoblox):recordar({},'Prueba',m)
    def test_apertura_solo_favoritos_por_accion_explicita_y_cancelacion(self):
        c=ControlRoblox(iniciar=False);c.configurar(config());abrir=Mock()
        c.abrir('mi aventura',abrir=abrir);abrir.assert_called_once_with('https://www.roblox.com/games/123456')
        self.assertIsNotNone(c.inicio)
        with self.assertRaises(ErrorRoblox):c.abrir('otra',abrir=abrir)
        stop=threading.Event();stop.set()
        with self.assertRaises(InterruptedError):c.abrir('mi aventura',cancelar=stop,abrir=abrir)
        self.assertEqual(abrir.call_count,1)
    def test_avatar_consistente_independiente_de_orden_y_versiones_del_recurso(self):
        cliente=ClientePublico();datos={'assets':[{'id':10,'name':'Chaqueta','assetType':{'name':'Shirt'}},
                    {'id':20,'name':'Sombrero','assetType':{'name':'Hat'}}]}
        with patch.object(cliente,'json',return_value=datos):a=cliente.avatar('1')
        datos['assets'].reverse();datos['assets'][0]['currentVersionId']=999
        with patch.object(cliente,'json',return_value=datos):b=cliente.avatar('1')
        self.assertEqual(a['huella'],b['huella']);self.assertEqual(opinion(a),opinion(b))
        for idioma in ('es','en','pt','ja'):self.assertTrue(opinion(a,idioma))
    def test_avatar_usuario_cambiado_o_peticion_cancelada_no_se_publica(self):
        fake=Mock();c=ControlRoblox(iniciar=False,cliente=fake);c.configurar({'usuario':'1'})
        def responder(u):c.configurar({'usuario':'2'});return {'usuario':u,'huella':'abc'}
        fake.avatar.side_effect=responder
        with self.assertRaises(InterruptedError):c.avatar()
        self.assertIsNone(c.avatar_actual)
    def test_cliente_no_envia_cookies_y_limita_host_y_tamano(self):
        c=ClientePublico();c.opener=Mock();c.opener.open.return_value=io.BytesIO(b'{"assets":[]}')
        self.assertEqual(c.json('https://avatar.roblox.com/v1/users/1/avatar'),{'assets':[]})
        req=c.opener.open.call_args.args[0];self.assertFalse(any(k.lower()=='cookie' for k in req.headers))
        with self.assertRaises(ErrorRoblox):c.json('https://localhost/v1/avatar')
        self.assertEqual(c.opener.open.call_count,1)
    def test_respuestas_publicas_incompletas_no_rompen_el_controlador(self):
        c=ClientePublico()
        for datos in ({'data':None},{'data':[None]},{'data':{'id':1}}):
            with patch.object(c,'json',return_value=datos):
                with self.assertRaises(ErrorRoblox):c.avatar('Nombre')
        with patch.object(c,'json',return_value={'assets':[{'id':10,'name':'Prenda','assetType':None}]}):
            self.assertEqual(c.avatar('1')['piezas'][0]['tipo'],'')
        for datos in ({'data':None},{'data':[None]},{'data':[{'targetId':1,'state':'Completed','imageUrl':None}]}):
            with patch.object(c,'json',return_value=datos):self.assertIsNone(c.miniatura('1'))

    def test_ocr_dos_observaciones_linea_exacta_sin_repetir_ni_ambiguedad(self):
        d=DetectorEventos();reglas={'victoria':'VICTORY|Ganaste','muerte':'YOU DIED'}
        self.assertIsNone(d.observar(['Texto que contiene VICTORY'],reglas,0))
        self.assertIsNone(d.observar(['VICTORY'],reglas,1));self.assertEqual(d.observar(['VICTORY'],reglas,5),'victoria')
        for t in (10,60,100):self.assertIsNone(d.observar(['VICTORY'],reglas,t))
        d.observar([],reglas,110);d.observar([],reglas,114)
        self.assertIsNone(d.observar(['VICTORY','YOU DIED'],reglas,120))
        self.assertIsNone(d.observar(['VICTORY'],reglas,125));self.assertEqual(d.observar(['VICTORY'],reglas,129),'victoria')
    def test_contexto_no_inventa_estado_del_juego_y_no_se_traslada_sin_ser_asignado(self):
        ia=IA();ia.contexto_roblox={'experiencia_elegida':'Mi aventura','perfil':'terror','nota_del_usuario':'Una llave azul.'}
        with patch('core.urllib.request.urlopen',return_value=io.BytesIO(json.dumps({'message':{'content':'Tu nota menciona una llave azul.'}}).encode())) as red:
            ia.conversar('¿Qué había anotado?','modelo')
        sistema=json.loads(red.call_args.args[0].data)['messages'][0]['content']
        self.assertIn('Una llave azul.',sistema);self.assertIn('no prueban lo que está pasando',sistema)
    def test_reacciones_sin_promesas_de_acciones_y_perfil_discreto_breve(self):
        for e in ('victoria','derrota','muerte'):
            for idioma in ('es','en','pt','ja'):
                self.assertTrue(reaccion(e,'terror',idioma));self.assertTrue(reaccion(e,'discreta',idioma))
        self.assertLess(len(reaccion('victoria','discreta')),80)

    def test_lectura_visual_solo_roblox_y_descarta_cambios_de_ventana(self):
        import roblox_vision as vision
        from PIL import Image
        from types import SimpleNamespace
        v=(123,(10,20,1010,820));im=Image.new('RGB',(600,480))
        with patch.object(vision,'ventana',return_value=None),patch('PIL.ImageGrab.grab') as grab:
            self.assertIsNone(vision.leer_centro());grab.assert_not_called()
        with patch.object(vision,'ventana',return_value=v),patch('PIL.ImageGrab.grab',return_value=im) as grab,patch('fortnite_vision.leer_imagen',return_value=[SimpleNamespace(texto='VICTORY')]) as ocr:
            self.assertEqual(vision.leer_centro(),['VICTORY']);self.assertEqual(grab.call_args.kwargs['bbox'],(210,116,810,596))
            self.assertFalse(ocr.call_args.args[0].exists(),'La captura temporal debe borrarse')
        with patch.object(vision,'ventana',side_effect=[v,None]),patch('PIL.ImageGrab.grab',return_value=im),patch('fortnite_vision.leer_imagen') as ocr:
            self.assertIsNone(vision.leer_centro());ocr.assert_not_called()

if __name__=='__main__':unittest.main()
