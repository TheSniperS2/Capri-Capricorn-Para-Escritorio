import copy,json,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import Mock,patch
from fortnite_avisos import (normalizar,leer_tienda,leer_misiones,ErrorDatos,MonitorFortnite,
                            FuentesAvisos,Redirecciones,mensaje)

AHORA=datetime(2026,11,9,0,10,tzinfo=timezone.utc)


def tienda(dia='2026-11-09'):
    return {'status':200,'data':{'date':dia+'T00:00:00Z','hash':'abc','entries':[{'id':'publico'}]}}


def misiones(total=40):
    return {'status':'current','snapshot':{'mode':'live','complete':True,'coverage':['vbucks'],
        'rotationId':'2026-11-09','effectiveAt':'2026-11-09T00:00:00Z','expiresAt':'2026-11-10T00:00:00Z',
        'vbucksHistory':{'today':{'total':total}},'missions':[
            {'missionId':'m1','category':'vbucks','quantity':total,'pl':82,'zone':'Canny Valley','type':'Fight the Storm'}] if total else []}}


def html(d):return '<html><script type="application/json" id="mission-bootstrap">'+json.dumps(d)+'</script></html>'


class DatosPublicos(unittest.TestCase):
    def test_flags_estrictos_y_sin_cuenta(self):
        self.assertEqual(normalizar(None),{'tienda':False,'pavos':False,'fundador':False})
        self.assertFalse(normalizar({'pavos':'true'})['pavos'])

    def test_tienda_fecha_utc_y_rotacion_que_aun_no_comienza(self):
        d=leer_tienda(tienda(),AHORA);self.assertEqual(d['rotacion'],'2026-11-09')
        local=AHORA.astimezone(timezone(timedelta(hours=-3)));self.assertEqual(local.day,8)
        self.assertEqual(leer_tienda(tienda(),local),d)
        for fecha in ('2026-11-08','2026-11-10'):
            with self.assertRaises(ErrorDatos):leer_tienda(tienda(fecha),AHORA)
        with self.assertRaises(ErrorDatos):leer_tienda(tienda(),datetime(2026,11,10,tzinfo=timezone.utc))

    def test_misiones_positivas_cero_y_duplicados(self):
        d=misiones();d['snapshot']['missions']*=2
        p=leer_misiones(html(d),AHORA);self.assertEqual(p['total'],40);self.assertEqual(len(p['misiones']),1)
        self.assertEqual(leer_misiones(html(misiones(0)),AHORA)['misiones'],[])
        self.assertEqual(p['misiones'][0]['nivel'],82)

    def test_error_no_es_ausencia_de_pavos(self):
        for cambiar in (lambda d:d.update(status='stale'),
                        lambda d:d['snapshot'].update(complete=False),
                        lambda d:d['snapshot'].update(coverage=[]),
                        lambda d:d['snapshot'].update(mode='demo'),
                        lambda d:d['snapshot'].update(missions=[]),
                        lambda d:d['snapshot'].update(expiresAt='2026-11-11T00:00:00Z')):
            d=misiones();cambiar(d)
            with self.subTest(d=d),self.assertRaises(ErrorDatos):leer_misiones(html(d),AHORA)
        with self.assertRaises(ErrorDatos):leer_misiones('<h1>No data</h1>',AHORA)
        with self.assertRaises(ErrorDatos):leer_misiones(html(misiones())*2,AHORA)
        with self.assertRaises(ErrorDatos):leer_misiones(html(misiones()),AHORA+timedelta(days=1))

    def test_red_solo_get_publico_acotado_y_sin_redireccion_ajena(self):
        respuesta=Mock();respuesta.__enter__=Mock(return_value=respuesta);respuesta.__exit__=Mock(return_value=False)
        respuesta.read.return_value=json.dumps(tienda()).encode();abridor=Mock();abridor.open.return_value=respuesta
        with patch('fortnite_avisos.urllib.request.build_opener',return_value=abridor):
            self.assertEqual(FuentesAvisos().obtener('tienda',AHORA)['rotacion'],'2026-11-09')
            req=abridor.open.call_args.args[0];self.assertEqual(req.get_method(),'GET');self.assertIsNone(req.data)
            self.assertFalse(any(k.lower() in ('cookie','authorization','x-api-key') for k in req.headers))
            respuesta.read.return_value=b'x'*3_000_001
            with self.assertRaises(ErrorDatos):FuentesAvisos().obtener('tienda',AHORA)
        import urllib.request
        req=urllib.request.Request('https://vbucksdaily.com/')
        for u in ('http://vbucksdaily.com/','https://otro.test/','https://vbucksdaily.com:99/'):
            with self.assertRaises(ErrorDatos):Redirecciones().redirect_request(req,None,302,'',{},u)


