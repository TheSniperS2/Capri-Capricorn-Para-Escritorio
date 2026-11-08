import threading
import time
import unittest
from unittest.mock import Mock,patch
from core import interpretar
from fortnite import ControlFortnite,normalizar,Texto,Pantalla,ErrorFortnite,EQUIPOS,MODOS


def pantalla(equipo='duo',modo='br',cola=False,extra=()):
    labels=[Texto('TAQUILLA',(160,20,120,25))]
    if cola:labels.extend((Texto('EMPAREJAMIENTO',(20,640,270,25)),Texto('CANCELAR',(20,790,150,35))))
    else:labels.extend((Texto('JUGAR',(20,790,150,35)),Texto(EQUIPOS[equipo][1][0],(20,710,130,25)),Texto(MODOS[modo][1][0],(20,660,270,25))))
    return Pantalla(123,(0,0,1600,900),tuple(labels)+tuple(extra),time.monotonic())


def menu(equipo='duo'):
    textos=(Texto('CONSTRUCCIÓN',(1000,90,170,25)),Texto('CERO CONSTRUCCIÓN',(1250,90,240,25)),
            Texto(EQUIPOS[equipo][1][0],(1000,330,170,25)))
    botones=tuple(Texto(k,(1200+i*70,320,60,60)) for i,k in enumerate(('solo','duo','trio','squad')))
    return Pantalla(123,(0,0,1600,900),textos,time.monotonic(),botones)


