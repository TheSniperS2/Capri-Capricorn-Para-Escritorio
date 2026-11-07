import copy
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock,MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from league import ClienteLCU,Credenciales,FASE,ErrorCliente
from lol_seleccion import *


class Cliente:
    def __init__(self,tipo='pick'):
        self.llamadas=[];self.fase='ChampSelect';self.disponibles=[1,2,3,4]
        self.sesion={'gameId':123,'localPlayerCellId':1,'timer':{'phase':'BAN_PICK'},
                     'myTeam':[{'cellId':1,'assignedPosition':'middle','championId':0,'championPickIntent':0},
                               {'cellId':2,'assignedPosition':'top','championId':0,'championPickIntent':0}],
                     'theirTeam':[],'actions':[[{'id':7,'actorCellId':1,'type':tipo,'completed':False,'isInProgress':True,'championId':0}]]}
        self.rechazar=False;self.confirmar=True;self.leer=None
        self.fichas={}

    def pedir(self,metodo,ruta,datos=None):
        self.llamadas.append((metodo,ruta,datos))
        if self.leer:self.leer(metodo,ruta)
        if ruta==FASE:return self.fase
        if metodo=='GET' and ruta==SESION:return copy.deepcopy(self.sesion)
        if ruta in (PICK,BAN):return list(self.disponibles)
        if ruta.startswith(FICHA):return copy.deepcopy(self.fichas.get(int(ruta[len(FICHA):]),{}))
        if metodo=='PATCH':
            if self.rechazar:raise ErrorCliente('rechazo')
            if self.confirmar:self.sesion['actions'][0][0].update(datos)


