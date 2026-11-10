"""Sala de Valorant y tres preferencias, con retratos incluidos y sin red en Tk."""
import copy
import queue
import threading
from PIL import Image,ImageTk
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,InterruptorCyber,BarraCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui
from lol_ui import clave,CIAN
from valorant import normalizar,cargar_catalogo,carpeta_catalogo,MENSAJES
from valorant_cliente import ErrorValorant

TEXTOS=('Configurar Valorant','Tus agentes. En tu orden.','TRES PREFERENCIAS','Elegir agente','Quitar agente',
        'Selecciona una prioridad y pulsa un agente. Si está ocupado, Capri pasa a la siguiente.',
        'Si se agotan tus preferencias, no se selecciona ningún agente.',
        'Confirmar agente automáticamente','Confirmar agente en partida','Buscar agente…','AGENTES',
        'El modo y los servidores se eligen en Valorant. Cancelar no reinicia la búsqueda.',
        'Sin espera adicional. Se respetan los agentes señalados por aliados.',
        'Si la búsqueda se interrumpe y el motivo no es claro, Capri espera una nueva orden.')

class CampoBusqueda(LienzoUI):
    """Campo integrado con lupa, indicación interior y acción de limpiar."""
    def __init__(self,padre,variable):
        super().__init__(padre,width=330,height=44,bg=FONDO,highlightthickness=0)
        self.variable=variable;self.enfocado=False
        self.entrada=tk.Entry(self,textvariable=variable,bg=TARJETA,fg=TEXTO,insertbackground=CIAN,
                              relief='flat',bd=0,font=(FAMILIA,11),highlightthickness=0)
        self.entrada.place(x=40,y=10,relwidth=1,width=-79,height=24)
        self.indicacion=tk.Label(self,text=ui('Buscar agente…'),bg=TARJETA,fg=SUAVE,font=(FAMILIA,10),anchor='w')
        self.indicacion.bind('<Button-1>',lambda e:self.entrada.focus_set())
        self.entrada.bind('<FocusIn>',lambda e:self.enfocar(True));self.entrada.bind('<FocusOut>',lambda e:self.enfocar(False))
        self.entrada.bind('<Escape>',lambda e:self.limpiar())
        self.bind('<Configure>',lambda e:self.dibujar());self.bind('<Button-1>',self.pulsar)
        self._traza=variable.trace_add('write',lambda *_:self.dibujar())
        self.bind('<Destroy>',self.destruir,add='+');self.dibujar()
    def destruir(self,e):
        if e.widget==self:self.variable.trace_remove('write',self._traza)
    def enfocar(self,activo):self.enfocado=activo;self.dibujar()
    def limpiar(self):self.variable.set('');self.entrada.focus_set();return 'break'
    def pulsar(self,e):
        if e.x>self.winfo_width()-36 and self.variable.get():self.limpiar()
        else:self.entrada.focus_set()
    def dibujar(self):
        self.delete('campo');w=max(180,self.winfo_width())
        self.create_polygon(8,1,w-9,1,w-1,9,w-1,35,w-9,43,8,43,1,35,1,9,
                            fill=TARJETA,outline=CIAN if self.enfocado else '#55313e',tags='campo')
        self.create_oval(13,14,25,26,outline=CIAN,width=2,tags='campo');self.create_line(24,25,30,31,fill=CIAN,width=2,tags='campo')
        if self.variable.get():
            self.create_line(w-25,17,w-15,27,fill=SUAVE,width=2,tags='campo');self.create_line(w-25,27,w-15,17,fill=SUAVE,width=2,tags='campo')
        if not self.variable.get() and not self.enfocado:self.indicacion.place(x=40,y=10,relwidth=1,width=-79,height=24)
        else:self.indicacion.place_forget()

class CatalogoAgentes:
    def __init__(self,master):
        self.master=master;self.datos=cargar_catalogo();self.agentes={a['id']:a for a in self.datos['agents']};self.fotos={}
        with Image.open(carpeta_catalogo()/'agentes.png') as im:self.atlas=im.convert('RGBA')
    def foto(self,identificador,tamano=64):
        llave=(identificador,tamano)
        if llave not in self.fotos:
            a=self.agentes[identificador]['image'];x,y=a['x'],a['y']
            im=self.atlas.crop((x,y,x+a['w'],y+a['h'])).resize((tamano,tamano),Image.Resampling.LANCZOS)
            self.fotos[llave]=ImageTk.PhotoImage(im,master=self.master)
        return self.fotos[llave]