class Avisos(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.reloj=Mock(return_value=AHORA.timestamp());self.f=Mock()
        self.m=MonitorFortnite(self.tmp.name,self.f,self.reloj);self.addCleanup(self.m.cerrar)
        self.f.obtener.side_effect=lambda tipo,ahora:leer_tienda(tienda(ahora.date().isoformat()),ahora) if tipo=='tienda' else leer_misiones(html(misiones()),ahora)

    def consultar(self,c=None):
        if c is not None:self.m.configurar(c,iniciar=False)
        self.m._consultar()

    def test_tienda_primera_lectura_no_anuncia_un_cambio_y_tras_reinicio_solo_una(self):
        self.consultar({'tienda':True});self.assertIsNone(self.m.siguiente())
        self.reloj.return_value+=(24*3600);self.consultar();p=self.m.siguiente();self.assertEqual(p.tipo,'tienda')
        # Puede permanecer pendiente mientras Capri conversa.
        self.assertIs(self.m.siguiente(),p);self.assertTrue(self.m.confirmar(p));self.assertFalse(self.m.confirmar(p))
        m=MonitorFortnite(self.tmp.name,self.f,self.reloj);self.addCleanup(m.cerrar);m.configurar({'tienda':True},False);m._consultar()
        self.assertIsNone(m.siguiente());self.assertIn('tienda de Fortnite',mensaje(p))

    def test_pavos_necesitan_fundador_y_confirmacion_antes_de_deduplicar(self):
        self.consultar({'pavos':True});self.assertIsNone(self.m.siguiente())
        self.consultar({'pavos':True,'fundador':True});p=self.m.siguiente();self.assertEqual(p.datos['total'],40)
        self.assertNotIn('pavos',self.m.memoria);self.assertTrue(self.m.confirmar(p));self.assertIn('40',mensaje(p,'en'))
        self.consultar();self.assertIsNone(self.m.siguiente())
        m=MonitorFortnite(self.tmp.name,self.f,self.reloj);self.addCleanup(m.cerrar);m.configurar({'pavos':True,'fundador':True},False);m._consultar();self.assertIsNone(m.siguiente())

    def test_caduca_se_desactiva_o_cambia_configuracion_no_se_narra(self):
        self.consultar({'pavos':True,'fundador':True});p=self.m.siguiente()
        self.m.configurar({'pavos':True},False);self.assertFalse(self.m.confirmar(p));self.assertIsNone(self.m.siguiente())
        self.consultar({'pavos':True,'fundador':True});p=self.m.siguiente();self.reloj.return_value=p.datos['vence']
        self.assertFalse(self.m.confirmar(p));self.assertIsNone(self.m.siguiente())

    def test_fallo_o_datos_revisados_sin_pavos_descartan_alerta_vieja(self):
        self.consultar({'pavos':True,'fundador':True});p=self.m.siguiente()
        self.f.obtener.side_effect=TimeoutError();self.consultar();self.assertIsNone(self.m.siguiente());self.assertIn('pavos',self.m.errores)
        self.assertFalse(self.m.confirmar(p));self.assertEqual(self.m.proxima,self.reloj()+60)
        self.f.obtener.side_effect=lambda *a:leer_misiones(html(misiones(0)),AHORA)
        self.consultar();self.assertIsNone(self.m.siguiente());self.assertNotIn('pavos',self.m.errores)

    def test_desactivar_durante_red_descarta_resultado_y_no_hay_hilos_por_defecto(self):
        with patch('fortnite_avisos.threading.Thread') as t:
            self.m.configurar({},True);t.assert_not_called()
        def fuente(*a):
            self.m.configurar({},False);return leer_misiones(html(misiones()),AHORA)
        self.f.obtener.side_effect=fuente;self.consultar({'pavos':True,'fundador':True})
        self.assertEqual(self.m.datos,{});self.assertIsNone(self.m.siguiente())


if __name__=='__main__':unittest.main()
