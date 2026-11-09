import time,unittest
from unittest.mock import Mock,patch
from PIL import Image,ImageDraw
from fortnite import Texto,Pantalla,ErrorFortnite
from counter_strike import PantallaCS2,ErrorCS2
from counter_strike_vision import analizar,VistaCS2,casillas


def ejemplo(escala=1):
    im=Image.new('RGB',(1920,1080),(32,38,40));d=ImageDraw.Draw(im);textos=[]
    for s,rect in (('MATCHMAKING',(780,50,190,28)),('COMPETITIVE',(780,100,190,28))):
        x,y,w,h=rect;d.rectangle((x-6,y-3,x+w+6,y+h+3),fill=(35,90,120));textos.append(Texto(s,rect))
    for i,n in enumerate(('Mirage','Nuke','Dust II','Overpass','Office','Cache')):
        c=i%3;f=i//3;x=615+c*420;y=200+f*410
        if i in (1,3):
            d.rectangle((x,y,x+25,y+25),fill=(245,245,245));d.line((x+5,y+13,x+10,y+19,x+21,y+5),fill=(35,35,35),width=3)
        else:d.rectangle((x,y,x+25,y+25),outline=(200,200,200),width=2)
        textos.append(Texto(n,(x-125,y+310,100,28)))
        textos.append(Texto('Wait Time 02:00',(x-135,y+345,130,16)))
    if escala!=1:
        im=im.resize((round(im.width*escala),round(im.height*escala)))
        textos=[Texto(t.texto,tuple(v*escala for v in t.rect)) for t in textos]
    return im,Pantalla(123,(0,0,*im.size),tuple(textos),time.monotonic())


class Vision(unittest.TestCase):
    def test_casillas_seleccionadas_vacias_y_escalas(self):
        for escala in (.75,1,1.5):
            im,p=ejemplo(escala);q=analizar(p,im)
            self.assertTrue(q.online);self.assertTrue(q.competitivo);self.assertTrue(q.completa,(escala,[(m.nombre,m.seleccionado) for m in q.mapas]))
            self.assertEqual({m.nombre for m in q.mapas if m.seleccionado},{'Nuke','Overpass'})
    def test_casilla_oculta_o_menu_no_resaltado_no_se_da_por_valido(self):
        im,p=ejemplo();ImageDraw.Draw(im).rectangle((610,195,645,230),fill=(32,38,40))
        self.assertFalse(analizar(p,im).completa)
        im,p=ejemplo();ImageDraw.Draw(im).rectangle((770,44,980,82),fill=(32,38,40))
        self.assertFalse(analizar(p,im).online)
    def test_ocr_no_activa_si_no_se_pide_ni_envia_entradas_y_traduce_error(self):
        im,p=ejemplo();v=VistaCS2.__new__(VistaCS2);v._ventana=Mock(return_value=123);v._activar=Mock();v._validar=Mock();v.a=Mock();v.ocr=Mock()
        v.ocr.leer.return_value=p.textos
        def imagen(*a,**k):v.imagen=im;return im,p.rect,time.monotonic()
        v._imagen=imagen;q=v.capturar();self.assertTrue(q.completa);v._activar.assert_not_called();v.a.mouse_event.assert_not_called()
        v.capturar();self.assertEqual(v.ocr.leer.call_count,2)
        self.assertTrue(v.ocr.leer.call_args.kwargs['palabras']);self.assertEqual(v.NOMBRES,{'cs2.exe'})
        v._validar.side_effect=ErrorFortnite('Fortnite perdió el foco.')
        with self.assertRaisesRegex(ErrorCS2,'Counter-Strike 2 perdió el foco'):v.capturar()
        v.a.mouse_event.assert_not_called()
    def test_palabras_del_mismo_boton_no_son_dos_controles(self):
        p=PantallaCS2(123,(0,0,1920,1080),(Texto('Cancel Search',(1500,950,200,40)),Texto('Cancel',(1500,950,80,40))),time.monotonic())
        from counter_strike import CANCELAR,ZONA_BOTON
        self.assertEqual(p.buscar(CANCELAR,ZONA_BOTON).texto,'Cancel Search')


if __name__=='__main__':unittest.main()
