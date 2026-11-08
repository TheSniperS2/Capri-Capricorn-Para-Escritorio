import math
import unittest
from unittest.mock import Mock,patch
import numpy as np
from PIL import Image
from bienvenida import Bienvenida,LienzoAnimado,SALIDA
from retrato_intro import plan_transicion,renderizar_transicion,CIERRE,ENCOGER,PREPARADOS
from test_capri import PruebasTk
import test_companera_control as fixtures


def geometria():
    b=Bienvenida.__new__(Bienvenida)
    b.w=1920;b.h=1080;b.fin=(1716,841);b.destino_tamano=(360,338)
    return b


class Visor(unittest.TestCase):
    def test_traslado_personaje_termina_exactamente_en_el_sprite_sin_retrato_ni_marco(self):
        from retrato_intro import plan_personaje
        b=geometria();b.destino_tamano=(210,240)
        retrato=Image.new('RGBA',(1238,941),'#ff0030')
        cuerpo=Image.new('RGBA',(210,240),'#00ef24')
        for u in (.28,.55,.8,1):
            im,pos=renderizar_transicion(retrato,cuerpo,plan_personaje(b,u),'#ff4267')
            self.assertEqual(im.getchannel('R').getextrema(),(0,0))
        self.assertEqual(im.size,cuerpo.size)
        self.assertEqual(im.tobytes(),cuerpo.tobytes())
        self.assertEqual(pos,(round(b.fin[0]-105),round(b.fin[1]-120)))

    def test_color_key_equivale_a_componer_sobre_el_fondo_real_sin_perder_detalle(self):
        from retrato_intro import imagen_opaca,FONDO
        im=Image.new('RGBA',(3,1))
        im.putdata(((255,0,25,0),(19,220,240,128),(255,0,80,255)))
        esperado=Image.alpha_composite(Image.new('RGBA',im.size,(*FONDO,255)),im).convert('RGB')
        opaca=imagen_opaca(im)
        self.assertEqual(opaca.mode,'RGB')
        self.assertEqual(opaca.tobytes(),esperado.tobytes())

    def test_cuadro_preparado_se_transfiere_como_rgb_sin_recodificar_en_la_interfaz(self):
        import io
        from retrato_intro import preparar_imagen,imagen_opaca
        im=Image.new('RGBA',(1238,941),'#fa003a80')
        panel=Image.new('RGBA',(360,338),'#182838')
        plan=plan_transicion(geometria(),.55)
        datos,pos=preparar_imagen(im,panel,plan,'#ff4267')
        esperado,origen=renderizar_transicion(im,panel,plan,'#ff4267')
        recibido=Image.open(io.BytesIO(datos));recibido.load()
        self.assertEqual(recibido.mode,'RGB');self.assertEqual(pos,origen)
        self.assertEqual(recibido.tobytes(),imagen_opaca(esperado).tobytes())

    def test_el_visor_se_cierra_antes_de_empezar_a_encoger(self):
        b=geometria();inicial=b.geometria_salida(0)
        for u in (.05,.12,CIERRE,ENCOGER):
            self.assertEqual(b.geometria_salida(u),inicial)
        self.assertLess(b.geometria_salida(.6)[0],inicial[0])
        for u in (CIERRE,ENCOGER,.6,.9):
            p=plan_transicion(b,u)
            self.assertEqual(p['apertura'],p['caja'])

    def test_la_figura_nunca_sobresale_del_visor_al_reducirse(self):
        b=geometria();retrato=Image.new('RGBA',(1238,941),'#ff0000')
        panel=Image.new('RGBA',(360,338),'#183821')
        for u in (.12,CIERRE,ENCOGER,.55,.85):
            p=plan_transicion(b,u)
            im,(x,y)=renderizar_transicion(retrato,panel,p,'#ff4267')
            a=np.asarray(im);rojo=(a[:,:,0]==255)&(a[:,:,1]==0)&(a[:,:,2]==0)&(a[:,:,3]>0)
            l,t,r,borde=p['apertura'];yy,xx=np.ogrid[y:y+im.height,x:x+im.width]
            fuera=(xx<math.ceil(l))|(xx>=math.floor(r))|(yy<math.ceil(t))|(yy>=math.floor(borde))
            self.assertFalse(bool((rojo&fuera).any()),u)

    def test_lienzo_estatico_no_reordena_ni_invalida_la_imagen_grande(self):
        canvas=Mock();canvas.create_image.side_effect=(1,2);canvas.type.return_value='image'
        c=LienzoAnimado(canvas)
        def dibujar(cara):
            c.delete('all')
            c.create_image(0,0,image='cuerpo',tags='intro_retrato')
            c.create_image(100,100,image=cara,tags='intro_expresion')
            c.terminar()
        dibujar('ojos_abiertos');canvas.reset_mock()
        dibujar('ojos_abiertos')
        canvas.coords.assert_not_called();canvas.tag_raise.assert_not_called();canvas.itemconfigure.assert_not_called()
        dibujar('ojos_cerrados')
        canvas.itemconfigure.assert_called_once_with(2,image='ojos_cerrados')
        canvas.coords.assert_not_called();canvas.tag_raise.assert_not_called()


