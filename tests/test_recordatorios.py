import json,unittest
from core import interpretar
from recordatorios import agregar,normalizar,migrar,ErrorRecordatorio

class Recordatorios(unittest.TestCase):
    def test_ordenes_sin_juego_conservan_texto_y_plazo(self):
        for t,minutos in [('recuérdame en 10 minutos beber agua',10),('avísame dentro de 2 horas apagar el horno',120),('recuérdame en 30 segundos mirar la ventana',.5)]:
            o=interpretar(t);self.assertEqual(o.tipo,'recordatorios_crear');self.assertEqual(json.loads(o.valor)['minutos'],minutos)
        for t in ('no me recuerdes en 10 minutos beber agua','"recuérdame en 10 minutos beber agua"','si digo recuérdame en 10 minutos beber agua'):
            o=interpretar(t);self.assertFalse(o and o.tipo=='recordatorios_crear')
    def test_migracion_preserva_avisos_sin_duplicar_ni_resucitar_entregados(self):
        viejos=agregar([],'Una pausa',20,ahora=100)
        cfg={'roblox':{'recordatorios':viejos},'recordatorios':[],'otro':'conservado'}
        self.assertTrue(migrar(cfg));self.assertEqual(cfg['recordatorios'],viejos);self.assertEqual(cfg['roblox']['recordatorios'],[])
        self.assertFalse(migrar(cfg));self.assertEqual(cfg['otro'],'conservado')
        cfg['recordatorios']=[];migrar(cfg);self.assertEqual(cfg['recordatorios'],[])
    def test_ordenes_en_los_idiomas_de_la_interfaz(self):
        for texto in ('remind me in 20 minutes to take a break','lembre-me em 20 minutos de fazer uma pausa','カプリ、20分後に休憩を教えて'):
            o=interpretar(texto);self.assertEqual(o.tipo,'recordatorios_crear');self.assertEqual(json.loads(o.valor)['minutos'],20)
    def test_persistencia_y_limites_de_plazo(self):
        lista=agregar([],'Agua',10,ahora=100);self.assertEqual(normalizar(json.loads(json.dumps(lista))),lista)
        self.assertEqual(lista[0]['vence'],700)
        for plazo in (0,-1,10081,float('nan')):
            with self.assertRaises(ErrorRecordatorio):agregar([],'Prueba',plazo)

if __name__=='__main__':unittest.main()
