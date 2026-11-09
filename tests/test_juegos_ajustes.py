import json
from unittest.mock import patch
from test_capri import PruebasTk
import test_companera_control as fixtures


class JuegosAjustes(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_opciones_en_su_juego_sin_iniciar_busquedas_ni_lecturas(self):
        with self.capri() as (c,_),patch.object(c.skins,'_fuentes') as fuentes,patch.object(c.fortnite_avisos,'actualizar') as red:
            c.configurar();c.panel_ajustes.mostrar('Juegos')
            p=c.ajustes_juegos
            self.assertEqual(set(p.paginas),{'lol','valorant','fortnite','cs2','roblox'})
            self.assertNotIn('Reacciones',c.panel_ajustes.secciones)
            self.assertNotIn('Avisos de Fortnite',c.panel_ajustes.secciones)
            for juego,nombre in p.pestanas:
                p.mostrar(juego,nombre);c.root.update()
                self.assertEqual(p.actual,juego)
                self.assertTrue(p.pestanas[juego,nombre][0].winfo_ismapped())
            self.assertIs(c.ajustes_avisos_fortnite.f,p.pestanas['fortnite','Avisos'][0])
            for juego in ('fortnite','valorant'):
                s=c.ajustes_skins[juego]
                self.assertIs(s.f,p.pestanas[juego,'Skins'][0])
                self.assertIsNone(s.juego)
                self.assertTrue(all(v['juego']==juego for v in s.opciones))
            fuentes.assert_not_called();red.assert_not_called()

    def test_reacciones_y_frecuencia_independientes_sin_pisar_el_otro_juego(self):
        with self.capri() as (c,base):
            c.configurar();v=c.ajustes_skins['valorant'];f=c.ajustes_skins['fortnite']
            v.cambiar('activo',True)
            self.assertTrue(c.cfg['reacciones_skins']['valorant']);self.assertFalse(c.cfg['reacciones_skins']['fortnite'])
            v.cambiar('frecuencia','discreta')
            f.cambiar('activo',True);f.cambiar('frecuencia','entusiasta')
            v.cambiar('activo',False)
            datos=json.loads((base/'ajustes.json').read_text(encoding='utf8'))['reacciones_skins']
            self.assertTrue(datos['activo']);self.assertFalse(datos['valorant']);self.assertTrue(datos['fortnite'])
            self.assertEqual(datos['frecuencia_valorant'],'discreta')
            self.assertEqual(datos['frecuencia_fortnite'],'entusiasta')
            self.assertEqual(c.skins.config,datos)
            f.cambiar('activo',False);self.assertFalse(c.cfg['reacciones_skins']['activo'])
