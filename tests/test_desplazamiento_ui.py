from test_capri import PruebasTk
from tema_ui import tk
from desplazamiento_ui import Desplazable

class Desplazamiento(PruebasTk):
    def crear(self):
        r=tk.Tk();r.geometry('300x420');self.addCleanup(r.destroy)
        d=Desplazable(r);d.pack(fill='both',expand=True)
        return r,d
    def test_contenido_corto_no_se_mueve_en_ninguna_direccion(self):
        r,d=self.crear();tk.Label(d.interior,text='The Maze',height=3).pack(fill='x');d.conectar();r.update()
        for sentido in (-3,3):
            for _ in range(12):d.mover(sentido)
            r.update();self.assertEqual(d.lienzo.canvasy(0),0)
            self.assertEqual(d.lienzo.yview(),(0.,1.));self.assertFalse(d.barra.winfo_ismapped())
    def test_al_ampliar_vista_que_cabe_recoloca_la_lista_arriba(self):
        r,d=self.crear();r.geometry('300x140')
        for i in range(8):tk.Label(d.interior,text=str(i),height=2).pack(fill='x')
        r.update();d.mover(9);r.update();self.assertGreater(d.lienzo.canvasy(0),0)
        r.geometry('300x600');r.update()
        self.assertEqual(d.lienzo.canvasy(0),0);self.assertFalse(d.barra.winfo_ismapped())
    def test_lista_larga_respeta_ambos_extremos_sin_huecos(self):
        r,d=self.crear()
        for i in range(35):tk.Label(d.interior,text=str(i),height=2).pack(fill='x')
        r.update();d.mover(10000);r.update()
        self.assertEqual(d.lienzo.yview()[1],1)
        d.mover(-10000);r.update();self.assertEqual(d.lienzo.canvasy(0),0)

if __name__=='__main__':__import__('unittest').main()
