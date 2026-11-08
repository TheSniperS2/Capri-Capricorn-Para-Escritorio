import time
import unittest
from unittest.mock import Mock,patch
from PIL import Image,ImageDraw
from fortnite import Texto,Pantalla,ErrorFortnite,ControlFortnite
from fortnite_vision import botones_equipo,VistaFortnite,leer_imagen


class Vision(unittest.TestCase):
    def vista(self):
        v=VistaFortnite.__new__(VistaFortnite);v.g=Mock();v.a=Mock();v.c=Mock();v.error=OSError
        v._es_fortnite=Mock(return_value=True);v.g.IsWindow.return_value=True
        v.g.GetClientRect.return_value=(0,0,800,600);v.g.ClientToScreen.side_effect=lambda h,p:p
        return v

    def test_restauracion_lenta_espera_ventana_y_render_sin_entradas(self):
        from contextlib import ExitStack
        v=self.vista();reloj=[0.];solicitada=[]
        v._mostrar_restaurada=Mock(side_effect=lambda h:solicitada.append(h))
        # No se permite dar el foco antes de finalizar la restauración.
        v.g.IsIconic.side_effect=lambda h:not solicitada or reloj[0]<1.8
        foco=[999];v.g.GetForegroundWindow.side_effect=lambda:foco[0]
        def activar(h):
            self.assertFalse(v.g.IsIconic(h));foco[0]=h
        v.g.SetForegroundWindow.side_effect=activar
        v._ventana=Mock(return_value=123)
        vacia=Image.new('RGB',(800,600),'black');lista=vacia.copy();ImageDraw.Draw(lista).rectangle((100,100,500,400),fill='white')
        def imagen(**kw):return lista if reloj[0]>=2.5 else vacia
        with ExitStack() as s:
            s.enter_context(patch('fortnite_vision.time.monotonic',side_effect=lambda:reloj[0]))
            s.enter_context(patch('fortnite_vision.time.sleep',side_effect=lambda n:reloj.__setitem__(0,reloj[0]+n)))
            s.enter_context(patch('PIL.ImageGrab.grab',side_effect=imagen))
            ocr=s.enter_context(patch('fortnite_vision.leer_imagen',return_value=(Texto('JUGAR',(20,500,100,25)),)))
            p=v.capturar(activar=True)
        self.assertGreaterEqual(reloj[0],2.5);self.assertEqual(p.ventana,123)
        v._mostrar_restaurada.assert_called_once_with(123);v.g.SetForegroundWindow.assert_called_once_with(123)
        ocr.assert_called_once();v.a.mouse_event.assert_not_called();v.a.keybd_event.assert_not_called()

    def test_activacion_no_restaura_de_nuevo_ni_forza_foco_en_capturas_posteriores(self):
        v=self.vista();v._mostrar_restaurada=Mock();v.g.GetForegroundWindow.return_value=123;v.g.IsIconic.return_value=False
        self.assertFalse(v._activar(123));v._mostrar_restaurada.assert_not_called();v.g.SetForegroundWindow.assert_not_called()
        v._ventana=Mock(return_value=123);v.g.GetForegroundWindow.return_value=999
        with self.assertRaises(ErrorFortnite):v.capturar(activar=False)
        v._mostrar_restaurada.assert_not_called();v.g.SetForegroundWindow.assert_not_called()

    def test_minimizada_se_recupera_aunque_el_foco_conserve_el_mismo_hwnd(self):
        v=self.vista();minimizada=[True];v.g.IsIconic.side_effect=lambda h:minimizada[0]
        v.g.GetForegroundWindow.return_value=123
        v._mostrar_restaurada=Mock(side_effect=lambda h:minimizada.__setitem__(0,False))
        self.assertTrue(v._activar(123));v._mostrar_restaurada.assert_called_once_with(123)
        v.g.SetForegroundWindow.assert_not_called()

    def test_windows_rechaza_foco_no_se_hacen_clics_ni_se_envian_teclas(self):
        v=self.vista();v.g.IsIconic.return_value=False;v.g.GetForegroundWindow.return_value=999
        v.g.SetForegroundWindow.side_effect=OSError('denegado');reloj=[0.]
        with patch('fortnite_vision.time.monotonic',side_effect=lambda:reloj[0]),patch('fortnite_vision.time.sleep',side_effect=lambda n:reloj.__setitem__(0,reloj[0]+n)):
            with self.assertRaisesRegex(ErrorFortnite,'no permitió activar'):v._activar(123)
        v.g.SetForegroundWindow.assert_called_once();v.a.mouse_event.assert_not_called();v.a.keybd_event.assert_not_called()

    def test_minimizada_sin_fotogramas_falla_sin_repetir_acciones(self):
        v=self.vista();v._validar=Mock();v._rect=Mock(return_value=(0,0,800,600));reloj=[0.]
        with patch('fortnite_vision.time.monotonic',side_effect=lambda:reloj[0]),patch('fortnite_vision.time.sleep',side_effect=lambda n:reloj.__setitem__(0,reloj[0]+n)),patch('PIL.ImageGrab.grab',return_value=Image.new('RGB',(800,600),'black')):
            with self.assertRaisesRegex(ErrorFortnite,'todavía no muestra'):v._imagen(123,esperar=True)
        self.assertGreaterEqual(reloj[0],4);self.assertLess(reloj[0],4.2)
        v.a.mouse_event.assert_not_called();v.a.keybd_event.assert_not_called()

    def test_detecta_cuatro_botones_en_varias_resoluciones(self):
        for factor in (1,1.25,1.5,2):
            with self.subTest(factor=factor):
                ancho,alto=int(1280*factor),int(720*factor)
                im=Image.new('RGB',(ancho,alto),'#271075');d=ImageDraw.Draw(im)
                x,y=int(790*factor),int(240*factor);t=Texto('Tamaño del equipo',(x,y,int(140*factor),int(14*factor)))
                for i in range(4):
                    l=int((976+i*55)*factor);a=int(232*factor);lado=int(43*factor)
                    d.rectangle((l,a,l+lado-1,a+lado-1),fill='#5c32cb')
                    d.ellipse((l+lado*.43,a+lado*.28,l+lado*.57,a+lado*.42),fill='white')
                    d.rectangle((l+lado*.36,a+lado*.48,l+lado*.64,a+lado*.69),fill='white')
                botones=botones_equipo(im,(t,))
                self.assertEqual([b.texto for b in botones],['solo','duo','trio','squad'])
                for b in botones:self.assertLess(abs(b.rect[2]-b.rect[3]),3)
                self.assertEqual(botones_equipo(im,()),())
                d.rectangle((int(1140*factor),int(220*factor),ancho,alto),fill='#271075')
                self.assertEqual(botones_equipo(im,(t,)),())

    def test_una_letra_de_ocr_solo_en_menu_completo_y_sin_ambiguedad(self):
        texto=Texto('}ERO CONSTRUCCIÓN',(1000,90,280,24))
        p=Pantalla(123,(0,0,1600,900),(texto,),time.monotonic())
        self.assertIsNone(ControlFortnite._boton_modo(p,'cero'))
        p=Pantalla(123,(0,0,1600,900),(texto,),time.monotonic(),tuple(Texto(str(i),(i,1,1,1)) for i in range(4)))
        self.assertEqual(ControlFortnite._boton_modo(p,'cero'),texto)
        self.assertIsNone(ControlFortnite._boton_modo(p,'br'))

    def test_no_envia_entrada_con_lectura_vencida_control_extra_o_ventana_tapada(self):
        v=VistaFortnite.__new__(VistaFortnite);v._validar=Mock();v.a=Mock();v.g=Mock();v.c=Mock()
        t=Texto('JUGAR',(20,700,160,40));p=Pantalla(123,(0,0,1600,900),(t,),time.monotonic()-20)
        with self.assertRaises(ErrorFortnite):v.pulsar(p,t)
        v.a.mouse_event.assert_not_called();v.a.SetCursorPos.assert_not_called()
        p=Pantalla(123,(0,0,1600,900),(t,),time.monotonic());v.g.GetAncestor.return_value=999
        with self.assertRaises(ErrorFortnite):v.pulsar(p,t)
        v.a.mouse_event.assert_not_called()
        v._validar.side_effect=ErrorFortnite('foco')
        with self.assertRaises(ErrorFortnite):v.volver(p)
        v.a.keybd_event.assert_not_called()

    def test_ocr_no_transmite_imagenes_y_tiene_limite(self):
        import subprocess
        with patch('fortnite_vision.subprocess.run',return_value=Mock(returncode=0,stdout='[{"text":"JUGAR","rect":[20,30,40,15]}]')) as run:
            self.assertEqual(leer_imagen('foto.png')[0].texto,'JUGAR')
            self.assertEqual(run.call_args.kwargs['timeout'],9)
            self.assertEqual(run.call_args.args[0][0],'powershell.exe')
            self.assertNotIn('http',run.call_args.kwargs['input'])
        with patch('fortnite_vision.subprocess.run',side_effect=subprocess.TimeoutExpired('ocr',9)):
            with self.assertRaises(ErrorFortnite):leer_imagen('foto.png')

    def test_ficha_de_skin_lee_region_ampliada_de_izquierda_y_derecha_sin_entradas(self):
        from pathlib import Path
        from skins_fuentes import FuentesSkins
        v=self.vista();v._validar=Mock();rutas=[];tamanos=[]
        p=Pantalla(123,(0,0,1920,1080),(Texto('ATUENDO',(1060,135,100,17)),
            Texto('ATUENDO - ESTILO FO',(87,734,306,17)),Texto('PHILIP Z',(80,767,236,32))),time.monotonic())
        regiones=v.regiones_ficha(p);self.assertEqual(len(regiones),1)
        l,a,r,b=regiones[0];self.assertLessEqual(l,80);self.assertGreaterEqual(r,447);self.assertGreaterEqual(b,800)
        def ocr(ruta):
            rutas.append(Path(ruta))
            with Image.open(ruta) as im:tamanos.append(im.size)
            return (Texto('ATUENDO - ESTILO FO',(66,57,918,49)),Texto('PHILIP J. FR',(45,156,974,95)))
        with patch('PIL.ImageGrab.grab',return_value=Image.new('RGB',(1920,1080),'#1255aa')),patch('fortnite_vision.leer_imagen',side_effect=ocr):
            detalle=v.leer_ficha(p)
        self.assertEqual(FuentesSkins().fortnite_visible(detalle).skins[0]['perfil'],'fry')
        self.assertEqual(len(tamanos),2);self.assertGreater(tamanos[0][0],tamanos[1][0]);self.assertLessEqual(max(tamanos[0]),3600)
        self.assertTrue(all(not ruta.exists() for ruta in rutas))
        v.a.mouse_event.assert_not_called();v.a.keybd_event.assert_not_called()
        derecha=Pantalla(123,(0,0,1920,1080),(Texto('OUTFIT - FORTNITE STYLE',(1200,830,350,20)),),time.monotonic())
        l,a,r,b=v.regiones_ficha(derecha)[0];self.assertGreater(l,1000);self.assertLessEqual(r,1920);self.assertLessEqual(b,1080)


if __name__=='__main__':unittest.main()
