"""Panel Fortnite: preferencias locales y acciones explícitas del lobby."""
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui
from fortnite import MODOS,EQUIPOS,normalizar

CIAN='#5ce2e7'
TEXTOS=('Configurar Fortnite','Tu escuadrón. Tu próxima partida.','EXPERIENCIA','TAMAÑO DEL EQUIPO',
        'Modo actual','Equipo actual','Cero construcción','Solo','Dúo','Trío','Squad',
        'Conservar el modo del juego','Construye y compite','Combate sin construir',
        'Conservar el equipo del juego','Aplicar en Fortnite','Aplicar opciones sin buscar partida',
        'Elige tus opciones. Buscar partida las aplica antes de pulsar Jugar.',
        'Tus cambios se guardan al instante en este equipo.',
        'Clasificatoria y rellenar equipo se conservan como estén en Fortnite.',
        'Cancelar no vuelve a iniciar la búsqueda.',
        'Fortnite se comprueba al pulsar una acción.')


class TarjetaFortnite(LienzoUI):
    def __init__(self,padre,titulo,detalle,numero,command):
        super().__init__(padre,bg=FONDO,highlightthickness=0,height=104,cursor='hand2',takefocus=True)
        self.titulo=titulo;self.detalle=detalle;self.numero=numero;self.command=command;self.activa=False
        self.bind('<Configure>',lambda e:self.dibujar());self.bind('<Button-1>',lambda e:self.command())
        self.bind('<Return>',lambda e:self.command());self.bind('<space>',lambda e:self.command())
        self.bind('<FocusIn>',lambda e:self.dibujar());self.bind('<FocusOut>',lambda e:self.dibujar())

    def dibujar(self):
        self.delete('all');an=max(80,self.winfo_width());color=CIAN if self.activa else '#644184'
        self.create_polygon(1,1,an-12,1,an-1,12,an-1,102,12,102,1,91,fill=TARJETA,outline=color,width=2 if self.activa else 1)
        if self.numero:
            n=self.numero
            for i in range(n):
                x=an/2+(i-(n-1)/2)*19
                self.create_oval(x-4,17,x+4,25,fill=color,outline='')
                self.create_polygon(x-7,29,x+7,29,x+9,43,x-9,43,fill=color,outline='')
        else:
            self.create_line(an/2-20,20,an/2+20,20,an/2+9,32,an/2-9,32,an/2-20,20,fill=color,width=2)
            self.create_line(an/2-9,32,an/2,44,an/2+9,32,fill=color,width=2)
        self.create_text(an/2,61,text=ui(self.titulo),fill=TEXTO,font=(FAMILIA,12,'bold'))
        if self.detalle:self.create_text(an/2,84,text=ui(self.detalle),fill=SUAVE,font=(FAMILIA,8))
        if self.activa:self.create_line(12,97,an-12,97,fill=CIAN,width=3)


