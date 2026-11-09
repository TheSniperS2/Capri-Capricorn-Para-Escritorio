"""Preferencias de mapas de CS2 y acciones explícitas del menú Competitivo."""
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from desplazamiento_ui import Desplazable
from fuentes import FAMILIA
from idiomas import ui
from counter_strike import MAPAS,normalizar,clave

TEXTOS=('Configurar Counter-Strike','Tus mapas. Tu próxima partida.','COMPETITIVO · COUNTER-STRIKE 2',
        'Selecciona los mapas que quieras. Capri los comprueba en el juego antes de buscar.',
        'Filtrar mapas','Escribe el nombre de un mapa…','Leer mapas del juego','Aplicar mapas sin buscar',
        'Elige al menos un mapa para buscar.','{0} mapas seleccionados','No hay mapas con ese nombre.',
        'Tus mapas se guardan al instante en este equipo.','Cancelar no vuelve a iniciar la búsqueda.',
        'Las acciones recuperan el juego si está minimizado. La aceptación de partida queda a tu cargo.',
        'La lista del juego puede cambiar. Leer mapas del juego actualiza los disponibles; conserva los mapas guardados que ya no estén.',
        'Counter-Strike 2 se comprueba al pulsar una acción.')


class TarjetaMapa(LienzoUI):
    def __init__(self,padre,nombre,activo,command):
        super().__init__(padre,bg=FONDO,highlightthickness=0,height=86,cursor='hand2',takefocus=True)
        self.nombre=nombre;self.activo=activo;self.command=command
        self.bind('<Configure>',lambda e:self.dibujar());self.bind('<Button-1>',lambda e:command())
        self.bind('<Return>',lambda e:command());self.bind('<space>',lambda e:command())
        self.bind('<FocusIn>',lambda e:self.dibujar());self.bind('<FocusOut>',lambda e:self.dibujar())
    def dibujar(self):
        self.delete('all');w=max(120,self.winfo_width());color=ACENTO if self.activo else '#6b3a4c'
        self.create_polygon(1,1,w-14,1,w-1,14,w-1,84,14,84,1,71,fill=TARJETA,outline=color,width=2 if self.activo else 1)
        self.create_line(15,14,42,14,fill=color,width=3)
        abreviatura='D2' if self.nombre=='Dust II' else ''.join(n[0] for n in self.nombre.split())[:2].upper()
        if len(abreviatura)==1:abreviatura=self.nombre[:2].upper()
        self.create_text(17,37,text=abreviatura,anchor='w',fill=color,font=(FAMILIA,12,'bold'),traducir=False)
        self.create_text(17,64,text=self.nombre,anchor='w',fill=TEXTO,font=(FAMILIA,13,'bold'),traducir=False)
        self.create_rectangle(w-34,15,w-16,33,fill=ACENTO if self.activo else FONDO,outline=color)
        if self.activo:self.create_line(w-31,24,w-26,29,w-19,19,fill=FONDO,width=2)