class Fortnite(unittest.TestCase):
    def control(self,frames,config=None):
        v=Mock();v.capturar.side_effect=frames;c=ControlFortnite(v);c.configurar(config)
        # La transición no ralentiza las pruebas ni ejecuta entradas reales.
        c._stop=Mock();c._stop.is_set.return_value=False;c._stop.wait.return_value=False
        return c,v

    def test_defaults_independientes_y_config_invalida(self):
        for config in (None,[],{'modo':[],'equipo':{}},{'modo':'br;code','equipo':'admin'}):
            self.assertEqual(normalizar(config),{'modo':'actual','equipo':'actual'})
        c,v=self.control([]);c.configurar({'modo':'cero','equipo':'squad'})
        v.capturar.assert_not_called();v.pulsar.assert_not_called()
        self.assertEqual(normalizar({}),{'modo':'actual','equipo':'actual'})

    def test_interpretacion_explicitamente_fortnite_y_negaciones(self):
        for orden,tipo in (('Capri, busca partida en Fortnite.','buscar'),('tira la cola en fortnite','buscar'),
                           ('cancela la búsqueda en Fortnite','cancelar'),('aplica mis opciones en Fortnite','preparar')):
            self.assertEqual(interpretar(orden).tipo,'fortnite_'+tipo)
        for texto in ('no busques partida en fortnite','cómo buscar partida en fortnite','busca skins en fortnite','busca partida en valorant'):
            orden=interpretar(texto);self.assertFalse(orden and orden.tipo.startswith('fortnite_'))

    def test_busca_una_vez_con_opciones_verificadas(self):
        p=pantalla();q=pantalla(cola=True)
        c,v=self.control([p,p,q],{'modo':'br','equipo':'duo'})
        self.assertIn('confirmó',c.ejecutar('fortnite_buscar'))
        self.assertEqual(v.pulsar.call_count,1);self.assertEqual(v.pulsar.call_args.args[1].texto,'JUGAR')
        self.assertEqual(v.capturar.call_args_list[0].kwargs,{'activar':True})

    def test_aplicar_y_configurar_no_buscan_y_no_crean_vigilancia(self):
        c,v=self.control([pantalla()],{'equipo':'duo','modo':'br'})
        with patch('threading.Thread') as hilo:
            self.assertIn('espera tu orden',c.ejecutar('fortnite_preparar'))
            v.pulsar.assert_not_called();hilo.assert_not_called()

    def test_transicion_al_restaurar_solo_repite_lecturas_antes_de_buscar(self):
        transicion=Pantalla(123,(0,0,1600,900),(Texto('TIENDA',(200,20,100,25)),),time.monotonic())
        c,v=self.control([transicion,pantalla(),pantalla(),pantalla(cola=True)])
        self.assertIn('confirmó',c.ejecutar('fortnite_buscar'))
        self.assertEqual(v.pulsar.call_count,1);self.assertEqual(v.pulsar.call_args.args[1].texto,'JUGAR')
        self.assertEqual([a.kwargs['activar'] for a in v.capturar.call_args_list],[True,False,False,False])

    def test_lobby_restaurado_espera_el_resumen_de_las_preferencias(self):
        incompleta=Pantalla(123,(0,0,1600,900),(Texto('TIENDA',(200,20,100,25)),Texto('JUGAR',(20,790,150,35))),time.monotonic())
        c,v=self.control([incompleta,pantalla(equipo='solo',modo='cero')],{'modo':'cero','equipo':'solo'})
        self.assertIn('espera tu orden',c.ejecutar('fortnite_preparar'));v.pulsar.assert_not_called()

    def test_minimizado_con_opciones_abiertas_vuelve_al_lobby_antes_de_actuar(self):
        c,v=self.control([menu(),pantalla()])
        self.assertIn('espera tu orden',c.ejecutar('fortnite_preparar'))
        v.volver.assert_called_once();v.pulsar.assert_not_called()

    def test_cambia_tamano_luego_confirma_antes_de_jugar(self):
        for elegido in ('solo','trio','squad'):
            with self.subTest(elegido=elegido):
                final=pantalla(equipo=elegido)
                c,v=self.control([pantalla(),menu(),menu(elegido),final,final,pantalla(cola=True)],{'equipo':elegido})
                self.assertIn('confirmó',c.ejecutar('fortnite_buscar'))
                self.assertEqual([a.args[1].texto for a in v.pulsar.call_args_list],['battle royale',elegido,'JUGAR'])

    def test_cambia_experiencia_y_verifica_resultado(self):
        final=pantalla(modo='cero')
        c,v=self.control([pantalla(),menu(),menu(),final,final,pantalla(cola=True)],{'modo':'cero'})
        self.assertIn('confirmó',c.ejecutar('fortnite_buscar'))
        self.assertEqual([a.args[1].texto for a in v.pulsar.call_args_list],['battle royale','CERO CONSTRUCCIÓN','JUGAR'])

    def test_tarjeta_del_lobby_partida_en_lineas_e_iconos(self):
        for equipo,lineas in (('solo',('Construcción, En','solitario')),('squad',('Construcción, En','escuadrón, Llenar')),('duo',('Cero construcción,','• En dúo')),('trio',('Cero construcción,','• En trío'))):
            p=Pantalla(1,(0,0,1920,1080),tuple(Texto(s,(149,653+i*30,250,24)) for i,s in enumerate(lineas)),time.monotonic())
            self.assertEqual(ControlFortnite._opcion(p,EQUIPOS)[0],equipo)
            self.assertEqual(ControlFortnite._opcion(p,MODOS)[0],'cero' if lineas[0].startswith('Cero') else 'br')

    def test_menu_incompleto_no_usa_coordenadas_ni_pulsa_jugar(self):
        q=Pantalla(123,(0,0,1600,900),(),time.monotonic())
        c,v=self.control([pantalla(),q,q,q,q],{'equipo':'solo'})
        self.assertIn('No pude leer',c.ejecutar('fortnite_buscar'))
        self.assertEqual(v.pulsar.call_count,1)
        self.assertNotEqual(v.pulsar.call_args.args[1].texto,'JUGAR')

    def test_manual_cancela_sin_reintentar_ni_tocar_jugar(self):
        c,v=self.control([pantalla(cola=True),pantalla()])
        self.assertIn('cancelación',c.ejecutar('fortnite_cancelar'));self.assertEqual(v.pulsar.call_count,1)
        self.assertEqual(v.pulsar.call_args.args[1].texto,'CANCELAR')

    def test_no_duplica_cola_y_no_cancela_sin_cola(self):
        c,v=self.control([pantalla(cola=True)]);self.assertIn('ya está',c.ejecutar('fortnite_buscar'));v.pulsar.assert_not_called()
        c,v=self.control([pantalla()]);self.assertIn('No pude confirmar',c.ejecutar('fortnite_cancelar'));v.pulsar.assert_not_called()

    def test_no_inventa_exito_ni_reintenta_jugar(self):
        p=pantalla();c,v=self.control([p]*6)
        self.assertIn('todavía no pude confirmar',c.ejecutar('fortnite_buscar'));self.assertEqual(v.pulsar.call_count,1)

    def test_no_pulsa_si_foco_restriccion_ambiguedad_o_cambio(self):
        c,v=self.control([]);v.capturar.side_effect=ErrorFortnite('Foco perdido')
        self.assertEqual(c.ejecutar('fortnite_buscar'),'Foco perdido');v.pulsar.assert_not_called()
        for p in (pantalla(extra=(Texto('JUGAR',(200,790,150,35)),)),pantalla(extra=(Texto('MATCHMAKING ERROR',(30,500,300,25)),))):
            c,v=self.control([p]*5);c.ejecutar('fortnite_buscar');v.pulsar.assert_not_called()
        c,v=self.control([pantalla(),pantalla(equipo='trio')],{'equipo':'duo'})
        self.assertIn('cambiaron',c.ejecutar('fortnite_buscar'));v.pulsar.assert_not_called()

    def test_cancelacion_por_escape_y_cierre_impiden_clics(self):
        c,v=self.control([]);stop=threading.Event();stop.set()
        with self.assertRaises(InterruptedError):c.ejecutar('fortnite_buscar',cancelar=stop)
        v.capturar.assert_not_called();v.pulsar.assert_not_called()
        c=ControlFortnite(v);c.cerrar()
        with self.assertRaises(InterruptedError):c.ejecutar('fortnite_buscar')
        v.capturar.assert_not_called()


if __name__=='__main__':unittest.main()
