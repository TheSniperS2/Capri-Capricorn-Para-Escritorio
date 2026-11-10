from types import SimpleNamespace
from unittest.mock import patch
from test_capri import PruebasTk
from tema_ui import tk
from ajustes_ui import VentanaCyber, BotonCyber


class RedimensionAjustes(PruebasTk):
    def setUp(self):
        super().setUp()
        self.root=tk.Tk();self.root.withdraw()
        self.p=tk.Toplevel(self.root);self.p.geometry('800x740+100+100');self.p.minsize(720,560)
        self.m=VentanaCyber(self.p,'PRUEBA')
        self.entrada=tk.Entry(self.m.cuerpo);self.entrada.pack(fill='x',padx=20,pady=20)
        self.pulsaciones=[]
        self.boton=BotonCyber(self.m.cuerpo,text='Continuar',command=lambda:self.pulsaciones.append(True))
        self.boton.pack(fill='x',padx=20)
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        super().tearDown()

    def iniciar(self,lado='se'):
        w,h=self.p.winfo_width(),self.p.winfo_height()
        x=3 if 'w' in lado else (w-3 if 'e' in lado else w//2)
        y=3 if 'n' in lado else (h-3 if 's' in lado else h//2)
        e=SimpleNamespace(x=x,y=y,x_root=self.p.winfo_rootx()+x,y_root=self.p.winfo_rooty()+y)
        self.m.iniciar(e)
        return e

    def test_soltar_sobre_un_control_libera_el_raton_y_permite_usar_la_interfaz(self):
        self.iniciar()
        self.assertIs(self.p.grab_current(),self.m.canvas)
        self.entrada.event_generate('<ButtonRelease-1>',x=3,y=3)
        self.root.update()
        self.assertIsNone(self.m.resize);self.assertIsNone(self.p.grab_current())
        self.assertEqual(self.m.canvas.cget('cursor'),'')
        self.assertEqual(self.m.cuerpo.cget('cursor'),'arrow')
        self.assertEqual(self.entrada.cget('cursor'),'xterm')
        self.boton.event_generate('<ButtonPress-1>',x=30,y=15)
        self.boton.event_generate('<ButtonRelease-1>',x=30,y=15)
        self.root.update()
        self.assertEqual(self.pulsaciones,[True])

    def test_salir_del_marco_y_recuperarse_de_una_liberacion_perdida(self):
        self.m.canvas.event_generate('<Motion>',x=3,y=200)
        self.assertTrue(self.m.canvas.cget('cursor'))
        self.m.canvas.event_generate('<Leave>')
        self.entrada.event_generate('<Enter>',state=0)
        self.assertEqual(self.m.canvas.cget('cursor'),'')
        self.iniciar()
        self.entrada.event_generate('<Motion>',state=0,x=20,y=10)
        self.assertIsNone(self.m.resize);self.assertIsNone(self.p.grab_current())
        geometria=self.p.geometry()
        self.entrada.event_generate('<B1-Motion>',state=256,x=100,y=10)
        self.root.update()
        self.assertEqual(self.p.geometry(),geometria)

    def test_solo_aplica_la_posicion_mas_reciente_y_no_salta_al_soltar(self):
        inicio=self.iniciar()
        with patch.object(self.p,'geometry',wraps=self.p.geometry) as aplicar:
            for delta in range(1,81):
                self.m.mover(SimpleNamespace(x_root=inicio.x_root+delta,y_root=inicio.y_root+delta))
            self.assertEqual(aplicar.call_count,0)
            self.m.canvas.event_generate('<ButtonRelease-1>',x=-40,y=-40)
            self.root.update()
            self.assertEqual(aplicar.call_count,1)
            self.assertEqual((self.p.winfo_width(),self.p.winfo_height()),(880,820))
            self.assertIsNone(self.m._geometria_tarea);self.assertIsNone(self.p.grab_current())
            self.root.update()
            self.assertEqual(aplicar.call_count,1)

    def test_ocultar_o_cerrar_durante_un_arrastre_no_deja_capturas_ni_tareas(self):
        self.iniciar();self.m.mover(SimpleNamespace(x_root=1000,y_root=900))
        self.p.withdraw();self.root.update()
        self.assertIsNone(self.m.resize);self.assertIsNone(self.m._geometria_tarea)
        self.assertIsNone(self.p.grab_current())
        self.p.deiconify();self.root.update();self.iniciar()
        self.m.mover(SimpleNamespace(x_root=950,y_root=850))
        self.p.destroy();self.root.update()
        self.assertIsNone(self.m._geometria_tarea);self.assertIsNone(self.root.grab_current())

    def test_el_tamano_se_actualiza_aunque_sigan_llegando_eventos(self):
        inicio=self.iniciar();vistos=[]
        self.m.mover(SimpleNamespace(x_root=inicio.x_root+100,y_root=inicio.y_root+60))
        listo=tk.BooleanVar(master=self.root)
        def comprobar():
            vistos.append((self.p.winfo_width(),self.p.winfo_height()))
            self.m.mover(SimpleNamespace(x_root=inicio.x_root+120,y_root=inicio.y_root+80))
            listo.set(True)
        self.root.after(20,comprobar)
        self.root.wait_variable(listo)
        self.assertEqual(vistos,[(900,800)])
        self.m.terminar_arrastre();self.root.update()

    def test_contenido_se_adapta_y_repinta_durante_una_secuencia_sin_perder_la_entrada(self):
        self.entrada.insert(0,'Mi playlist')
        etiqueta=tk.Label(self.m.cuerpo,text='Texto que no cambia')
        etiqueta.place(x=20,y=160,width=220,height=24)
        self.root.update();exposiciones=[]
        etiqueta.bind('<Expose>',lambda e:exposiciones.append(True),add='+')
        for ancho,alto in ((940,800),(720,560),(1000,860),(760,580)):
            with self.subTest(tamano=(ancho,alto)):
                antes=len(exposiciones)
                self.m.pedir_geometria(f'{ancho}x{alto}+100+100');self.root.update()
                self.assertEqual((self.m.cuerpo.winfo_width(),self.m.cuerpo.winfo_height()),(ancho-28,alto-68))
                self.assertGreater(len(exposiciones),antes)
                self.assertEqual(self.entrada.get(),'Mi playlist')
                self.assertIsNone(self.m._geometria_tarea)
                self.assertIsNone(self.m._repintado)
        self.assertEqual(self.m.cuerpo.winfo_manager(),'place')
        self.assertIs(self.m.cuerpo.master,self.p)

    def test_apertura_resuelve_el_tamano_sin_ejecutar_trabajo_de_timer_pendiente(self):
        ejecutados=[]
        self.root.after(0,lambda:ejecutados.append(True))
        self.p.geometry('940x800+100+100');self.m.mostrar_completa()
        self.assertEqual((self.p.winfo_width(),self.p.winfo_height()),(940,800))
        self.assertEqual(ejecutados,[])
        self.root.update();self.assertEqual(ejecutados,[True])

    def test_preparar_una_vista_agrupa_repintados_y_conserva_su_pintado_final(self):
        with patch('ventanas.repintar_ventana',wraps=__import__('ventanas').repintar_ventana) as pintar:
            with self.m.cambio_de_vista():
                self.p.geometry('940x800+100+100')
                self.m.repintar();self.m.pedir_repintado();self.p.update_idletasks()
                self.assertEqual(pintar.call_count,0)
            self.assertEqual(pintar.call_count,2)
        self.assertEqual(float(self.p.attributes('-alpha')),1.)
        self.assertEqual(self.m._preparando,0)

    def test_ancho_de_boton_cacheado_se_adapta_a_la_escala(self):
        from tkinter import font
        with patch.object(font.Font,'measure',autospec=True,side_effect=font.Font.measure) as medir:
            a=BotonCyber(self.m.cuerpo,text='Buscar partida',font=('Chakra Petch',9,'bold'))
            primera=medir.call_count
            b=BotonCyber(self.m.cuerpo,text='Buscar partida',font=('Chakra Petch',9,'bold'))
            self.assertEqual(medir.call_count,primera)
            self.assertEqual(a.cget('width'),b.cget('width'))
            escala=float(self.root.tk.call('tk','scaling'))
            try:
                self.root.tk.call('tk','scaling',escala*1.2)
                BotonCyber(self.m.cuerpo,text='Buscar partida',font=('Chakra Petch',9,'bold'))
                self.assertGreater(medir.call_count,primera)
            finally:self.root.tk.call('tk','scaling',escala)

    def test_ocho_bordes_respetan_minimo_y_conservan_el_lado_opuesto(self):
        with patch('companera.area_trabajo',return_value=(0,0,1920,1080)):
            for lado in ('n','s','e','w','ne','nw','se','sw'):
                self.p.geometry('800x740+100+100');self.root.update()
                inicio=self.iniciar(lado)
                self.m.mover(SimpleNamespace(x_root=inicio.x_root+(2000 if 'w' in lado else -2000),
                                            y_root=inicio.y_root+(2000 if 'n' in lado else -2000)))
                self.m.terminar_arrastre();self.root.update()
                with self.subTest(lado=lado):
                    self.assertGreaterEqual(self.p.winfo_width(),720)
                    self.assertGreaterEqual(self.p.winfo_height(),560)
                    if 'w' in lado:self.assertEqual(self.p.winfo_x()+self.p.winfo_width(),900)
                    elif 'e' in lado:self.assertEqual(self.p.winfo_x(),100)
                    if 'n' in lado:self.assertEqual(self.p.winfo_y()+self.p.winfo_height(),840)
                    elif 's' in lado:self.assertEqual(self.p.winfo_y(),100)

    def test_redimensionar_reutiliza_textos_y_conserva_estados_y_traduccion(self):
        from idiomas import activar
        with patch.object(self.m.canvas,'create_text',wraps=self.m.canvas.create_text) as titulo, \
             patch.object(self.boton,'create_text',wraps=self.boton.create_text) as texto:
            for ancho in (840,900,760,800):
                self.p.geometry(f'{ancho}x740+100+100');self.root.update()
                self.assertEqual(self.boton.coords(self.boton._texto_boton)[0],self.boton.winfo_width()/2)
            self.assertEqual(titulo.call_count,0);self.assertEqual(texto.call_count,0)
        self.boton.configure(text='Cancelar',state='disabled')
        self.boton.invoke();self.assertEqual(self.pulsaciones,[])
        self.assertEqual(self.boton.itemcget(self.boton._texto_boton,'text'),'Cancelar')
        self.boton.configure(state='normal');self.boton.invoke();self.assertEqual(self.pulsaciones,[True])
        activar('en')
        try:
            self.boton.retraducir()
            self.p.geometry('900x740+100+100');self.root.update()
            self.assertEqual(self.boton.itemcget(self.boton._texto_boton,'text'),'Cancel')
        finally:activar('es')