class PanelFortnite:
    def __init__(self,padre,config,guardar,enviar,control,ocultar=None):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.control=control;self.cerrado=False
        self.ventana=w=tk.Toplevel(padre);w.withdraw();w.title('Capri · Fortnite')
        w.geometry(f'{min(820,w.winfo_screenwidth()-64)}x{min(840,w.winfo_screenheight()-80)}');w.minsize(680,560)
        marco=VentanaCyber(w,'FORTNITE',self.cerrar,minimizar=ocultar);w.protocol('WM_DELETE_WINDOW',self.cerrar)
        cont=tk.Frame(marco.cuerpo,bg=FONDO);cont.pack(fill='both',expand=True)
        self.scroll=LienzoUI(cont,bg=FONDO,highlightthickness=0);self.scroll.pack(side='left',fill='both',expand=True)
        barra=tk.Scrollbar(cont,command=self.scroll.yview);barra.pack(side='right',fill='y');self.scroll.configure(yscrollcommand=barra.set)
        f=tk.Frame(self.scroll,bg=FONDO);item=self.scroll.create_window(0,0,window=f,anchor='nw')
        def ajustar(e=None):
            ancho=self.scroll.winfo_width();alto=max(self.scroll.winfo_height(),f.winfo_reqheight())
            self.scroll.itemconfigure(item,width=ancho,height=alto);self.scroll.configure(scrollregion=(0,0,ancho,alto))
        self.scroll.bind('<Configure>',ajustar);f.bind('<Configure>',ajustar)
        w.bind('<MouseWheel>',lambda e:self.scroll.yview_scroll(-int(e.delta/120),'units'))
        self.contenido=f
        cab=tk.Frame(f,bg=FONDO);cab.pack(fill='x',padx=20,pady=(10,14))
        tk.Label(cab,text='FORTNITE // LOBBY',bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold')).pack(anchor='w')
        tk.Label(cab,text=ui('Tu escuadrón. Tu próxima partida.'),bg=FONDO,fg=TEXTO,font=(FAMILIA,23,'bold')).pack(anchor='w',pady=(4,4))
        tk.Label(cab,text=ui('Elige tus opciones. Buscar partida las aplica antes de pulsar Jugar.'),
                 bg=FONDO,fg=SUAVE,font=(FAMILIA,10),wraplength=700,justify='left').pack(anchor='w')
        self.tarjetas={}
        self.seccion(f,'EXPERIENCIA')
        modos=tk.Frame(f,bg=FONDO);modos.pack(fill='x',padx=17,pady=(0,12))
        for i,(k,detalle) in enumerate((('actual','Conservar el modo del juego'),('br','Construye y compite'),('cero','Combate sin construir'))):
            modos.columnconfigure(i,weight=1,uniform='modos')
            t=TarjetaFortnite(modos,MODOS[k][0],detalle,0,lambda v=k:self.elegir('modo',v))
            t.grid(row=0,column=i,sticky='ew',padx=3);self.tarjetas['modo',k]=t
        self.seccion(f,'TAMAÑO DEL EQUIPO')
        equipo=tk.Frame(f,bg=FONDO);equipo.pack(fill='x',padx=17)
        self.actual=tk.BooleanVar(value=self.config['equipo']=='actual')
        from ajustes_ui import InterruptorCyber
        InterruptorCyber(equipo,text='Conservar el equipo del juego',variable=self.actual,
                         command=lambda:self.elegir('equipo','actual' if self.actual.get() else 'solo'),
                         bg=FONDO,fg=SUAVE).grid(row=0,column=0,columnspan=4,sticky='w',padx=3,pady=(0,10))
        for i,k in enumerate(('solo','duo','trio','squad')):
            equipo.columnconfigure(i,weight=1,uniform='equipo')
            t=TarjetaFortnite(equipo,EQUIPOS[k][0],'',i+1,lambda v=k:self.elegir('equipo',v))
            t.grid(row=1,column=i,sticky='ew',padx=3);self.tarjetas['equipo',k]=t
        tk.Label(f,text=ui('Clasificatoria y rellenar equipo se conservan como estén en Fortnite.'),bg=FONDO,fg=SUAVE,
                 font=(FAMILIA,9),wraplength=700,justify='left').pack(anchor='w',padx=20,pady=(12,16))
        estado=tk.Frame(f,bg=TARJETA);estado.pack(fill='x',padx=20)
        self.estado=tk.StringVar(value=ui(control.estado))
        tk.Label(estado,textvariable=self.estado,bg=TARJETA,fg=TEXTO,wraplength=680,justify='left',anchor='w',
                 font=(FAMILIA,10)).pack(fill='x',padx=14,pady=13)
        self.acciones={};acciones=tk.Frame(f,bg=FONDO);acciones.pack(fill='x',padx=17,pady=(12,6))
        for i,(texto,orden) in enumerate((('Buscar partida','busca partida en fortnite'),('Cancelar búsqueda','cancela la cola en fortnite'))):
            acciones.columnconfigure(i,weight=1)
            b=BotonCyber(acciones,text=texto,command=lambda o=orden:self.accion(o));b.grid(row=0,column=i,sticky='ew',padx=3)
            self.acciones[texto]=b
        b=BotonCyber(f,text='Aplicar opciones sin buscar partida',command=lambda:self.accion('aplica mis opciones en fortnite'))
        b.pack(fill='x',padx=20,pady=(2,10));self.acciones['Aplicar en Fortnite']=b
        for texto in ('Cancelar no vuelve a iniciar la búsqueda.','Tus cambios se guardan al instante en este equipo.'):
            tk.Label(f,text=ui(texto),bg=FONDO,fg=SUAVE,font=(FAMILIA,9)).pack(anchor='w',padx=20,pady=(0,4))
        tk.Frame(f,bg=FONDO,height=12).pack()
        self.pintar();w.deiconify();self.refrescar()

    @staticmethod
    def seccion(padre,texto):
        tk.Label(padre,text=ui(texto),bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold')).pack(anchor='w',padx=20,pady=(2,9))

    def elegir(self,campo,valor):
        self.config=normalizar({**self.config,campo:valor});self.guardar('fortnite',dict(self.config));self.pintar()

    def pintar(self):
        self.actual.set(self.config['equipo']=='actual')
        for (campo,valor),t in self.tarjetas.items():t.activa=self.config[campo]==valor;t.dibujar()

    def accion(self,orden):
        aceptada=self.enviar(orden)
        if aceptada is not False:self.ventana.withdraw()

    def refrescar(self):
        if self.cerrado:return
        self.estado.set(ui(self.control.estado));self._after=self.ventana.after(300,self.refrescar)

    def cerrar(self):
        self.cerrado=True
        if getattr(self,'_after',None):self.ventana.after_cancel(self._after)
        self.ventana.destroy()
