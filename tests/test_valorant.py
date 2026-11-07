import copy
import json
import sys
import tempfile
import threading
from pathlib import Path
import unittest
from unittest.mock import Mock,MagicMock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valorant import *
from valorant_cliente import SesionRiot,permitida,descubrir,ClienteValorant

YO='00000000-0000-0000-0000-000000000001'
ALIADO='00000000-0000-0000-0000-000000000002'
PARTY='10000000-0000-0000-0000-000000000001'
MATCH='20000000-0000-0000-0000-000000000001'
A='30000000-0000-0000-0000-000000000001'
B='30000000-0000-0000-0000-000000000002'
C='30000000-0000-0000-0000-000000000003'

class Cliente:
    jugador=YO
    def __init__(self):
        self.llamadas=[];self.pregame=True;self.en_juego=False;self.owned=[A,B,C];self.leer=None;self.rechazar=None;self.confirmar=True
        self.sala={'ID':PARTY,'State':'DEFAULT','Members':[{'Subject':YO,'IsOwner':True}],
                   'RestrictedSeconds':0,'QueueIneligibilities':[]}
        self.match={'ID':MATCH,'PregameState':'character_select_active','MapID':'/Game/Maps/Test/Test','PhaseTimeRemainingNS':80000000000,'AllyTeam':{'Players':[
            {'Subject':YO,'CharacterID':'','CharacterSelectionState':'','PregamePlayerState':'joined'},
            {'Subject':ALIADO,'CharacterID':'','CharacterSelectionState':''}]}}
    def pedir(self,m,r):
        self.llamadas.append((m,r))
        if self.leer:self.leer(m,r)
        if m=='GET':
            if r==f'/pregame/v1/players/{YO}':return {'Subject':YO,'MatchID':MATCH} if self.pregame else None
            if r==f'/core-game/v1/players/{YO}':return {'Subject':YO} if self.en_juego else None
            if r==f'/parties/v1/players/{YO}':return {'Subject':YO,'CurrentPartyID':PARTY}
            if r==f'/parties/v1/parties/{PARTY}':return copy.deepcopy(self.sala)
            if r==f'/pregame/v1/matches/{MATCH}':return copy.deepcopy(self.match)
            if r.startswith('/store/'):return {'Entitlements':[{'ItemID':a} for a in self.owned]}
        if m=='POST':
            if self.rechazar and r.endswith(self.rechazar):raise ErrorValorant('rechazo')
            if r.endswith('/join') and self.confirmar:self.sala['State']='MATCHMAKING'
            elif r.endswith('/leave') and self.confirmar:self.sala['State']='DEFAULT'
            elif '/select/' in r and self.confirmar:self.match['AllyTeam']['Players'][0].update(CharacterID=r.rsplit('/',1)[1],CharacterSelectionState='selected')
            elif '/lock/' in r and self.confirmar:self.match['AllyTeam']['Players'][0]['CharacterSelectionState']='locked'
        return None

