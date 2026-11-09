from unittest.mock import patch
import json
from test_capri import PruebasTk
import test_companera_control as fixtures


class VozLocalUI(PruebasTk):
    capri=fixtures.ModoPersonaje.capri
    def test_versiones_inglesas_persisten_y_no_regresan_selectores_antiguos(self):
        antes={'idioma':'en','voz_perfil':'ingles_vivaz','voz_acento':'es-CL','voz_ingles_modo':'local'}
        with patch('voz_local.disponible',return_value=True),patch('voz_local.rapida_disponible',return_value=True),patch('app.Voz.precalentar'),self.capri(antes) as (c,base):
            c.configurar();c.ajustes.update_idletasks()
            self.assertTrue(c.cfg['voz_ingles_local']);self.assertTrue(c.voz.ingles_local)
            self.assertEqual(c.voz.modo_ingles,'local');self.assertFalse(c.voz.rapida_unica)
            self.assertEqual(c.cfg['voz_perfil'],'capri');self.assertEqual(c.voz.acento,'auto')
            for nombre in ('acento_combo','perfil_voz_combo','voz_local_interruptor'):
                self.assertFalse(hasattr(c,nombre),nombre)
            self.assertEqual(c.opciones_voz.selector.current(),1)
            self.assertEqual(tuple(c.opciones_voz.selector.cget('values')),('Capri V1','Capri V2'))
            self.assertTrue(c.escala_volumen.winfo_exists())
            c.guardar('voz_ingles_modo','rapida');c.guardar('voz_perfil','ingles_calida')
            self.assertEqual(c.voz.modo_ingles,'rapida');self.assertEqual(c.cfg['voz_perfil'],'capri')
            c.guardar('voz_ingles_modo','local')
            c.guardar('volumen_voz',75)
            persistido=json.loads((base/'ajustes.json').read_text(encoding='utf8'))
            self.assertEqual(persistido['voz_ingles_modo'],'local')
            self.assertEqual(persistido['voz_acento'],'auto')
            self.assertEqual(persistido['volumen_voz'],75)

    def test_versiones_solo_ingles_y_espanol_conserva_dalia(self):
        from voz import elegir_voz
        with patch('voz_local.rapida_disponible',return_value=True),patch('app.Voz.precalentar'),self.capri() as (c,_):
            c.configurar();c.panel_ajustes.mostrar('Voz')
            for idioma in ('en','es','pt','ja'):
                c.guardar('idioma',idioma)
                c.root.update_idletasks()
                self.assertEqual(c.voz.idioma,idioma)
                self.assertEqual(c.voz.usar_voz_personal(),idioma=='en')
                self.assertEqual(bool(c.opciones_voz.ingles.winfo_manager()),idioma=='en')
                self.assertEqual(c.voz.modo_ingles,'rapida')
            c.guardar('idioma','es')
            self.assertEqual(elegir_voz(c.cfg['voz_perfil'],c.voz.idioma,c.voz.acento),('es-MX-DaliaNeural','+16Hz'))

    def test_silencio_anterior_migra_a_cero_y_el_volumen_reactiva(self):
        with patch('app.Voz.precalentar') as cargar,self.capri({'voz':True,'voz_natural':False}) as (c,base):
            self.assertEqual(c.cfg['volumen_voz'],0);self.assertFalse(c.cfg['voz_natural']);cargar.assert_not_called()
            c.guardar('volumen_voz',65)
            persistido=json.loads((base/'ajustes.json').read_text(encoding='utf8'))
            self.assertTrue(c.cfg['voz_natural']);self.assertTrue(persistido['voz_natural'])
            self.assertTrue(persistido['voz'])
            self.assertTrue(c.puede_narrar())
            c.configurar();c.guardar('volumen_voz',0)
            self.assertFalse(c.puede_narrar());self.assertEqual(c.escala_volumen.get(),0)
            c.alternar_silencio()
            self.assertTrue(c.puede_narrar());self.assertEqual(c.escala_volumen.get(),65)

    def test_sin_recursos_de_v1_no_usa_un_perfil_inexistente(self):
        with patch('voz_local.disponible',return_value=True),patch('voz_local.rapida_disponible',return_value=False),patch('app.Voz.precalentar'),self.capri({'idioma':'en','voz_ingles_local':True}) as (c,_):
            self.assertFalse(c.voz.usar_voz_personal())
            c.guardar('voz_ingles_modo','local')
            self.assertTrue(c.voz.usar_voz_personal())
            c.guardar('voz_ingles_modo','rapida')
            self.assertFalse(c.voz.usar_voz_personal())

    def test_traducciones_de_voz_y_juegos_incluidas(self):
        from idiomas import catalogo
        from ajustes_voz import TEXTOS as voz
        from juegos_ui import TEXTOS as juegos
        for texto in voz+juegos:self.assertIn(texto,catalogo())

    def test_preparando_local_no_termina_turno_ni_abre_escucha(self):
        with self.capri() as (c,_),patch.object(c.escucha_activa,'fin_voz') as fin:
            c.voz_ticket=c.peticion
            c.eventos.put(('voz',(c.voz.generacion,('preparando_local',None))))
            c.poll()
            self.assertEqual(c.estado,'Preparando voz local…')
            self.assertEqual(c.voz_ticket,c.peticion);fin.assert_not_called()

    def test_preparando_rapida_no_finaliza_escucha(self):
        with self.capri() as (c,_):
            c.voz_ticket=c.peticion
            with patch.object(c.escucha_activa,'fin_voz') as fin:
                c.eventos.put(('voz',(c.voz.generacion,('preparando_rapida',None))));c.poll()
                self.assertEqual(c.estado,'Preparando voz…');fin.assert_not_called()