class PanelValorant:
    def __init__(self,padre,config,guardar,enviar,control,consultar=True,ocultar=None,contenedor=None):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.control=control
        self.activa=0;self.cerrado=False;self._stop=threading.Event();self._consulta_error=None;self._eventos=queue.Queue()
        from paneles_integrados import preparar_panel
        integrado=contenedor is not None
        self.ventana,marco=preparar_panel(padre,'Valorant',self,(960,900),(800,620),ocultar,contenedor)
        w=self.ventana
        self.catalogo=CatalogoAgentes(w)
        cont=tk.Frame(marco.cuerpo,bg=FONDO);cont.pack(fill='both',expand=True)
        self.scroll=LienzoUI(cont,bg=FONDO,highlightthickness=0);self.scroll.pack(side='left',fill='both',expand=True)
        barra=BarraCyber(cont,self.scroll.yview);barra.pack(side='right',fill='y');self.scroll.configure(yscrollcommand=barra.set)
        f=tk.Frame(self.scroll,bg=FONDO);item=self.scroll.create_window(0,0,window=f,anchor='nw')
        def ajustar(e=None):
            ancho=self.scroll.winfo_width();alto=max(self.scroll.winfo_height(),f.winfo_reqheight())
            self.scroll.itemconfigure(item,width=ancho,height=alto);self.scroll.configure(scrollregion=(0,0,ancho,alto))
        self.scroll.bind('<Configure>',ajustar);f.bind('<Configure>',ajustar)
        w.bind('<MouseWheel>',lambda e:self.scroll.yview_scroll(-int(e.delta/120),'units'))
        cab=tk.Frame(f,bg=FONDO);cab.pack(fill='x',padx=20,pady=(12,10))
        tk.Label(cab,text='VALORANT',bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold')).pack(anchor='w')
        tk.Label(cab,text=ui('Tus agentes. En tu orden.'),bg=FONDO,fg=TEXTO,font=(FAMILIA,25,'bold')).pack(anchor='w')
        acciones=tk.Frame(f,bg=TARJETA);acciones.pack(fill='x',padx=20)
        self.acciones={}
        for texto,orden in (('Buscar partida','busca partida en valorant'),('Cancelar búsqueda','cancela la cola en valorant'),
                            ('Confirmar agente en partida','confirma mi agente en valorant')):
            boton=BotonCyber(acciones,text=texto,command=lambda o=orden:self.enviar(o),padx=10)
            boton.pack(side='left',fill='x',expand=True,padx=8,pady=12);self.acciones[texto]=boton
        tk.Label(f,text=ui('El modo y los servidores se eligen en Valorant. Cancelar no reinicia la búsqueda.'),
                 bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=850,justify='left').pack(anchor='w',padx=22,pady=(8,4))
        self.cola=tk.StringVar(value=ui(control.cola_estado))
        tk.Label(f,textvariable=self.cola,bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold'),wraplength=850,justify='left').pack(anchor='w',padx=22,pady=(0,14))
        tk.Label(f,text=ui('TRES PREFERENCIAS'),bg=FONDO,fg=SUAVE,font=(FAMILIA,10,'bold')).pack(anchor='w',padx=22)
        tarjetas=tk.Frame(f,bg=FONDO);tarjetas.pack(fill='x',padx=20,pady=(7,4));self.slots=[];self._slots_pintados={}
        for i in range(3):
            cv=LienzoUI(tarjetas,bg=FONDO,highlightthickness=0,height=100,takefocus=True,cursor='hand2')
            cv.grid(row=0,column=i,sticky='ew',padx=(0,8) if i<2 else 0);tarjetas.columnconfigure(i,weight=1,uniform='preferencias')
            cv.bind('<Configure>',lambda e,n=i:self.dibujar_slot(n));cv.bind('<Button-1>',lambda e,n=i:self.activar(n))
            cv.bind('<Return>',lambda e,n=i:self.activar(n));cv.bind('<space>',lambda e,n=i:self.activar(n));self.slots.append(cv)
        instrucciones=tk.Frame(f,bg=FONDO);instrucciones.pack(fill='x',padx=22)
        tk.Label(instrucciones,text=ui('Selecciona una prioridad y pulsa un agente. Si está ocupado, Capri pasa a la siguiente.'),
                 bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=650,justify='left').pack(side='left')
        BotonCyber(instrucciones,text='Quitar agente',command=lambda:self.elegir(''),padx=8,font=(FAMILIA,9,'bold')).pack(side='right')
        self.automatico=tk.BooleanVar(value=self.config['auto_pick'])
        InterruptorCyber(f,text='Confirmar agente automáticamente',variable=self.automatico,command=self.cambiar_auto).pack(fill='x',padx=22,pady=(5,0))
        tk.Label(f,text=ui('Sin espera adicional. Se respetan los agentes señalados por aliados.'),
                 bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=850,justify='left').pack(anchor='w',padx=22)
        self.estado=tk.StringVar(value=ui(control.estado))
        tk.Label(f,textvariable=self.estado,bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold'),wraplength=850,justify='left').pack(anchor='w',padx=22,pady=(5,0))
        busqueda=tk.Frame(f,bg=FONDO);busqueda.pack(fill='x',padx=22,pady=(14,8))
        tk.Label(busqueda,text=ui('AGENTES'),bg=FONDO,fg=CIAN,font=(FAMILIA,11,'bold')).pack(side='left')
        self.busqueda=tk.StringVar()
        self.campo_busqueda=CampoBusqueda(busqueda,self.busqueda);self.campo_busqueda.pack(side='right')
        self.entrada=self.campo_busqueda.entrada
        self.grid=tk.Frame(f,bg=FONDO);self.grid.pack(fill='x',padx=20)
        self.busqueda.trace_add('write',lambda *_:self.filtrar());self.filtrar()
        tk.Label(f,text=ui('Si se agotan tus preferencias, no se selecciona ningún agente.'),bg=FONDO,fg=SUAVE,
                 font=(FAMILIA,9),wraplength=850,justify='left').pack(anchor='w',padx=22,pady=(12,0))
        tk.Label(f,text=ui('Tus cambios se guardan al instante'),bg=FONDO,fg=SUAVE,font=(FAMILIA,9)).pack(anchor='w',padx=22,pady=(0,10))
        self.dibujar();self.refrescar()
        if not integrado:w.update_idletasks();ajustar()
        w.deiconify()
        if consultar:threading.Thread(target=PanelValorant._consultar,args=(control,self._stop,self._eventos),daemon=True).start()

    def activar(self,indice):self.activa=indice;self.dibujar()
    def elegir(self,identificador):
        lista=self.config['preferencias']
        if identificador:
            for i,v in enumerate(lista):
                if v==identificador and i!=self.activa:lista[i]=''
        lista[self.activa]=identificador;self.persistir();self.dibujar()
    def persistir(self):self.guardar('valorant',copy.deepcopy(self.config))
    def cambiar_auto(self):self.config['auto_pick']=self.automatico.get();self.persistir()
    def dibujar(self):
        for i in range(len(self.slots)):self.dibujar_slot(i)
    def dibujar_slot(self,i):
        cv=self.slots[i];ancho=cv.winfo_width()
        if ancho<=1:return
        id=self.config['preferencias'][i];agente=self.catalogo.agentes.get(id)
        prioridad=ui('Prioridad '+str(i+1));nombre=agente['name'] if agente else ui('Elegir agente')
        rol=ui(agente['role']) if agente else '';marca=(ancho,id,i==self.activa,prioridad,nombre,rol)
        if self._slots_pintados.get(i)==marca:return
        cv.delete('all')
        cv.create_polygon(1,1,ancho-12,1,ancho-1,12,ancho-1,99,12,99,1,88,fill=TARJETA,outline=CIAN if i==self.activa else '#55313e',width=2)
        if agente:cv.create_image(42,50,image=self.catalogo.foto(id))
        else:cv.create_text(42,48,text='+',font=(FAMILIA,26),fill=CIAN)
        cv.create_text(84,22,text=prioridad,anchor='w',fill=SUAVE,font=(FAMILIA,9))
        cv.create_text(84,46,text=nombre,anchor='w',fill=TEXTO,font=(FAMILIA,13,'bold'))
        if agente:cv.create_text(84,70,text=rol,anchor='w',fill=SUAVE,font=(FAMILIA,9))
        self._slots_pintados[i]=marca
    def filtrar(self):
        for hijo in self.grid.winfo_children():hijo.destroy()
        self.botones={}
        encontrados=[a for a in self.catalogo.agentes.values() if clave(self.busqueda.get()) in clave(a['name'])]
        for i in range(8):self.grid.columnconfigure(i,weight=1,uniform='agentes')
        for i,a in enumerate(encontrados):
            b=tk.Button(self.grid,text=a['name'],image=self.catalogo.foto(a['id'],56),compound='top',bg=TARJETA,fg=TEXTO,
                        activebackground='#421327',activeforeground=TEXTO,relief='flat',bd=0,cursor='hand2',font=(FAMILIA,9),command=lambda id=a['id']:self.elegir(id))
            b.grid(row=i//8,column=i%8,sticky='nsew',padx=3,pady=3,ipady=4);self.botones[a['id']]=b
        if not encontrados:tk.Label(self.grid,text=ui('Sin resultados'),bg=FONDO,fg=SUAVE).grid(row=0,column=0,columnspan=8,pady=20)
    @staticmethod
    def _consultar(control,stop,eventos):
        # El trabajador no conserva widgets, variables Tcl ni retratos.
        while not stop.is_set():
            try:control.consultar();error=None
            except ErrorValorant as e:error=MENSAJES.get(e.clave,MENSAJES['conexion'])
            except (ValueError,TypeError,KeyError,AttributeError):error=MENSAJES['conexion']
            eventos.put(error);stop.wait(3)
    def refrescar(self):
        if self.cerrado:return
        while not self._eventos.empty():self._consulta_error=self._eventos.get_nowait()
        self.cola.set(ui(self._consulta_error or self.control.cola_estado));self.estado.set(ui(self.control.estado))
        self._after=self.ventana.after(300,self.refrescar)
    def cerrar(self):
        self.cerrado=True;self._stop.set()
        if getattr(self,'_after',None):self.ventana.after_cancel(self._after)
        self.ventana.destroy()
