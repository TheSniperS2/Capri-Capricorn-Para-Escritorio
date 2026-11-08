import io,json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from roblox import ClientePublico,ControlRoblox,DetectorEventos,agregar_favorito
from roblox_info import perfil_automatico,REGLAS_AUTOMATICAS,resolver_resultado
from roblox_dialogos import opinion

class Automatico(unittest.TestCase):
    def test_categoria_y_descripcion_distinguen_terror_de_aventura_generica(self):
        self.assertEqual(perfil_automatico({'genero':'Adventure','descripcion':'A horror game involving doors.'}),'terror')
        for genero,perfil in [('Dress Up','estilo'),('Platformer','aventura'),('Puzzle','discreta'),('Sports','clasica')]:
            self.assertEqual(perfil_automatico({'genero':genero}),perfil)
        self.assertEqual(perfil_automatico({}),'clasica')
    def test_metadatos_resuelven_place_a_universo_y_se_guardan_en_cache(self):
        c=ClientePublico()
        respuestas=[{'universeId':2440500124},{'data':[{'id':2440500124,'name':'Puertas','description':'A horror game','genre':'Adventure','genre_l1':'Survival','genre_l2':'Escape','creator':{'name':'Creador'}}]}]
        with patch.object(c,'json',side_effect=respuestas) as red:
            a=c.detalles_lugar('6516141723');b=c.detalles_lugar('6516141723')
        self.assertEqual(a,b);self.assertEqual(a['perfil'],'terror');self.assertEqual(red.call_count,2)
        self.assertIn('/places/6516141723/universe',red.call_args_list[0].args[0])
        self.assertIn('universeIds=2440500124',red.call_args_list[1].args[0])
    def test_accesorio_hombro_se_localiza_por_tipo_y_gusto_no_cambia_con_otras_prendas(self):
        p={'id':88,'nombre':'Robot diminuto','tipo_id':44,'tipo':'ShoulderAccessory'}
        a={'gusto':0,'piezas':[p]};b={'gusto':2,'piezas':[p,{'id':91,'nombre':'Camisa','tipo_id':11}]}
        frase=opinion(a);self.assertIn('En el hombro',frase);self.assertIn('Robot diminuto',frase)
        self.assertIn(frase.split(': ',1)[1],opinion(b))
        falso={'gusto':0,'piezas':[{'id':88,'nombre':'Robot shoulder','tipo_id':46,'tipo':'BackAccessory'}]}
        self.assertIn('espalda',opinion(falso));self.assertNotIn('En el hombro',opinion(falso))
    def test_avisos_conocidos_no_requieren_configuracion_y_el_final_ambiguo_pregunta(self):
        for texto,evento in [('YOU DIED','muerte'),('VICTORY!','victoria'),('Game over','duda')]:
            d=DetectorEventos();self.assertIsNone(d.observar([texto],REGLAS_AUTOMATICAS,0))
            self.assertEqual(d.observar([texto],REGLAS_AUTOMATICAS,3),evento)
            self.assertIsNone(d.observar([texto],REGLAS_AUTOMATICAS,100))
        d=DetectorEventos()
        for t in (0,3):r=d.observar(['VICTORY','YOU DIED'],REGLAS_AUTOMATICAS,t)
        self.assertEqual(r,'duda')
        self.assertIsNone(resolver_resultado('no'));self.assertEqual(resolver_resultado('perdí'),'derrota')
    def test_registro_solo_extrae_el_ultimo_lugar_y_no_lee_fuera_de_roblox(self):
        from roblox_vision import lugar_actual
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'2026_Player_ABC.log';p.write_text('Joining game x place 123 at not-used\nplaceId=456\n',encoding='utf8')
            with patch('roblox_vision.en_primer_plano',return_value=True):self.assertEqual(lugar_actual(tmp),'456')
            with patch('roblox_vision.en_primer_plano',return_value=False):self.assertIsNone(lugar_actual(tmp))
    def test_contexto_automatico_no_confunde_favorito_con_partida_detectada(self):
        c=ControlRoblox(iniciar=False);d=agregar_favorito({},'Elegido','123');c.configurar(d)
        c.informacion[d['seleccion']]={'nombre':'Elegido','perfil':'terror','descripcion':'A horror game','genero':'Survival'}
        self.assertEqual(c.contexto()['origen'],'favorito seleccionado');self.assertEqual(c.perfil(),'terror')
        c.experiencia_actual={'nombre':'Juego actual','perfil':'estilo','genero':'Dress Up','descripcion':'Fashion'}
        self.assertEqual(c.contexto()['experiencia_elegida'],'Juego actual');self.assertEqual(c.perfil(),'estilo')
    def test_vigilancia_completa_reacciona_sin_favorito_ni_palabras_personales(self):
        from unittest.mock import Mock
        from test_roblox_ui import informacion
        cliente=Mock();cliente.detalles_lugar.return_value=informacion('123')
        eventos=[];c=ControlRoblox(eventos.append,iniciar=False,cliente=cliente);c.configurar({'acompanar':True});c.permitido=True
        with patch.object(c.fin,'wait',side_effect=[False,False,True]),patch('roblox_vision.en_primer_plano',return_value=True),patch('roblox_vision.lugar_actual',return_value='123'),patch('roblox_vision.leer_centro',return_value=['VICTORY']),patch('roblox.time.monotonic',side_effect=[0,4,4]):
            c._vigilar()
        self.assertEqual(len(eventos),1);self.assertEqual(eventos[0][1]['evento'],'victoria');self.assertEqual(eventos[0][1]['perfil'],'terror')
    def test_desactivar_durante_consulta_impide_una_captura_tardia(self):
        from unittest.mock import Mock
        from test_roblox_ui import informacion
        cliente=Mock();c=ControlRoblox(iniciar=False,cliente=cliente);c.configurar({'acompanar':True});c.permitido=True
        def responder(*a):c.configurar({'acompanar':False});return informacion('123')
        cliente.detalles_lugar.side_effect=responder
        with patch.object(c.fin,'wait',side_effect=[False,True]),patch('roblox_vision.en_primer_plano',return_value=True),patch('roblox_vision.lugar_actual',return_value='123'),patch('roblox_vision.leer_centro') as leer:
            c._vigilar()
        leer.assert_not_called()

if __name__=='__main__':unittest.main()