class Valorant(unittest.TestCase):
    def preparar(self):
        c=Cliente();v=ControlValorant(c,reloj=Mock(return_value=0));v._base=set();v.configurar({'preferencias':[A,B,C]},iniciar=False)
        v.revisar(manual=True);c.llamadas.clear();v._reloj.return_value=ESPERA_PRESENTACION
        return v,c
    def post(self,c):return [r for m,r in c.llamadas if m=='POST']

    def test_normalizar_no_activa_automatico_ni_duplica(self):
        self.assertEqual(normalizar({'auto_pick':'true','preferencias':[A,A,'http://malicioso']}),{'auto_pick':False,'preferencias':[A,'','']})

    def test_espera_presentacion_de_mapa_antes_de_select_y_lock(self):
        v,c=self.preparar();v._preparacion=None;v._reloj.return_value=0
        v.revisar(manual=True);self.assertEqual(self.post(c),[])
        v._reloj.return_value=ESPERA_PRESENTACION-.01
        v.revisar(manual=True);self.assertEqual(self.post(c),[])
        v._reloj.return_value=ESPERA_PRESENTACION
        v.revisar(manual=True)
        self.assertEqual(self.post(c),[f'/pregame/v1/matches/{MATCH}/select/{A}',f'/pregame/v1/matches/{MATCH}/lock/{A}'])

    def test_sin_mapa_tiempo_o_jugador_listo_no_elige(self):
        for campo,valor in (('MapID',''),('PhaseTimeRemainingNS',0),('PhaseTimeRemainingNS',None),('PregamePlayerState','loading')):
            v,c=self.preparar()
            destino=c.match['AllyTeam']['Players'][0] if campo=='PregamePlayerState' else c.match
            destino[campo]=valor;v.revisar(manual=True);v._reloj.return_value=100;v.revisar(manual=True)
            self.assertEqual(self.post(c),[],campo)

    def test_cambio_de_mapa_reinicia_espera_y_revalida_antes_de_enviar(self):
        v,c=self.preparar();c.match['MapID']='/Game/Maps/Other/Other'
        v.revisar(manual=True);self.assertEqual(self.post(c),[])
        v._reloj.return_value=2*ESPERA_PRESENTACION
        def leer(m,r):
            if r.startswith('/store/'):c.match['PhaseTimeRemainingNS']=0
        c.leer=leer;v.revisar(manual=True);self.assertEqual(self.post(c),[])

    def test_tres_preferencias_y_sin_alternativa_no_selecciona(self):
        for ocupados,esperado in (([],A),([A],B),([A,B],C),([A,B,C],None)):
            v,c=self.preparar();c.match['AllyTeam']['Players'] += [dict(Subject='aliado'+str(i),CharacterID=a,CharacterSelectionState='locked') for i,a in enumerate(ocupados)]
            v.revisar(manual=True)
            self.assertEqual(self.post(c),[f'/pregame/v1/matches/{MATCH}/select/{esperado}',f'/pregame/v1/matches/{MATCH}/lock/{esperado}'] if esperado else [])
            self.assertEqual(v.estado,MENSAJES['confirmado' if esperado else 'sin_opciones'])

    def test_una_preferencia_ocupada_no_inventa_otra(self):
        v,c=self.preparar();v.configurar({'preferencias':[A]},iniciar=False)
        c.match['AllyTeam']['Players'][1].update(CharacterID=A,CharacterSelectionState='selected')
        v.revisar(manual=True);self.assertEqual(self.post(c),[])

    def test_salta_agente_no_desbloqueado(self):
        v,c=self.preparar();c.owned=[C];v.revisar(manual=True)
        self.assertTrue(self.post(c)[0].endswith('/select/'+C))

    def test_respeta_hover_aliado_y_seleccion_manual_local(self):
        v,c=self.preparar();c.match['AllyTeam']['Players'][1].update(CharacterID=A,CharacterSelectionState='selected')
        v.revisar(manual=True);self.assertTrue(self.post(c)[0].endswith('/select/'+B))
        v,c=self.preparar();c.match['AllyTeam']['Players'][0].update(CharacterID=C,CharacterSelectionState='selected')
        v.revisar(manual=True);self.assertEqual(self.post(c),[]);self.assertEqual(v.estado,MENSAJES['manual'])

    def test_solo_seleccion_activa_y_miembro_local(self):
        for tipo in ('fuera','estado','sin_yo'):
            v,c=self.preparar()
            if tipo=='fuera':c.pregame=False
            elif tipo=='estado':c.match['PregameState']='provisioned'
            else:c.match['AllyTeam']['Players']=[]
            v.revisar(manual=True);self.assertEqual(self.post(c),[],tipo)

    def test_revalida_aliado_antes_de_lock_y_pasa_a_segunda(self):
        v,c=self.preparar()
        def leer(m,r):
            if m=='POST' and '/select/' in r:c.match['AllyTeam']['Players'][1].update(CharacterID=A,CharacterSelectionState='locked')
        c.leer=leer;v.revisar(manual=True)
        self.assertEqual(self.post(c),[f'/pregame/v1/matches/{MATCH}/select/{A}'])
        v.revisar(manual=True);self.assertTrue(self.post(c)[-1].endswith('/lock/'+B))

    def test_no_doble_lock_ni_repetir_rechazo_mismo_agente(self):
        v,c=self.preparar();v.revisar(manual=True);v.revisar(manual=True);self.assertEqual(len(self.post(c)),2)
        v,c=self.preparar();c.rechazar='/select/'+A
        v.revisar(manual=True);v.revisar(manual=True)
        self.assertEqual(self.post(c).count(f'/pregame/v1/matches/{MATCH}/select/{A}'),1)
        self.assertTrue(self.post(c)[-1].endswith('/lock/'+B))

    def test_no_afirma_exito_sin_confirmacion(self):
        v,c=self.preparar();c.confirmar=False;v.revisar(manual=True)
        self.assertEqual(v.estado,MENSAJES['enviado']);self.assertEqual(len(self.post(c)),1)

    def test_cancelacion_y_config_cambiada_antes_de_escritura(self):
        for modo in ('stop','config'):
            v,c=self.preparar();stop=threading.Event()
            def leer(m,r):
                if r.startswith('/store/'):
                    if modo=='stop':stop.set()
                    else:v.configurar({},iniciar=False)
            c.leer=leer;v.revisar(stop,manual=True);self.assertEqual(self.post(c),[])

    def test_monitor_no_busca_ni_acepta(self):
        v,c=self.preparar();v.configurar({'auto_pick':True,'preferencias':[A,B,C]},iniciar=False)
        v.revisar();self.assertEqual(len(self.post(c)),2)
        v.revisar();self.assertEqual(len(self.post(c)),2)
        self.assertTrue(all('/pregame/' in r for r in self.post(c)))

    def test_buscar_cancelar_y_volver_manualmente(self):
        v,c=self.preparar();c.pregame=False
        self.assertEqual(v.ejecutar('valorant_buscar'),MENSAJES['buscando'])
        self.assertEqual(v.ejecutar('valorant_cancelar'),MENSAJES['cancelada'])
        v.consultar();v.consultar();self.assertEqual(len(self.post(c)),2)
        v.ejecutar('valorant_buscar');self.assertEqual(len(self.post(c)),3)

    def test_cancelacion_desde_juego_no_reencola(self):
        v,c=self.preparar();c.pregame=False;c.sala['State']='MATCHMAKING';v.consultar()
        c.sala['State']='DEFAULT';v.consultar();v.consultar();self.assertEqual(self.post(c),[])

    def test_cancelar_no_desactiva_preferencias_ni_impide_busqueda_manual(self):
        v,c=self.preparar();v.configurar({'auto_pick':True,'preferencias':[A,B,C]},iniciar=False)
        c.pregame=False;c.sala['State']='MATCHMAKING';v.ejecutar('valorant_cancelar')
        self.assertTrue(v.config['auto_pick']);self.assertEqual(v.config['preferencias'],[A,B,C])
        v.ejecutar('valorant_buscar');self.assertTrue(self.post(c)[-1].endswith('/join'))

    def test_cancelar_antes_de_busqueda_y_cambio_de_lider_no_envian(self):
        v,c=self.preparar();c.pregame=False;stop=threading.Event();stop.set()
        v.ejecutar('valorant_buscar',cancelar=stop);self.assertEqual(self.post(c),[])
        lecturas=[]
        def leer(m,r):
            if r==f'/parties/v1/parties/{PARTY}':
                lecturas.append(r)
                if len(lecturas)==2:c.sala['Members'][0]['IsOwner']=False
        c.leer=leer;v.ejecutar('valorant_buscar');self.assertEqual(self.post(c),[])

    def test_no_buscar_sin_lider_con_restriccion_o_dentro_partida(self):
        for tipo in ('lider','restriccion','pregame','juego'):
            v,c=self.preparar();c.pregame=False
            if tipo=='lider':c.sala['Members'][0]['IsOwner']=False
            elif tipo=='restriccion':c.sala['RestrictedSeconds']=60
            elif tipo=='pregame':c.pregame=True
            else:c.en_juego=True
            v.ejecutar('valorant_buscar');self.assertEqual(self.post(c),[],tipo)

    def test_ordenes_explicitas_no_extraen_de_citas_ni_negaciones(self):
        from core import interpretar
        for texto,accion in (('Capri, busca partida en valorant','valorant_buscar'),('cancela la cola en valorant','valorant_cancelar'),
                             ('find a match in valorant','valorant_buscar'),('busque uma partida no valorant','valorant_buscar'),
                             ('VALORANTでマッチを検索して','valorant_buscar'),('confirma mi agente en valorant','valorant_elegir')):
            self.assertEqual(interpretar(texto).tipo,accion)
        for texto in ('no busques partida en valorant','cómo buscar partida en valorant','busca en google busca partida en valorant'):
            o=interpretar(texto);self.assertFalse(o and o.tipo.startswith('valorant_'))

    def test_formas_habladas_de_cola_no_terminan_en_chat_web_o_spotify(self):
        from core import interpretar
        for frase in ('tira partida en Valorant','inicia la búsqueda en Valorant',
                      'busca partida de Valorant','ponme en cola en Valorant',
                      'realiza una búsqueda en Valorant','lanza la cola del Valorant',
                      'dale a buscar partida en Valorant','busca partida en el Valo',
                      'quiero que busques partida en Valorant','puedes poner la cola en Valorant',
                      'puedes buscarme una partida en Valorant'):
            with self.subTest(frase=frase):self.assertEqual(interpretar('Capri, '+frase).tipo,'valorant_buscar')
        self.assertEqual(interpretar('Capri, selecciona mi personaje en Valorant').tipo,'valorant_elegir')
        self.assertEqual(interpretar('Capri, detén la búsqueda en Valorant').tipo,'valorant_cancelar')
        for frase in ('no tires partida en Valorant','cómo iniciar la búsqueda en Valorant',
                      'explica cómo ponme en cola en Valorant','busca en Google tira partida en Valorant'):
            orden=interpretar(frase)
            self.assertFalse(orden and orden.tipo.startswith('valorant_'))

    def test_transporte_no_acepta_hosts_rutas_cuentas_ni_post_arbitrarios(self):
        for m,r in (('GET','https://evil.com'),('GET',f'/pregame/v1/players/{ALIADO}'),('GET','//evil.com'),
                    ('POST',f'/pregame/v1/matches/{MATCH}/quit'),('POST',f'/parties/v1/parties/{PARTY}/matchmaking/join?x=1')):
            self.assertFalse(permitida(m,r,YO))
        self.assertTrue(permitida('POST',f'/pregame/v1/matches/{MATCH}/lock/{A}',YO))
        s=SesionRiot(YO,'secreto-privado','derecho-privado','latam','na','release-13.09-shipping-18-5804228')
        self.assertNotIn('privado',repr(s));self.assertNotIn(YO,repr(s))
        with self.assertRaises(ErrorValorant):SesionRiot(YO,'a','b','latam','evil.com','version')

    def test_descubrimiento_solo_local_sesion_activa_y_sin_persistir_tokens(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'LOCALAPPDATA':d}):
            p=Path(d)/'Riot Games/Riot Client/Config';p.mkdir(parents=True);(p/'lockfile').write_text('RiotClient:1:12345:password:https')
            log=Path(d)/'VALORANT/Saved/Logs';log.mkdir(parents=True);(log/'ShooterGame.log').write_text('CI server version: release-13.09-shipping-18-5804228')
            respuestas=[{'a':{'productId':'valorant','phase':'RUNNING','launchConfiguration':{'arguments':['-ares-deployment=latam']}}},
                        {'subject':YO,'accessToken':'privado','token':'privado2'}]
            with patch('valorant_cliente._json',side_effect=respuestas) as leer:
                s=descubrir();self.assertEqual(s.region,'latam')
                self.assertTrue(all(c.args[1].full_url.startswith('https://127.0.0.1:12345/') for c in leer.call_args_list))
            for fase,proceso,aceptar in (('Idle',True,True),('Idle',False,False),('Stopped',True,False)):
                respuestas[0]['a']['phase']=fase
                with self.subTest(fase=fase,proceso=proceso),patch('valorant_cliente._json',side_effect=respuestas),patch('valorant_cliente.juego_en_ejecucion',return_value=proceso):
                    if aceptar:self.assertEqual(descubrir().region,'latam')
                    else:
                        with self.assertRaises(ErrorValorant) as error:descubrir()
                        self.assertEqual(error.exception.clave,'cliente')

    def test_transporte_pvp_con_tls_y_detiene_cambio_cuenta_antes_de_post(self):
        import ssl,urllib.request
        s=SesionRiot(YO,'token','derecho','latam','na','release-13.09-shipping-18-5804228')
        otro=SesionRiot(ALIADO,'otro','otro2','latam','na','release-13.09-shipping-18-5804228')
        c=ClienteValorant(obtener=Mock(side_effect=[s,otro]));respuesta=Mock();respuesta.read.return_value=b'null'
        contexto=next(h._context for h in c.abridor.handlers if isinstance(h,urllib.request.HTTPSHandler))
        self.assertEqual(contexto.verify_mode,ssl.CERT_REQUIRED);self.assertTrue(contexto.check_hostname)
        c.abridor.open=MagicMock();c.abridor.open.return_value.__enter__.return_value=respuesta
        c.pedir('GET',f'/pregame/v1/players/{YO}')
        req=c.abridor.open.call_args.args[0]
        self.assertEqual(req.full_url,f'https://glz-latam-1.na.a.pvp.net/pregame/v1/players/{YO}')
        self.assertEqual(req.get_header('Authorization'),'Bearer token')
        self.assertEqual(req.get_header('User-agent'),'CapriDesktop')
        with self.assertRaises(ErrorValorant):c.pedir('POST',f'/parties/v1/parties/{PARTY}/matchmaking/join')
        self.assertEqual(c.abridor.open.call_count,1)

    def test_todos_los_estados_tienen_traduccion(self):
        from idiomas import ui
        for texto in MENSAJES.values():
            for idioma in ('en','pt','ja'):self.assertNotEqual(ui(texto,idioma),texto)

    def test_detectar_juego_en_primer_plano_no_activa_ni_minimiza_ventanas(self):
        import escritorio
        from pathlib import PureWindowsPath
        from types import SimpleNamespace
        user=MagicMock();kernel=MagicMock();user.GetForegroundWindow.return_value=100;kernel.OpenProcess.return_value=123
        def identidad(handle,flags,ruta,longitud):
            ruta.value='C:/Riot Games/VALORANT/live/VALORANT-Win64-Shipping.exe';return 1
        kernel.QueryFullProcessImageNameW.side_effect=identidad
        with patch.object(escritorio.os,'name','nt'),patch('ctypes.windll',SimpleNamespace(user32=user,kernel32=kernel),create=True),patch.object(escritorio,'Path',PureWindowsPath):
            self.assertTrue(escritorio.valorant_en_primer_plano());kernel.CloseHandle.assert_called_once_with(123)
            kernel.OpenProcess.return_value=0;self.assertFalse(escritorio.valorant_en_primer_plano())
        user.SetForegroundWindow.assert_not_called();user.ShowWindow.assert_not_called()

if __name__=='__main__':unittest.main()