class PanelCS2:
    def __init__(self,raiz,config,guardar,enviar,control):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.control=control;self.cerrado=False;self._after=None
        self.ventana=w=tk.Toplevel(raiz);w.withdraw();w.title('Capri · Counter-Strike 2');w.geometry('850x730');w.minsize(680,540)
        w.protocol('WM_DELETE_WINDOW',self.cerrar);w.bind('<Escape>',lambda e:self.cerrar())
        marco=VentanaCyber(w,'COUNTER-STRIKE 2',cerrar=self.cerrar);f=marco.cuerpo
        self.titulo=self.etiqueta(f,'Tus mapas. Tu próxima partida.',TEXTO,23);self.titulo.pack(anchor='w',padx=18,pady=(6,4))
        self.etiqueta(f,'COMPETITIVO · COUNTER-STRIKE 2',ACENTO,10).pack(anchor='w',padx=18,pady=(0,8))
        self.descripcion=self.etiqueta(f,'Selecciona los mapas que quieras. Capri los comprueba en el juego antes de buscar.',SUAVE,10);self.descripcion.pack(fill='x',padx=18,pady=(0,10))
        pie=self.pie=tk.Frame(f,bg=FONDO);pie.pack(side='bottom',fill='x',padx=18,pady=(10,6))
        self.resumen=tk.StringVar();self.etiqueta_resumen=self.etiqueta(pie,'',ACENTO,10,textvariable=self.resumen);self.etiqueta_resumen.pack(anchor='w',pady=(0,6))
        self.estado=tk.StringVar();self.etiqueta_estado=self.etiqueta(pie,'',SUAVE,10,textvariable=self.estado);self.etiqueta_estado.pack(fill='x',pady=(0,8))
        acciones=tk.Frame(pie,bg=FONDO);acciones.pack(fill='x');self.acciones={}
        for i,(titulo,orden) in enumerate((('Buscar partida','busca partida en cs2'),('Cancelar búsqueda','cancela la cola en cs2'),('Aplicar mapas sin buscar','aplica mis mapas en cs2'))):
            acciones.columnconfigure(i,weight=1,uniform='acciones')
            b=BotonCyber(acciones,text=titulo,command=lambda o=orden:self.accion(o),estilo='principal' if i==0 else 'angular',bg=ACENTO if i==0 else TARJETA,fg=FONDO if i==0 else TEXTO)
            b.grid(row=0,column=i,sticky='ew',padx=(0,8) if i<2 else 0);self.acciones[titulo]=b
        self.etiqueta_cancelar=self.etiqueta(pie,'Cancelar no vuelve a iniciar la búsqueda.',SUAVE,9);self.etiqueta_cancelar.pack(anchor='w',pady=(8,0))
        self.etiqueta_recuperar=self.etiqueta(pie,'Las acciones recuperan el juego si está minimizado. La aceptación de partida queda a tu cargo.',SUAVE,9);self.etiqueta_recuperar.pack(fill='x',pady=(5,0))
        barra=self.barra=tk.Frame(f,bg=FONDO);barra.pack(fill='x',padx=18,pady=(0,10))
        self.etiqueta(barra,'Filtrar mapas',SUAVE,10).pack(anchor='w',pady=(0,4))
        fila=tk.Frame(barra,bg=TARJETA,highlightthickness=1,highlightbackground='#6b3a4c');fila.pack(fill='x')
        self.filtro=tk.StringVar();self.entrada=tk.Entry(fila,textvariable=self.filtro,bg=TARJETA,fg=TEXTO,insertbackground=ACENTO,relief='flat',font=(FAMILIA,11));self.entrada.pack(side='left',fill='x',expand=True,padx=10,pady=10)
        self.placeholder=tk.Label(self.entrada,text=ui('Escribe el nombre de un mapa…'),bg=TARJETA,fg=SUAVE,font=(FAMILIA,10),anchor='w',cursor='xterm')
        self.placeholder.bind('<Button-1>',lambda e:self.entrada.focus_set())
        BotonCyber(fila,text='Leer mapas del juego',command=lambda:self.accion('lee los mapas de cs2'),font=(FAMILIA,9,'bold')).pack(side='right',padx=6,pady=4)
        self.lista=Desplazable(f,bg=FONDO);self.lista.pack(fill='both',expand=True,padx=15)
        self.tarjetas={};self._ancho=0;self._columnas=3;self._catalogo=()
        self.lista.bind('<Configure>',self.redimensionar,add='+');self.filtro.trace_add('write',lambda *a:self.llenar())
        self.entrada.bind('<FocusIn>',lambda e:self.placeholder.place_forget());self.entrada.bind('<FocusOut>',lambda e:self.placeholder_filtro())
        self.entrada.bind('<Escape>',self.limpiar)
        self.compacto=None;w.bind('<Configure>',self.ajustar_alto,add='+')
        self.llenar();self.refrescar();w.deiconify()

    def ajustar_alto(self,e):
        if e.widget is not self.ventana:return
        compacto=e.height<650
        if compacto==self.compacto:return
        self.compacto=compacto;self.titulo.configure(font=(FAMILIA,18 if compacto else 23))
        if compacto:self.descripcion.pack_forget()
        else:self.descripcion.pack(fill='x',padx=18,pady=(0,10),before=self.barra)
        self.entrada.pack_configure(pady=6 if compacto else 10)
        self.pie.pack_configure(pady=(6,4) if compacto else (10,6))
        self.etiqueta_resumen.pack_configure(pady=(0,2 if compacto else 6))
        self.etiqueta_estado.pack_configure(pady=(0,4 if compacto else 8))
        self.etiqueta_cancelar.pack_configure(pady=(4 if compacto else 8,0))
        self.etiqueta_recuperar.pack_configure(pady=(2 if compacto else 5,0))

    @staticmethod
    def etiqueta(p,t,color,tamano,**kw):
        l=tk.Label(p,text=ui(t),bg=p.cget('bg'),fg=color,font=(FAMILIA,tamano),anchor='w',justify='left',wraplength=700,**kw)
        l.bind('<Configure>',lambda e:l.configure(wraplength=max(180,e.width)));return l

    def placeholder_filtro(self):
        if not self.filtro.get() and self.entrada.focus_get() is not self.entrada:self.placeholder.place(x=0,y=0,relwidth=1,relheight=1)
        else:self.placeholder.place_forget()

    def limpiar(self,e=None):
        self.filtro.set('');return 'break'

    def redimensionar(self,e):
        columnas=3 if e.width>=660 else 2
        if columnas!=self._columnas:self._columnas=columnas;self.llenar()

    def llenar(self):
        self.placeholder_filtro()
        for hijo in self.lista.interior.winfo_children():hijo.destroy()
        self.tarjetas={};n=clave(self.filtro.get())
        nombres=self.config['detectados'] or list(MAPAS)
        nombres=list(dict.fromkeys([*nombres,*self.config['mapas']]))
        visibles=[s for s in nombres if n in clave(s)]
        for c in range(3):self.lista.interior.columnconfigure(c,weight=1 if c<self._columnas else 0,uniform='mapas' if c<self._columnas else '')
        for i,nombre in enumerate(visibles):
            t=TarjetaMapa(self.lista.interior,nombre,clave(nombre) in {clave(n) for n in self.config['mapas']},lambda s=nombre:self.elegir(s))
            t.grid(row=i//self._columnas,column=i%self._columnas,sticky='ew',padx=3,pady=3);self.tarjetas[nombre]=t
        if not visibles:self.etiqueta(self.lista.interior,'No hay mapas con ese nombre.',SUAVE,11).grid(row=0,column=0,columnspan=self._columnas,sticky='w',padx=10,pady=20)
        self.lista.conectar()
        cantidad=len(self.config['mapas']);self.resumen.set(ui('{0} mapas seleccionados').format(cantidad) if cantidad else ui('Elige al menos un mapa para buscar.'))
        for k in ('Buscar partida','Aplicar mapas sin buscar'):self.acciones[k].configure(state='normal' if cantidad else 'disabled')

    def elegir(self,nombre):
        mapas=self.config['mapas'];mapas=[s for s in mapas if clave(s)!=clave(nombre)] if any(clave(s)==clave(nombre) for s in mapas) else [*mapas,nombre]
        self.config=normalizar({**self.config,'mapas':mapas});self.guardar('cs2',self.config);self.llenar()

    def accion(self,orden):
        if self.enviar(orden) is not False:self.ventana.withdraw()

    def refrescar(self):
        if self.cerrado:return
        self.estado.set(ui(self.control.estado))
        detectados=tuple(self.control.catalogo)
        if detectados and detectados!=self._catalogo and not self.control._lock.locked():
            self._catalogo=detectados;self.config=normalizar({**self.config,'detectados':list(detectados)})
            self.guardar('cs2',self.config);self.llenar()
        self._after=self.ventana.after(400,self.refrescar)

    def cerrar(self):
        if self.cerrado:return
        self.cerrado=True
        if self._after:self.ventana.after_cancel(self._after);self._after=None
        self.ventana.destroy()