class Preparacion(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_intro_personaje_conserva_orientacion_posicion_y_pose_al_llegar(self):
        from PIL import ImageTk,ImageOps
        from companera import con_sombra
        with self.capri(ajustes={'modo_visual':'personaje','voz':False}) as (c,_):
            c.root.deiconify()
            for direccion in (-1,1):
                c.companera.direccion=direccion;c.iniciar_intro()
                b=c.bienvenida;p=c.companera;pos=(p.x,p.y)
                sprite=ImageOps.mirror(p.lienzos[0]) if direccion<0 else p.lienzos[0]
                esperado=con_sombra(sprite,c.cfg.get('halo_personaje','violeta'))
                self.assertEqual(b.destino.tobytes(),esperado.tobytes())
                with patch.object(p,'iniciar',side_effect=AssertionError('No reiniciar al llegar')):
                    c.finalizar_intro()
                c.root.update_idletasks()
                self.assertEqual((p.x,p.y,p.direccion),(*pos,direccion))
                self.assertEqual(ImageTk.getimage(p.imagen).tobytes(),sprite.tobytes())
                self.assertFalse(p.glitch_activo)
                self.assertGreater(p.proxima_accion,p.ultimo)
                self.assertEqual((c.root.winfo_width(),c.root.winfo_height()),sprite.size)

    def test_traslado_personaje_muestra_un_solo_compuesto_sin_estelas_ajenas(self):
        from PIL import ImageTk
        from bienvenida import DURACION
        with self.capri(ajustes={'modo_visual':'personaje','voz':False}) as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            r.detener();r.preparado=True
            foto=ImageTk.PhotoImage(b.destino)
            r.fotos={i:(foto,(100,100)) for i in range(r.pasos+1)}
            with patch('retrato_intro.ImageTk.PhotoImage',side_effect=AssertionError('Sin remuestreo en reproducción')):
                for u in (.1,.4,.8,.99):
                    b.dibujar(c.canvas,SALIDA+u*(b.duracion-SALIDA))
                    self.assertEqual(len(c.canvas.find_withtag('intro_retrato')),1)
                    self.assertFalse(c.canvas.find_withtag('intro_estela'))
                    visibles=[i for i in c.canvas.find_all() if c.canvas.itemcget(i,'state')!='hidden']
                    self.assertEqual(len(visibles),1)

    def test_no_prepara_transicion_durante_la_aparicion(self):
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            self.assertFalse(r.futuros)
            with patch.object(r,'preparar') as preparar:
                for t in (0,.03,.08,.16,.34,.44):self.assertEqual(b.tiempo(t),t)
                preparar.assert_not_called()
                b.tiempo(.46);preparar.assert_called_once()
            self.assertTrue(c.canvas.find_withtag('intro_aparicion_fragmentos'))

    def test_primer_cuadro_pintado_antes_de_mostrar_la_ventana(self):
        with self.capri() as (c,_):
            restaurar=c.restaurar_reubicacion
            def presentar():
                self.assertTrue(c.canvas.find_withtag('intro_aparicion_fragmentos'))
                self.assertFalse(c.bienvenida.retrato_aprobado.futuros)
                self.assertEqual(float(c.root.attributes('-alpha')),0.)
                restaurar()
            with patch.object(c,'restaurar_reubicacion',side_effect=presentar) as visible:
                c.iniciar_intro()
                visible.assert_called_once()
            self.assertFalse(hasattr(c,'intro_alpha'))

    def test_interferencias_son_tiras_pequenas_del_dibujo_y_no_siluetas_completas(self):
        with self.capri() as (c,_):
            c.iniciar_intro();r=c.bienvenida.retrato_aprobado
            for foto,y,direccion in r.efectos:
                self.assertLess(foto.height(),r.cuerpo.height()*.04)
                self.assertGreaterEqual(y,0)
                self.assertIn(direccion,(-1,1))
            c.bienvenida.dibujar(c.canvas,.08)
            self.assertTrue(c.canvas.find_withtag('intro_aparicion_interferencia'))
            self.assertFalse(c.canvas.find_withtag('intro_aparicion_destello'))

    def test_solo_se_preparan_pocos_cuadros_por_adelantado(self):
        with self.capri() as (c,_):
            c.iniciar_intro();r=c.bienvenida.retrato_aprobado
            for indice in (0,70,130):
                r.pedir(indice)
                self.assertLessEqual(len(r.futuros),PREPARADOS)
                self.assertTrue(all(indice<=i<indice+PREPARADOS for i in r.futuros))

    def test_ui_no_espera_a_un_trabajador_que_aun_no_termina(self):
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            for f in r.futuros.values():f.cancel()
            pendientes={i:Mock() for i in range(PREPARADOS)}
            for f in pendientes.values():f.done.return_value=False;f.cancelled.return_value=False
            r.futuros=pendientes
            with patch.object(r.pool,'submit',side_effect=AssertionError('No requiere mas cuadros')):
                self.assertLess(b.tiempo(SALIDA+.001),SALIDA)
                b.dibujar(c.canvas,SALIDA-.001)
            for f in pendientes.values():f.result.assert_not_called()
            self.assertTrue(c.canvas.find_withtag('intro_retrato'))

    def test_reproducir_no_remuestrea_ni_crea_imagenes_y_libera_cuadros_pasados(self):
        from bienvenida import DURACION
        from PIL import ImageTk
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            for f in r.futuros.values():f.cancel()
            r.pool.shutdown(wait=True,cancel_futures=True)
            r.fotos={i:(ImageTk.PhotoImage(Image.new('RGBA',(20,20),'#ff4267')),(120+i,100)) for i in (59,60,61)}
            r.preparado=True
            with patch('retrato_intro.ImageTk.PhotoImage',side_effect=AssertionError('Transferencia durante viaje')),patch('retrato_intro.PhotoImage',side_effect=AssertionError('Transferencia nativa durante viaje')),patch('retrato_intro.renderizar_transicion',side_effect=AssertionError('Remuestreo durante viaje')):
                for i in (60,61):
                    b.dibujar(c.canvas,SALIDA+(DURACION-SALIDA)*i/180)
                    self.assertEqual(r.ultimo,i)
                    self.assertTrue(all(k>=i for k in r.fotos))

    def test_el_reloj_del_viaje_no_corre_mientras_falta_preparacion(self):
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            with patch.object(r,'preparar'):
                r.preparado=False
                self.assertLess(b.tiempo(SALIDA+.01),SALIDA)
                self.assertLess(b.tiempo(SALIDA+.5),SALIDA)
                r.preparado=True
                visual=b.tiempo(SALIDA+.9)
                self.assertAlmostEqual(visual,SALIDA+.01)
                self.assertAlmostEqual(b.tiempo(SALIDA+1.1),visual+.2)

    def test_resolucion_del_reloj_windows_se_restaura_al_detener(self):
        with self.capri() as (c,_):
            c.iniciar_intro();r=c.bienvenida.retrato_aprobado
            reloj=r.reloj
            if reloj is not None:reloj.timeEndPeriod(1)
            r.reloj=Mock();simulado=r.reloj
            r.detener();r.detener()
            simulado.timeEndPeriod.assert_called_once_with(1)
