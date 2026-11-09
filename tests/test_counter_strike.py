import threading,time,unittest
from dataclasses import replace
from unittest.mock import Mock,patch
from core import interpretar
from fortnite import Texto
from counter_strike import ControlCS2,PantallaCS2,MapaVisible,normalizar,ErrorCS2


class Juego:
    def __init__(self):
        self.seleccion={'Nuke'};self.cola=False;self.clics=[];self.ver=[];self.completa=True;self.online=True;self.competitivo=True;self.extra=[];self.ignorar=False
    def capturar(self,activar=False):
        self.ver.append(activar);t=Texto('Cancelar' if self.cola else 'Go',(1500,950,230,50))
        mapas=tuple(MapaVisible(n,Texto(n,(400+i*300,190,25,25)),n in self.seleccion) for i,n in enumerate(('Mirage','Nuke','Dust II')))
        textos=(Texto('MATCHMAKING',(800,50,200,25)),Texto('COMPETITIVE',(800,100,200,25)),t,*self.extra)
        if self.cola:textos=(*textos,Texto('Searching for players',(1300,800,300,30)))
        return PantallaCS2(123,(0,0,1920,1080),textos,time.monotonic(),(),mapas,self.completa,self.online,self.competitivo)
    def pulsar(self,p,t):
        self.clics.append(t.texto)
        if self.ignorar:return
        if t.texto=='Go':self.cola=True
        elif t.texto=='Cancelar':self.cola=False
        elif t.texto in ('Mirage','Nuke','Dust II'):
            if t.texto in self.seleccion:self.seleccion.remove(t.texto)
            else:self.seleccion.add(t.texto)


class CS2(unittest.TestCase):
    def setUp(self):
        self.v=Juego();self.c=ControlCS2(self.v);self.c.configurar({'mapas':['Mirage','Dust II']});self.c._stop.wait=Mock(return_value=False)
        self.addCleanup(self.c.cerrar)
    def test_normalizador_preferencias_vacias_y_parser_sin_negaciones_ni_citas(self):
        self.assertEqual(normalizar(None),{'mapas':[],'detectados':[]})
        self.assertEqual(normalizar({'mapas':['dust2','Dust II','Nuke',None,19]})['mapas'],['Dust II','Nuke'])
        for texto,tipo in (('busca partida en counter strike','cs2_buscar'),('busca partida en csgo','cs2_buscar'),('cancela la cola en cs2','cs2_cancelar'),('aplica mis mapas en cs2','cs2_preparar'),('lee los mapas de cs2','cs2_leer'),('configura counter strike 2','cs2_panel')):
            self.assertEqual(interpretar(texto).tipo,tipo)
        for t in ('no busques partida en cs2','como busco partida en cs2','"busca partida en cs2"','busca partida en cs2 y compra una skin'):
            o=interpretar(t);self.assertTrue(o is None or not o.tipo.startswith('cs2_'))
    def test_aplica_exactamente_sin_buscar_y_busca_una_vez(self):
        r=self.c.ejecutar('cs2_preparar');self.assertIn('confirmados',r)
        self.assertEqual(self.v.clics,['Mirage','Dust II','Nuke']);self.assertFalse(self.v.cola)
        self.assertEqual(self.v.seleccion,{'Mirage','Dust II'});self.assertEqual(self.v.ver[0],True);self.assertFalse(any(self.v.ver[1:]))
        self.c.ejecutar('cs2_buscar');self.assertTrue(self.v.cola);self.assertEqual(self.v.clics.count('Go'),1)
        self.c.ejecutar('cs2_buscar');self.assertEqual(self.v.clics.count('Go'),1)
    def test_cancelar_no_reencola_ni_cambia_mapas(self):
        self.v.cola=True;self.c.ejecutar('cs2_cancelar');self.assertEqual(self.v.clics,['Cancelar']);self.assertFalse(self.v.cola)
        self.c.ejecutar('cs2_cancelar');self.assertEqual(self.v.clics,['Cancelar']);self.assertEqual(self.v.seleccion,{'Nuke'})
    def test_sin_preferencias_o_mapa_no_visible_no_pulsa(self):
        self.c.configurar({});self.c.ejecutar('cs2_buscar');self.assertEqual(self.v.ver,[])
        self.c.configurar({'mapas':['Cache']});self.c.ejecutar('cs2_buscar');self.assertEqual(self.v.clics,[])
    def test_no_pulsa_con_ficha_incompleta_confirmacion_o_restriccion(self):
        self.v.completa=False;self.c.ejecutar('cs2_buscar');self.assertEqual(self.v.clics,[])
        self.v.completa=True
        for s in ('ACCEPT','RECONNECT','Competitive cooldown'):
            self.v.extra=[Texto(s,(700,400,200,50))];self.c.ejecutar('cs2_buscar');self.assertEqual(self.v.clics,[])
    def test_click_no_confirmado_no_se_repite_ni_busca(self):
        self.v.ignorar=True;r=self.c.ejecutar('cs2_buscar');self.assertIn('No pude confirmar',r);self.assertEqual(self.v.clics,['Mirage'])
    def test_leer_mapas_no_modifica_el_juego(self):
        self.c.ejecutar('cs2_leer');self.assertEqual(self.c.catalogo,('Mirage','Nuke','Dust II'));self.assertEqual(self.v.clics,[])
    def test_aceptacion_manual_no_envia_acciones(self):
        self.assertIn('manual',self.c.ejecutar('cs2_aceptar'));self.assertEqual(self.v.ver,[]);self.assertEqual(self.v.clics,[])
    def test_cancelacion_o_preferencias_cambiadas_detienen_acciones(self):
        stop=threading.Event();stop.set()
        with self.assertRaises(InterruptedError):self.c.ejecutar('cs2_buscar',cancelar=stop)
        self.assertEqual(self.v.clics,[])
        capturar=self.v.capturar
        def cambiar(*a,**k):
            p=capturar(*a,**k);self.c.configurar({'mapas':['Nuke']});return p
        self.v.capturar=cambiar;r=self.c.ejecutar('cs2_buscar');self.assertIn('cambiaron',r);self.assertEqual(self.v.clics,[])
    def test_perder_foco_no_intenta_otro_click(self):
        self.v.pulsar=Mock(side_effect=ErrorCS2('Counter-Strike perdió el foco.'))
        r=self.c.ejecutar('cs2_buscar');self.assertIn('perdió el foco',r);self.v.pulsar.assert_called_once()


if __name__=='__main__':unittest.main()