class Seleccion(unittest.TestCase):
    def preparar(self,tipo='pick'):
        cliente=Cliente(tipo);control=ControlSeleccion(cliente)
        cfg=normalizar({});cfg['auto_'+tipo]=True;cfg['roles']['MIDDLE'][tipo]=[1,2,3]
        control.configurar(cfg,iniciar=False)
        return control,cliente

    def envios(self,c):return [p for p in c.llamadas if p[0]=='PATCH']

    def test_normaliza_config_sin_activar_por_valores_truthy(self):
        c=normalizar({'auto_pick':'true','auto_ban':1,'roles':{'MIDDLE':{'pick':[True,1,1],'ban':'abc'}}})
        self.assertFalse(c['auto_pick']);self.assertFalse(c['auto_ban'])
        self.assertEqual(c['roles']['MIDDLE']['pick'],[0,1,0]);self.assertEqual(len(c['roles']),5)

    def test_solo_una_confirmacion_de_turno_local(self):
        control,c=self.preparar();control.revisar();control.revisar()
        self.assertEqual(self.envios(c),[('PATCH',SESION+'/actions/7',{'championId':1,'completed':True})])
        self.assertEqual(control.estado,ESPERANDO) # turno ya completado
        self.assertTrue(all(ruta not in ('/lol-lobby/v2/lobby/matchmaking/search','/lol-matchmaking/v1/ready-check/accept') for _,ruta,_ in c.llamadas))

    def test_prioridad_salta_baneado_y_no_disponible(self):
        control,c=self.preparar();c.disponibles=[2,3];c.sesion['bans']={'theirTeamBans':[2]}
        control.revisar();self.assertEqual(self.envios(c)[0][2]['championId'],3)

    def test_pick_salta_campeones_ya_elegidos_hasta_agotar_preferencias(self):
        for ocupados,esperado in (([],1),([1],2),([1,2],3),([1,2,3],None)):
            with self.subTest(ocupados=ocupados):
                control,c=self.preparar()
                c.sesion['theirTeam']=[{'championId':v} for v in ocupados]
                control.revisar()
                if esperado is None:self.assertEqual(self.envios(c),[])
                else:self.assertEqual(self.envios(c)[0][2]['championId'],esperado)

    def test_pick_unica_preferencia_tomada_por_aliado_no_inventa_otro(self):
        control,c=self.preparar();cfg=normalizar(control.config);cfg['roles']['MIDDLE']['pick']=[1,0,0]
        control.configurar(cfg,iniciar=False);c.sesion['myTeam'][1]['championId']=1
        control.revisar();self.assertEqual(self.envios(c),[])

    def test_pick_rechazado_por_carrera_pasa_a_siguiente_si_ya_fue_elegido(self):
        control,c=self.preparar();c.rechazar=True;control.revisar()
        self.assertEqual(len(self.envios(c)),1)
        c.sesion['theirTeam']=[{'championId':1}];c.rechazar=False
        control.revisar();self.assertEqual([r[2]['championId'] for r in self.envios(c)],[1,2])

    def test_carrera_agota_prioridades_sin_elegir_fuera_de_lista(self):
        control,c=self.preparar();c.rechazar=True;control.revisar()
        c.sesion['theirTeam']=[{'championId':v} for v in (1,2,3)];c.rechazar=False
        control.revisar();self.assertEqual(len(self.envios(c)),1);self.assertEqual(control.estado,SIN_OPCIONES)

    def test_ban_respeta_hover_aliado(self):
        control,c=self.preparar('ban');c.sesion['myTeam'][1]['championPickIntent']=1
        control.revisar();self.assertEqual(self.envios(c)[0][2]['championId'],2)

    def test_intenciones_aliadas_saltan_prioridades_o_no_banean_sin_alternativa(self):
        for disponibles in ([1,2,3],[-1]):
            for prioridades,esperado in (([1,2,3],3),([1,2,0],None),([1,0,0],None)):
                with self.subTest(disponibles=disponibles,prioridades=prioridades):
                    control,c=self.preparar('ban');c.disponibles=disponibles
                    cfg=normalizar(control.config);cfg['roles']['MIDDLE']['ban']=prioridades
                    control.configurar(cfg,iniciar=False)
                    c.sesion['myTeam'][1]['championPickIntent']=1
                    c.sesion['myTeam'].append({'cellId':3,'championId':0,'championPickIntent':2})
                    c.fichas={i:self.ficha(i) for i in (1,2,3)}
                    control.revisar()
                    if esperado is None:
                        self.assertEqual(self.envios(c),[]);self.assertEqual(control.estado,SIN_OPCIONES)
                    else:self.assertEqual(self.envios(c)[0][2]['championId'],esperado)

    def test_hover_aliado_justo_antes_de_confirmar_impide_ban(self):
        control,c=self.preparar('ban');c.disponibles=[-1];c.fichas[1]=self.ficha(1);lecturas=[]
        def leer(m,r):
            if r==FICHA+'1':
                lecturas.append(r)
                if len(lecturas)==2:c.sesion['myTeam'][1]['championPickIntent']=1
        c.leer=leer;control.revisar();self.assertEqual(self.envios(c),[])

    def ficha(self,id,**cambios):
        d={'id':id,'disabled':False,'owned':False,'selectionStatus':{'isBanned':False,'pickedByOtherOrBanned':False,
             'banIntented':False,'banIntentedByMe':False,'selectedByMe':False}}
        d.update(cambios);return d

    def test_regresion_cliente_real_baneables_menos_uno_y_akali_habilitada(self):
        control,c=self.preparar('ban');c.disponibles=[-1]
        cfg=normalizar(control.config);cfg['roles']['MIDDLE']['ban']=[84,0,0];control.configurar(cfg,iniciar=False)
        c.fichas[84]=self.ficha(84)
        control.revisar()
        self.assertEqual(self.envios(c)[0][2],{'championId':84,'completed':True})
        self.assertEqual(sum(r==FICHA+'84' for _,r,_ in c.llamadas),2)
        self.assertEqual(control.estado,CONFIRMADO)

    def test_ficha_no_permite_ban_deshabilitado_baneado_ni_hover_aliado(self):
        for motivo in ('disabled','isBanned','pickedByOtherOrBanned','banIntented','selectedByMe','sin_estado','id_distinto','aliado'):
            control,c=self.preparar('ban');c.disponibles=[-1];c.fichas[1]=self.ficha(1)
            if motivo=='disabled':c.fichas[1]['disabled']=True
            elif motivo=='sin_estado':c.fichas[1].pop('selectionStatus')
            elif motivo=='id_distinto':c.fichas[1]['id']=4
            elif motivo=='aliado':c.sesion['myTeam'][1]['championPickIntent']=1
            else:c.fichas[1]['selectionStatus'][motivo]=True
            control.revisar();self.assertEqual(self.envios(c),[],motivo)

    def test_respaldo_respeta_prioridad_y_revalida_ficha(self):
        control,c=self.preparar('ban');c.disponibles=[-1]
        c.fichas={1:self.ficha(1,disabled=True),2:self.ficha(2),3:self.ficha(3)}
        control.revisar();self.assertEqual(self.envios(c)[0][2]['championId'],2)
        control,c=self.preparar('ban');c.disponibles=[-1];c.fichas[1]=self.ficha(1)
        lecturas=[]
        def leer(m,r):
            if r==FICHA+'1':
                lecturas.append(r)
                if len(lecturas)==2:c.fichas[1]['selectionStatus']['isBanned']=True
        c.leer=leer;control.revisar();self.assertEqual(self.envios(c),[])

    def test_no_amplia_lista_valida_ni_aplica_respaldo_a_picks(self):
        for tipo,ids in (('pick',[-1]),('ban',[4])):
            control,c=self.preparar(tipo);c.disponibles=ids;c.fichas[1]=self.ficha(1)
            control.revisar();self.assertEqual(self.envios(c),[])
            self.assertFalse(any(r.startswith(FICHA) for _,r,_ in c.llamadas))

    def test_cambio_manual_durante_ficha_final_impide_baneo(self):
        control,c=self.preparar('ban');c.disponibles=[-1];c.fichas[1]=self.ficha(1);lecturas=[]
        def leer(m,r):
            if r==FICHA+'1':
                lecturas.append(r)
                if len(lecturas)==2:c.sesion['actions'][0][0]['championId']=4
        c.leer=leer;control.revisar();self.assertEqual(self.envios(c),[])

    def test_manual_hover_o_accion_no_se_sobrescriben(self):
        for campo in ('hover','accion'):
            control,c=self.preparar()
            if campo=='hover':c.sesion['myTeam'][0]['championPickIntent']=4
            else:c.sesion['actions'][0][0]['championId']=4
            control.revisar();self.assertEqual(self.envios(c),[]);self.assertEqual(control.estado,MANUAL)

    def test_fuera_turno_o_fase_no_envia(self):
        for cambio in ('fase','timer','actor','completada','linea','tipo'):
            control,c=self.preparar();a=c.sesion['actions'][0][0]
            if cambio=='fase':c.fase='Matchmaking'
            elif cambio=='timer':c.sesion['timer']['phase']='PLANNING'
            elif cambio=='actor':a['actorCellId']=2
            elif cambio=='completada':a['completed']=True
            elif cambio=='linea':c.sesion['myTeam'][0]['assignedPosition']=''
            elif cambio=='tipo':a['type']='ban'
            control.revisar();self.assertEqual(self.envios(c),[],cambio)

    def test_cambio_de_turno_durante_consulta_no_envia(self):
        control,c=self.preparar()
        def leer(m,r):
            if r==PICK:c.sesion['actions'][0][0]['isInProgress']=False
        c.leer=leer;control.revisar();self.assertEqual(self.envios(c),[])

    def test_cambio_manual_o_config_durante_consulta_no_envia(self):
        for cambio in ('manual','config','stop'):
            control,c=self.preparar();stop=threading.Event()
            def leer(m,r):
                if r==PICK:
                    if cambio=='manual':c.sesion['myTeam'][0]['championPickIntent']=4
                    elif cambio=='config':control.configurar({},iniciar=False)
                    else:stop.set()
            c.leer=leer;control.revisar(stop);self.assertEqual(self.envios(c),[],cambio)

    def test_no_opciones_no_inventa_campeon(self):
        control,c=self.preparar();c.disponibles=[4]
        control.revisar();self.assertEqual(self.envios(c),[]);self.assertEqual(control.estado,SIN_OPCIONES)

    def test_rechazo_o_sin_confirmacion_no_repite_ni_afirma_exito(self):
        for rechazo in (True,False):
            control,c=self.preparar();c.rechazar=rechazo;c.confirmar=False
            control.revisar();control.revisar()
            self.assertEqual(len(self.envios(c)),1);self.assertEqual(control.estado,ERROR if rechazo else ENVIADO)

    def test_desactivado_no_hace_peticiones(self):
        c=Cliente();control=ControlSeleccion(c);control.revisar();self.assertEqual(c.llamadas,[])

    def test_desactivar_con_peticion_en_curso_conserva_estado_apagado(self):
        control,c=self.preparar()
        def leer(m,r):
            if m=='PATCH':control.configurar({},iniciar=False)
        c.leer=leer;control.revisar();self.assertEqual(control.estado,APAGADO)

    def test_catalogo_local_y_sprites_completos(self):
        from PIL import Image
        catalogo=cargar_catalogo();ids=[]
        for c in catalogo['champions']:
            ids.append(c['id']);d=c['image']
            with Image.open(carpeta_catalogo()/d['sprite']) as im:
                self.assertLessEqual(d['x']+d['w'],im.width);self.assertLessEqual(d['y']+d['h'],im.height)
        self.assertGreater(len(ids),170);self.assertEqual(len(ids),len(set(ids)))

    def test_transporte_solo_patch_acotado(self):
        c=ClienteLCU(lambda:Credenciales(12345,'privado'));respuesta=Mock();respuesta.read.return_value=b''
        c.abridor.open=MagicMock();c.abridor.open.return_value.__enter__.return_value=respuesta
        c.pedir('PATCH',SESION+'/actions/7',{'championId':1,'completed':True})
        r=c.abridor.open.call_args.args[0]
        self.assertEqual(r.full_url,'https://127.0.0.1:12345'+SESION+'/actions/7')
        self.assertEqual(json.loads(r.data),{'championId':1,'completed':True})
        c.pedir('GET',FICHA+'84')
        self.assertTrue(c.abridor.open.call_args.args[0].full_url.endswith(FICHA+'84'))
        for ruta in (FICHA+'0',FICHA+'-1',FICHA+'84/other',FICHA+'84?x=1',FICHA+'100000'):
            with self.assertRaises(ValueError):c.pedir('GET',ruta)
        for ruta,datos in ((SESION,{'championId':1,'completed':True}),(SESION+'/actions/-1',{'championId':1,'completed':True}),
                           (SESION+'/actions/7',{'championId':True,'completed':True}),(SESION+'/actions/7',{'championId':1,'completed':False}),
                           (SESION+'/actions/7',{'championId':1,'completed':True,'extra':1})):
            with self.assertRaises(ValueError):c.pedir('PATCH',ruta,datos)

    def test_estados_traducidos(self):
        from idiomas import ui
        for estado in ESTADOS:
            for idioma in ('en','pt','ja'):self.assertNotEqual(ui(estado,idioma),estado)


if __name__=='__main__':unittest.main()
