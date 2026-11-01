import time
from unittest.mock import Mock,patch
from test_capri import PruebasTk
import test_companera_control as fixtures
from bienvenida import Bienvenida,SALIDA,DURACION


class BienvenidaYReaccion(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_intro_saluda_sin_preparar_ni_reproducir_voz_aunque_este_activada(self):
        with self.capri() as (c,_):
            c.cfg['voz']=True
            with patch.object(c.voz,'preparar') as preparar,patch.object(c.voz,'hablar') as hablar,patch.object(c.micro,'escuchar') as micro:
                c.iniciar_intro()
                for t in (.9,2.2,4.6):
                    c.inicio_intro=time.monotonic()-t;c.animar()
                textos=[c.canvas.itemcget(i,'text') for i in c.canvas.find_all() if c.canvas.type(i)=='text']
                self.assertIn(c.frase_intro,textos)
                preparar.assert_not_called();hablar.assert_not_called();micro.assert_not_called()
                self.assertFalse(c.intro_esperando_fin);self.assertFalse(c.dialogo.sincronizada)

    def test_intro_pose_propia_con_cuerpo_estable_y_expresiones(self):
        from PIL import Image,ImageChops,ImageDraw
        from retrato_intro import recurso,ATLAS
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;r=b.retrato_aprobado
            with Image.open(recurso(ATLAS)) as atlas:
                w,h=atlas.width//2,atlas.height//2
                for i,(fila,col) in enumerate(((0,0),(0,1),(1,0),(1,1))):
                    esperado=atlas.crop((col*w,fila*h,(col+1)*w,(fila+1)*h)).convert('RGB')
                    self.assertIsNone(ImageChops.difference(r.originales[i].convert('RGB'),esperado).getbbox())
                    self.assertEqual(r.originales[i].getchannel('A').getextrema(),(0,255))
                    cambios=ImageChops.difference(r.originales[i].convert('RGB'),r.originales[2].convert('RGB'))
                    ImageDraw.Draw(cambios).rectangle((670,380,1030,670),fill=0)
                    self.assertIsNone(cambios.getbbox())
            b.dibujar(c.canvas,1.4)
            item=c.canvas.find_withtag('intro_retrato')[-1]
            expresion_abierta=c.canvas.itemcget(item,'image')
            b.dibujar(c.canvas,1.86)
            self.assertNotEqual(expresion_abierta,c.canvas.itemcget(c.canvas.find_withtag('intro_retrato')[-1],'image'))
            self.assertEqual(b.tiempo(2,True),2)

    def test_intro_encuadre_deja_las_manos_fuera_y_conserva_el_arte(self):
        from PIL import ImageChops
        with self.capri() as (c,_):
            c.iniciar_intro();r=c.bienvenida.retrato_aprobado
            im=r.originales[2];w,h=im.size
            izq,arr,der,ab=r.ventana_fuente
            self.assertGreater(izq,w*.11);self.assertLess(der,w*.89)
            self.assertEqual((arr,ab),(0,h))
            for original,vista in zip(r.originales,r.vistas):
                self.assertIsNone(ImageChops.difference(vista,original.crop(r.ventana_fuente)).getbbox())
            self.assertLessEqual(abs(r.base[0]-c.bienvenida.w),1)

    def test_intro_conserva_detalle_hd_y_saludo_encima_del_pelo(self):
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida
            for t in (.45,1.4,2.7):b.dibujar(c.canvas,t)
            r=b.retrato_aprobado
            self.assertGreaterEqual(r.originales[0].width,1600)
            self.assertGreaterEqual(r.originales[0].height,900)
            orden=list(c.canvas.find_all())
            self.assertGreater(orden.index(c.canvas.find_withtag('intro_saludo')[-1]),orden.index(c.canvas.find_withtag('intro_retrato')[-1]))
            subtitulo=c.canvas.find_withtag('intro_subtitulo')
            self.assertTrue(subtitulo)
            self.assertEqual(c.canvas.itemcget(subtitulo[-1],'text'),'Capricorn Desktop')
            saludo=next(i for i in c.canvas.find_withtag('intro_saludo') if c.canvas.type(i)=='text')
            sx,sy,sr,sb=c.canvas.bbox(saludo);lx,ly,lr,lb=c.canvas.bbox(subtitulo[-1])
            self.assertGreaterEqual(sx,0);self.assertLessEqual(sr,b.w)
            self.assertLess(sb,ly);self.assertLessEqual(lr,b.w);self.assertLessEqual(lb,b.h)

    def test_intro_materializa_fragmentos_e_interferencia_sin_fogonazo(self):
        with self.capri() as (c,_):
            c.iniciar_intro();b=c.bienvenida;canvas=c.canvas
            centro=None
            for t,tag in ((0,'intro_aparicion_fragmentos'),(.08,'intro_aparicion_interferencia'),(.16,'intro_aparicion_interferencia')):
                b.dibujar(canvas,t)
                self.assertTrue(canvas.find_withtag(tag))
                if centro is None:centro=b.rig[5:7]
                self.assertEqual(b.rig[5:7],centro)
                self.assertFalse(canvas.find_withtag('intro_llegada'))
            b.dibujar(canvas,.4)
            self.assertTrue(canvas.find_withtag('intro_retrato'))
            for tag in ('intro_aparicion_fragmentos','intro_aparicion_interferencia','intro_aparicion_destello'):
                self.assertFalse(canvas.find_withtag(tag))
            izq,arr,der,ab=canvas.bbox('intro_retrato')
            self.assertGreater(der-izq,b.w*.85);self.assertLess(arr,b.h*.15)

    def test_intro_aterriza_en_personaje_sin_dejar_chat_ni_superficie_grande(self):
        with self.capri() as (c,_):
            c.cfg['modo_visual']='personaje';c.iniciar_intro()
            ultima=c.bienvenida.llegada[-1]
            self.assertEqual((ultima.width(),ultima.height()),(c.companera.ancho,c.companera.alto))
            c.inicio_intro=time.monotonic()-DURACION-.1;c.animar()
            self.assertFalse(c.intro_activa);self.assertFalse(c.entrada_compacta.winfo_manager())
            self.assertEqual(int(c.canvas.cget('height')),c.companera.alto)

    def test_intro_encoge_la_misma_cara_y_forma_el_panel_hasta_encajar(self):
        import base64,io
        from PIL import Image,ImageChops
        with self.capri() as (c,_):
            c.cfg['modo_visual']='pantalla';c.iniciar_intro();b=c.bienvenida;canvas=c.canvas
            b.dibujar(canvas,SALIDA-.001)
            b.dibujar(canvas,SALIDA+.001)
            self.assertTrue(canvas.find_withtag('intro_retrato'))
            self.assertFalse(canvas.find_withtag('intro_llegada'))
            tamanos=[]
            for u in (.05,.3,.55,.8,1):
                z,ox,oy,caja,factor=b.geometria_salida(u);tamanos.append(z)
                b.dibujar(canvas,SALIDA+u*(DURACION-SALIDA))
                self.assertTrue(canvas.find_withtag('intro_retrato'))
            self.assertEqual(tamanos,sorted(tamanos,reverse=True))
            self.assertLessEqual(len(b.retrato_aprobado.fotos),181)
            self.assertLessEqual(len(b.retrato_aprobado.futuros),5)
            imagen=canvas.find_withtag('intro_llegada')[0]
            self.assertEqual(canvas.coords(imagen),list(b.fin))
            datos=canvas.tk.call(canvas.itemcget(imagen,'image'),'data','-format','png')
            if isinstance(datos,str):datos=base64.b64decode(datos)
            final=Image.open(io.BytesIO(datos)).convert('RGBA')
            self.assertIsNone(ImageChops.difference(final.convert('RGB'),b.destino.convert('RGB')).getbbox())
            self.assertIsNone(ImageChops.difference(final.getchannel('A'),b.destino.getchannel('A')).getbbox())

    def test_reaccion_de_llamada_desaparece_un_segundo_despues_de_voz_en_ambos_modos(self):
        from tema_ui import tk
        original=tk.Toplevel
        class Oculta(original):
            def __init__(self,*a,**kw):super().__init__(*a,**kw);self.withdraw()
            def deiconify(self):self.withdraw()
        for modo in ('pantalla','personaje'):
            with self.capri() as (c,_),patch.object(c.voz,'hablar'),patch('escritorio.proteger_foco',return_value=False),patch.object(tk,'Toplevel',Oculta):
                c.cfg['voz']=True;c.cfg['modo_visual']=modo
                if modo=='personaje':c.companera.redimensionar(1)
                c.reaccion_pendiente=(0,'Ese chiste debería estar en busca y captura.')
                c.revisar_interacciones();self.assertEqual(c.dialogo.duracion_final,1)
                c.eventos.put(('voz',(c.voz.generacion,True)));c.poll()
                with patch('app.time.monotonic',return_value=1234.):
                    c.eventos.put(('voz',(c.voz.generacion,False)));c.poll()
                self.assertEqual(c.dialogo.vence,1235.);self.assertFalse(c.dialogo.sincronizada)
                with patch('dialogos.time.monotonic',return_value=1235.01),patch.object(c.dialogo,'ocultar') as ocultar:
                    c.dialogo.tick();ocultar.assert_called_once()
