import random
import threading
import time
import unittest
from unittest.mock import Mock,patch
from core import interpretar
from fortnite import Pantalla,Texto
from reacciones_skins import GustosCapri,Lectura,MonitorSkins,catalogo,normalizar
from skins_dialogos import frases,opinion,GENERICAS
from skins_fuentes import FuentesSkins
from valorant_cliente import permitida,ClienteValorant,SesionRiot

YO='00000000-0000-0000-0000-000000000001'
OTRO='00000000-0000-0000-0000-000000000002'


def skin(perfil,juego='valorant'):
    return next(s for s in catalogo() if s['perfil']==perfil and s['juego']==juego)


def ficha(nombres=('PHILIP J. FRV',),tipo=True):
    textos=[Texto('CASILLERO',(600,60,190,35)),Texto('EDITAR ESTILO',(1400,700,220,30))]
    if tipo:textos.append(Texto('ATUENDO - ESTILO FORTNITE',(890,890,400,25)))
    textos.extend(Texto(n,(890,925+i*30,400,25)) for i,n in enumerate(nombres))
    return Pantalla(123,(0,0,1920,1080),tuple(textos),time.monotonic())


class Skins(unittest.TestCase):
    def test_catalogo_publico_dialogos_y_preferencias_vacias(self):
        self.assertEqual(normalizar({}),{'activo':False,'valorant':True,'fortnite':True,'frecuencia':'equilibrada'})
        self.assertFalse(normalizar({'activo':'true'})['activo']);self.assertEqual(normalizar({'frecuencia':[]})['frecuencia'],'equilibrada')
        self.assertGreater(len(catalogo()),4000)
        for s in catalogo():
            self.assertNotIn('jugador',s);self.assertTrue(s['ids'])
            for idioma in ('es','en','pt','ja'):
                self.assertTrue(s['nombres'][idioma]);self.assertGreaterEqual(len(frases(s,idioma)),2)
                self.assertTrue(all(len(t)<430 for t in frases(s,idioma)))

    def test_parser_especifico_sin_convertir_compras_ni_negaciones(self):
        for texto,juego in (('Capri, mira mi skin en Fortnite.','fortnite'),('qué opinas de mi skin de Valorant','valorant'),('mira mis skins',''),
                            ('¿qué te parece esta skin?',''),('qué te parece esta skin de valo','valorant'),
                            ('qué te parecen estas skins en fortnite','fortnite'),
                            ('look at my skin in valorant','valorant'),('what do you think of this skin',''),('veja minha skin no fortnite','fortnite')):
            o=interpretar(texto);self.assertEqual((o.tipo,o.valor),('skins_opinar',juego))
        for t in ('no mires mi skin','cómo miras mi skin','compra una skin en Fortnite','busca partida en valorant'):
            o=interpretar(t);self.assertFalse(o and o.tipo=='skins_opinar')

    def test_dos_muestras_y_confirmacion_real_antes_de_gastar_cadencia(self):
        reloj=Mock(return_value=0);m=GustosCapri(reloj,random.Random(1));l=Lectura('valorant','equipamiento',(skin('rgx'),))
        self.assertIsNone(m.observar(l));p=m.observar(l);self.assertIsNotNone(p)
        self.assertIsNone(m.observar(l));self.assertLess(m._ultima,0)
        self.assertTrue(m.confirmar(p));self.assertEqual(m._ultima,0);self.assertIsNone(m.observar(l))
        otro=Lectura('valorant','equipamiento',(skin('oni'),));m.observar(otro);self.assertIsNone(m.observar(otro))
        reloj.return_value=9;p=m.observar(otro);self.assertIsNotNone(p);self.assertNotEqual(p.texto,l.skins[0]['nombres']['es'])

    def test_variantes_de_dialogo_y_reencuentro_solo_tras_pausa(self):
        reloj=Mock(return_value=0);m=GustosCapri(reloj,random.Random(1));l=Lectura('fortnite','ficha',(skin('fry','fortnite'),))
        p=m.observar(l,manual=True);m.confirmar(p,manual=True)
        q=m.observar(l,manual=True);self.assertNotEqual(p.texto,q.texto);m.confirmar(q,manual=True)
        otra=Lectura('fortnite','ficha',(skin('v','fortnite'),));reloj.return_value=200;m.observar(otra);p=m.observar(otra);m.confirmar(p)
        reloj.return_value=202;m.observar(l);self.assertIsNone(m.observar(l))
        reloj.return_value=210;p=m.observar(l);self.assertIn('Otra vez',p.texto)
        m.confirmar(p);reloj.return_value=5000;self.assertIsNone(m.observar(l))

    def test_genericas_tres_gustos_estables_y_reencuentros_sin_contradiccion(self):
        genericas=[s for s in catalogo() if s['perfil']=='generica']
        for juego in ('fortnite','valorant'):
            self.assertEqual({opinion(s) for s in genericas if s['juego']==juego},{'buena','neutral','mala'})
        for gusto in ('buena','neutral','mala'):
            s=next(s for s in genericas if opinion(s)==gusto)
            for idioma in ('es','en','pt','ja'):
                esperadas={t.format(nombre=s['nombres'][idioma]) for t in GENERICAS[idioma][gusto]}
                for semilla in range(6):
                    m=GustosCapri(azar=random.Random(semilla))
                    p=m.observar(Lectura(s['juego'],'ficha',(s,)),idioma=idioma,manual=True)
                    self.assertIn(p.texto,esperadas)
                self.assertTrue(all(t.endswith(tuple(esperadas)) for t in frases(s,idioma,reencuentro=True)))

    def test_goku_black_generica_reconocida_y_exacta_prevalece_sobre_parecidos(self):
        from skins_fuentes import resolver_nombres
        f=FuentesSkins();l=f.fortnite_visible(ficha(('GOKU BLACK',)))
        self.assertEqual(l.skins[0]['id'],'Character_DualParadox');self.assertEqual(l.skins[0]['perfil'],'generica')
        self.assertIn('Goku Black',frases(l.skins[0],'en')[0])
        exacta=resolver_nombres('fortnite',{'goku black'})
        self.assertEqual(set(exacta),{'Character_DualParadox'})
        self.assertIsNone(f.fortnite_visible(ficha(('PHILIP J. FRY', 'GOKU BLACK'))))

    def test_rotulo_atuendo_separado_por_ocr_no_se_confunde_con_pestana(self):
        from fortnite_vision import VistaFortnite
        f=FuentesSkins();p=ficha(('GOKU BLACK',))
        textos=tuple(Texto(t.texto.replace('ATUENDO','A TUENDO'),t.rect) for t in p.textos)
        p=Pantalla(p.ventana,p.rect,(Texto('C ATUENDO',(989,132,183,22)),*textos),p.momento)
        self.assertEqual(f.fortnite_visible(p).skins[0]['id'],'Character_DualParadox')
        regiones=VistaFortnite.regiones_ficha(p)
        self.assertTrue(regiones);self.assertGreater(regiones[0][1],700)

    def test_cambiar_seleccion_reacciona_sin_espera_larga_y_descarta_plan_anterior(self):
        reloj=Mock(return_value=0);m=GustosCapri(reloj)
        a=Lectura('valorant','equipamiento',(skin('rgx'),skin('oni')))
        m.observar(a);p=m.observar(a);m.confirmar(p)
        nueva=next(s for s in catalogo() if s['juego']=='valorant' and s['perfil']=='generica')
        b=Lectura('valorant','equipamiento',(*a.skins,nueva))
        reloj.return_value=9;m.observar(b);q=m.observar(b)
        self.assertEqual(q.skin['id'],nueva['id'])
        m.observar(a);self.assertFalse(m.confirmar(q))
        for frecuencia,intervalo in (('discreta',18),('equilibrada',8),('entusiasta',3)):
            m=GustosCapri(reloj);m.observar(a);m.confirmar(m.observar(a))
            reloj.return_value+=intervalo-1;m.observar(b);self.assertIsNone(m.observar(b,frecuencia))
            reloj.return_value+=1;self.assertIsNotNone(m.observar(b,frecuencia))

    def test_gusto_es_igual_entre_procesos_y_no_depende_de_hash_aleatorio(self):
        import os,subprocess,sys
        codigo="from reacciones_skins import catalogo;from skins_dialogos import opinion;print([(s['id'],opinion(s)) for s in catalogo() if s['perfil']=='generica'][::137])"
        salidas=[subprocess.check_output([sys.executable,'-c',codigo],env={**os.environ,'PYTHONHASHSEED':n}) for n in ('1','937')]
        self.assertEqual(*salidas)

    def test_plan_caducado_o_interrumpido_no_se_confirma(self):
        reloj=Mock(return_value=0);m=GustosCapri(reloj);l=Lectura('valorant','equipamiento',(skin('rgx'),))
        m.observar(l);p=m.observar(l);reloj.return_value=19;self.assertFalse(m.confirmar(p))
        m.anular();self.assertFalse(m.confirmar(p));self.assertIsNone(m.observar(l))

    def test_fortnite_nombre_real_ocr_una_letra_y_contexto(self):
        f=FuentesSkins();l=f.fortnite_visible(ficha());self.assertEqual(l.skins[0]['perfil'],'fry')
        self.assertIsNone(f.fortnite_visible(ficha(tipo=False)))
        self.assertIsNone(f.fortnite_visible(ficha(('PHILIP J. XXX',))))
        self.assertIsNone(f.fortnite_visible(ficha(('PHILIP J. FRY','JOHNNY SILVERHAND'))))
        self.assertIsNone(f.fortnite_visible(ficha(('PHILIP',))))
        p=ficha(('JOHNNY','SILVERHAND'));self.assertEqual(f.fortnite_visible(p).skins[0]['perfil'],'johnny')

    def test_ocr_no_confunde_chat_navegacion_y_pistas_de_otros_paneles(self):
        f=FuentesSkins();p=ficha(('Sin nombre reconocido',))
        p=Pantalla(p.ventana,p.rect,p.textos+(Texto('PHILIP J. FRY',(20,250,300,25)),),p.momento)
        self.assertIsNone(f.fortnite_visible(p))

    def test_valorant_lee_solo_equipamiento_propio_y_no_actua(self):
        s=skin('rgx');c=Mock();c.jugador=YO
        gun={'ID':s['arma_id'],'SkinID':s['id'],'SkinLevelID':s['ids'][-1]}
        def pedir(m,r):
            self.assertEqual(m,'GET')
            return {'Subject':YO,'Guns':[gun]} if r.endswith('playerloadout') else None
        c.pedir.side_effect=pedir;f=FuentesSkins(cliente=c);l=f.leer('valorant')
        self.assertEqual(l.skins[0]['id'],s['id']);self.assertNotIn(YO,repr(l));self.assertEqual(c.pedir.call_count,5)
        c.pedir.side_effect=lambda m,r:{'Subject':OTRO,'Guns':[gun]} if r.endswith('playerloadout') else None
        self.assertIsNone(f.leer('valorant'))
        c.pedir.reset_mock();c.pedir.side_effect=None;c.pedir.return_value={'MatchID':'partida'}
        self.assertIsNone(f.leer('valorant'));self.assertEqual(c.pedir.call_count,1)

    def test_valorant_ids_incompatibles_no_inventan_skin(self):
        s=skin('rgx');otro=skin('oni');c=Mock();c.jugador=YO
        def pedir(m,r):return {'Subject':YO,'Guns':[{'ID':s['arma_id'],'SkinID':s['id'],'ChromaID':otro['ids'][-1]}]} if r.endswith('playerloadout') else None
        c.pedir.side_effect=pedir;f=FuentesSkins(cliente=c);self.assertEqual(f.leer('valorant').skins,())

    def test_valorant_ficha_visible_prioritaria_y_no_escoge_otra_si_no_identifica(self):
        equipada=skin('rgx');vista=next(s for s in catalogo() if s['juego']=='valorant' and s['perfil']=='generica' and s['arma']=='Vandal')
        c=Mock();c.jugador=YO
        c.pedir.side_effect=lambda m,r:{'Subject':YO,'Guns':[{'ID':equipada['arma_id'],'SkinID':equipada['id']}]} if r.endswith('playerloadout') else None
        v=Mock();p=Pantalla(5,(0,0,1920,1080),(Texto('COLECCIÓN',(40,50,200,35)),Texto('EQUIPAR',(700,900,200,30)),Texto(vista['nombres']['es'],(650,280,500,45))),time.monotonic())
        v.capturar.return_value=p;f=FuentesSkins(cliente=c,vista_valorant=v)
        l=f.leer('valorant',manual=True);self.assertEqual(l.skins[0]['id'],vista['id']);self.assertEqual(l.contexto,'ficha')
        self.assertFalse(any(x.args[1].endswith('playerloadout') for x in c.pedir.call_args_list))
        v.capturar.return_value=Pantalla(p.ventana,p.rect,p.textos[:2]+(Texto('Nombre ilegible',(650,280,500,45)),),p.momento)
        self.assertIsNone(f.leer('valorant',manual=True))
        v.pulsar.assert_not_called();v.volver.assert_not_called()
        v.capturar.return_value=Pantalla(p.ventana,p.rect,(*p.textos,Texto(equipada['nombres']['es'],(650,360,500,45))),p.momento)
        self.assertIsNone(f.leer('valorant',manual=True))

    def test_valorant_manual_no_elige_arma_arbitraria_y_genericas_por_id(self):
        elegidas=[s for s in catalogo() if s['juego']=='valorant' and s['perfil']=='generica'][:2]
        c=Mock();c.jugador=YO
        c.pedir.side_effect=lambda m,r:{'Subject':YO,'Guns':[{'ID':s['arma_id'],'SkinID':s['id'],'SkinLevelID':s['ids'][-1]} for s in elegidas]} if r.endswith('playerloadout') else None
        f=FuentesSkins(cliente=c);self.assertEqual({s['id'] for s in f.leer('valorant').skins},{s['id'] for s in elegidas})
        self.assertIsNone(f.leer('valorant',manual=True))

    def test_pregunta_sin_juego_prioriza_juego_visible_sobre_preferencia_de_cola(self):
        f=Mock();f.primer_plano.return_value='fortnite';f.leer.return_value=Lectura('fortnite','ficha',(skin('fry','fortnite'),))
        m=MonitorSkins(Mock(),f)
        try:
            m.opinar(preferido='valorant');f.leer.assert_called_once_with('fortnite',manual=True)
        finally:m.cerrar()

    def test_no_reacciona_si_empieza_partida_durante_la_lectura_del_loadout(self):
        s=skin('rgx');c=Mock();c.jugador=YO;conteo=[0]
        def pedir(m,r):
            if r.endswith('playerloadout'):return {'Subject':YO,'Guns':[{'ID':s['arma_id'],'SkinID':s['id']}]}
            if r.startswith('/core-game/'):
                conteo[0]+=1
                return {'MatchID':'nueva'} if conteo[0]>1 else None
            return None
        c.pedir.side_effect=pedir;self.assertIsNone(FuentesSkins(cliente=c).leer('valorant'))

    def test_transporte_usa_pd_y_no_permite_cambiar_loadout_ni_leer_otra_cuenta(self):
        ruta=f'/personalization/v2/players/{YO}/playerloadout'
        self.assertTrue(permitida('GET',ruta,YO));self.assertFalse(permitida('GET',ruta,OTRO))
        for m in ('PUT','POST','DELETE'):self.assertFalse(permitida(m,ruta,YO))
        c=ClienteValorant(obtener=lambda:SesionRiot(YO,'token','entitlement','latam','na','release-13.09'))
        with patch('valorant_cliente._json',return_value={}) as leer:
            c.pedir('GET',ruta)
        self.assertEqual(leer.call_args.args[1].full_url,'https://pd.na.a.pvp.net'+ruta)

    def test_fortnite_nunca_activa_ventana_para_observar(self):
        v=Mock();v.capturar.return_value=ficha();f=FuentesSkins(vista=v)
        with patch.object(f,'primer_plano',return_value='fortnite'):
            self.assertIsNotNone(f.leer('fortnite'));v.capturar.assert_called_once_with(activar=False)
        v.reset_mock()
        with patch.object(f,'primer_plano',return_value=''):
            self.assertIsNone(f.leer('fortnite'));v.capturar.assert_not_called()
        v.pulsar.assert_not_called();v.volver.assert_not_called()
        with patch.object(f,'primer_plano',return_value=''):
            self.assertIsNotNone(f.leer('fortnite',manual=True));v.capturar.assert_called_once_with(activar=True)

    def test_monitor_descarta_desactivacion_cambio_juego_y_conversacion(self):
        fuente=Mock();fuente.primer_plano.return_value='valorant';m=MonitorSkins(Mock(),fuente)
        m.configurar({'activo':True},iniciar=False);m.permitir(True);l=Lectura('valorant','equipamiento',(skin('rgx'),))
        m.motor.observar(l);p=m.motor.observar(l);version=m._version
        fuente.primer_plano.return_value='fortnite';self.assertFalse(m.aceptar(version,p))
        fuente.primer_plano.return_value='valorant';m.permitir(False);self.assertFalse(m.aceptar(version,p))
        m.permitir(True);m.motor.observar(l);p=m.motor.observar(l);version=m._version
        self.assertTrue(m.aceptar(version,p));self.assertIs(m.ultima,p)
        m.configurar({},iniciar=False);self.assertFalse(m.aceptar(version,p));m.cerrar()

    def test_manual_espera_la_transicion_sin_repetir_restauracion(self):
        v=Mock();v.capturar.side_effect=[ficha(('Todavía cargando',)),ficha()];f=FuentesSkins(vista=v)
        with patch.object(f,'primer_plano',return_value='fortnite'),patch('skins_fuentes.time.sleep'):
            self.assertEqual(f.leer('fortnite',manual=True).skins[0]['perfil'],'fry')
        self.assertEqual([c.kwargs for c in v.capturar.call_args_list],[{'activar':True},{'activar':False}])
        v.pulsar.assert_not_called();v.volver.assert_not_called()

    def test_manual_casillero_seleccion_con_nombre_truncado_usa_lectura_ampliada(self):
        v=Mock();v.capturar.return_value=ficha(('PHILIP Z',))
        # El OCR ampliado recupera el nombre casi completo; la ficha y el
        # contexto se siguen validando, sin aceptar el fragmento PHILIP Z.
        v.leer_ficha.return_value=ficha(('PHILIP J. FR',));f=FuentesSkins(vista=v)
        self.assertIsNone(f.fortnite_visible(v.capturar.return_value))
        with patch.object(f,'primer_plano',return_value='fortnite'):
            lectura=f.leer('fortnite',manual=True)
        self.assertEqual(lectura.skins[0]['perfil'],'fry');v.leer_ficha.assert_called_once()
        v.capturar.assert_called_once_with(activar=True);v.pulsar.assert_not_called()

    def test_manual_informa_foco_perdido_sin_confundirlo_con_nombre_desconocido(self):
        from fortnite import ErrorFortnite
        f=Mock();f.leer.side_effect=ErrorFortnite('Fortnite perdió el foco.')
        m=MonitorSkins(Mock(),f)
        self.assertEqual(m.opinar('fortnite'),'Fortnite perdió el foco.');m.cerrar()

    def test_manual_respeta_idioma_no_reconoce_sin_datos_y_no_inicia_hilos(self):
        fuente=Mock();fuente.primer_plano.return_value='';fuente.leer.return_value=None
        m=MonitorSkins(Mock(),fuente)
        with patch('reacciones_skins.threading.Thread') as hilo:
            m.configurar({});hilo.assert_not_called()
            self.assertIn('Show me',m.opinar('fortnite',idioma='en'));self.assertIn('whether',m.opinar(idioma='en'))
            fuente.leer.return_value=Lectura('fortnite','ficha',(skin('fry','fortnite'),))
            self.assertNotEqual(m.opinar('fortnite',idioma='ja'),m.opinar('fortnite',idioma='es'))
        cancelar=threading.Event();cancelar.set();fuente.reset_mock()
        with self.assertRaises(InterruptedError):m.opinar('fortnite',cancelar=cancelar)
        fuente.leer.assert_not_called();m.cerrar()


if __name__=='__main__':unittest.main()
