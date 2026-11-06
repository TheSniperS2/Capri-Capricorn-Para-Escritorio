"""Panel de LoL: perfiles por línea y controles de sala, sin red en el hilo Tk."""
import copy
import queue
import threading
import unicodedata
from PIL import Image,ImageTk
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,InterruptorCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui
from league import ClienteLCU,ErrorCliente,FASE
from lol_seleccion import ROLES,NOMBRES,normalizar,cargar_catalogo,carpeta_catalogo

CIAN='#76dce4'
TEXTOS=('Tu próxima partida','Tu línea. Tus campeones.','PICKS','BANEOS','Prioridad 1','Prioridad 2','Prioridad 3',
        'Elegir campeón','Cambiar campeón','Sin configurar','Buscar campeón…','Sin resultados','Quitar campeón',
        'Confirmar picks automáticamente','Confirmar baneos automáticamente','Configurar League of Legends',
        'Perfiles por línea','Se usa la línea que te asigne LoL. Si una opción no está disponible, pasa a la siguiente.',
        'Tus cambios se guardan al instante','Cancelar detiene la búsqueda. Capri no vuelve a iniciarla.',
        'Abre LoL para conectar','Conectando con LoL…','Sala preparada','Buscando partida','Partida encontrada',
        'Selección de campeón','En partida','Cliente conectado','Este catálogo se incluye con Capri; no necesita descargas al abrir el panel.',
        'Capri no está avalado por Riot Games. League of Legends y Riot Games son marcas de Riot Games, Inc.')
FASES={'Lobby':'Sala preparada','Matchmaking':'Buscando partida','ReadyCheck':'Partida encontrada',
       'ChampSelect':'Selección de campeón','InProgress':'En partida','GameStart':'En partida','Reconnect':'En partida'}


def clave(texto):
    return ''.join(c for c in unicodedata.normalize('NFD',texto.casefold()) if unicodedata.category(c)!='Mn')


class Catalogo:
    def __init__(self,master):
        datos=cargar_catalogo();self.version=datos['version'];self.campeones={c['id']:c for c in datos['champions']}
        self.master=master;self.fotos={};self.sprites={}

    def foto(self,identificador,tamano=48):
        llave=(identificador,tamano)
        if llave not in self.fotos and identificador in self.campeones:
            d=self.campeones[identificador]['image'];nombre=d['sprite']
            if nombre not in self.sprites:
                with Image.open(carpeta_catalogo()/nombre) as im:self.sprites[nombre]=im.convert('RGB')
            im=self.sprites[nombre].crop((d['x'],d['y'],d['x']+d['w'],d['y']+d['h']))
            self.fotos[llave]=ImageTk.PhotoImage(im.resize((tamano,tamano),Image.Resampling.LANCZOS),master=self.master)
        return self.fotos.get(llave)


class PanelLoL:
    def __init__(self,padre,config,guardar,enviar,control,seleccion,auto_aceptar=False,consultar=True):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.control=control;self.seleccion=seleccion
        self.rol=ROLES[0];self.cerrado=False;self.selector=None;self._stop=threading.Event();self._eventos=queue.Queue()
        self.ventana=w=tk.Toplevel(padre);w.withdraw();w.title('Capri · League of Legends')
        ancho=min(980,w.winfo_screenwidth()-64);alto=min(890,w.winfo_screenheight()-80)
        w.geometry(f'{ancho}x{alto}');w.minsize(850,670)
        marco=VentanaCyber(w,'LEAGUE OF LEGENDS',self.cerrar);w.attributes('-topmost',False)
        w.protocol('WM_DELETE_WINDOW',self.cerrar)
        # Conserva accesibles los controles en portátiles y con escalado de Windows.
        contenedor=tk.Frame(marco.cuerpo,bg=FONDO);contenedor.pack(fill='both',expand=True)
        self.scroll=LienzoUI(contenedor,bg=FONDO,highlightthickness=0);self.scroll.pack(side='left',fill='both',expand=True)
        barra=tk.Scrollbar(contenedor,command=self.scroll.yview);barra.pack(side='right',fill='y')
        self.scroll.configure(yscrollcommand=barra.set)
        f=tk.Frame(self.scroll,bg=FONDO);item=self.scroll.create_window(0,0,window=f,anchor='nw')
        def ajustar(e=None):
            ancho=self.scroll.winfo_width();alto=max(740,self.scroll.winfo_height(),f.winfo_reqheight())
            self.scroll.itemconfigure(item,width=ancho,height=alto)
            self.scroll.configure(scrollregion=(0,0,ancho,alto))
        self.scroll.bind('<Configure>',ajustar)
        f.bind('<Configure>',ajustar)
        w.bind('<MouseWheel>',lambda e:self.scroll.yview_scroll(-int(e.delta/120),'units'))
        self.catalogo=Catalogo(w)
        cab=tk.Frame(f,bg=FONDO);cab.pack(fill='x',padx=20,pady=(12,12))
        tk.Label(cab,text=ui('Tu próxima partida'),bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold')).pack(anchor='w')
        tk.Label(cab,text=ui('Tu línea. Tus campeones.'),bg=FONDO,fg=TEXTO,font=(FAMILIA,25,'bold')).pack(side='left')
        self.conexion=tk.StringVar(value=ui('Conectando con LoL…') if consultar else ui('Abre LoL para conectar'))
        tk.Label(cab,textvariable=self.conexion,bg=FONDO,fg=CIAN,font=(FAMILIA,10)).pack(side='right',padx=8)
        cola=tk.Frame(f,bg=TARJETA);cola.pack(fill='x',padx=20)
        acciones=tk.Frame(cola,bg=TARJETA);acciones.pack(fill='x',padx=12,pady=(12,4))
        self.acciones={}
        for texto,orden in (('Buscar partida','busca partida en lol'),('Buscar y aceptar','busca partida en lol y acepta por mi'),
                            ('Aceptar partida','acepta partida en lol'),('Cancelar búsqueda','cancela la cola en lol')):
            b=BotonCyber(acciones,text=texto,command=lambda o=orden:self.enviar(o),padx=8,font=(FAMILIA,9,'bold'))
            b.pack(side='left',expand=True,fill='x',padx=3);self.acciones[texto]=b
        self.aceptar=tk.BooleanVar(value=auto_aceptar)
        self.aceptar_widget=InterruptorCyber(cola,text='Aceptar partidas automáticamente, también desde LoL',variable=self.aceptar,
            command=lambda:self.guardar('lol_aceptar_automatico',self.aceptar.get()))
        self.aceptar_widget.pack(fill='x',padx=12)
        tk.Label(cola,text=ui('Cancelar detiene la búsqueda. Capri no vuelve a iniciarla.'),bg=TARJETA,fg=SUAVE,
                 font=(FAMILIA,9)).pack(anchor='w',padx=14,pady=(0,10))
        self.cola_estado=tk.StringVar()
        tk.Label(f,textvariable=self.cola_estado,bg=FONDO,fg=SUAVE,font=(FAMILIA,9)).pack(anchor='w',padx=24,pady=(7,2))
        centro=tk.Frame(f,bg=FONDO);centro.pack(fill='both',expand=True,padx=20,pady=(10,5))
        lateral=tk.Frame(centro,bg=FONDO,width=144);lateral.pack(side='left',fill='y',padx=(0,18));lateral.pack_propagate(False)
        tk.Label(lateral,text=ui('Perfiles por línea'),bg=FONDO,fg=SUAVE,font=(FAMILIA,10,'bold')).pack(anchor='w',pady=(0,12))
        self.roles={}
        for numero,(rol,nombre) in enumerate(zip(ROLES,NOMBRES),1):
            b=tk.Button(lateral,text=f'0{numero}   {ui(nombre)}',command=lambda r=rol:self.elegir_rol(r),anchor='w',
                        bg=TARJETA,fg=TEXTO,activebackground='#421327',activeforeground=TEXTO,relief='flat',bd=0,
                        padx=14,pady=12,font=(FAMILIA,11,'bold'),cursor='hand2')
            b.pack(fill='x',pady=4);self.roles[rol]=b
        zona=tk.Frame(centro,bg=FONDO);zona.pack(side='left',fill='both',expand=True)
        self.titulo=tk.StringVar()
        tk.Label(zona,textvariable=self.titulo,bg=FONDO,fg=TEXTO,font=(FAMILIA,17,'bold')).pack(anchor='w')
        tk.Label(zona,text=ui('Se usa la línea que te asigne LoL. Si una opción no está disponible, pasa a la siguiente.'),
                 bg=FONDO,fg=SUAVE,wraplength=650,justify='left',font=(FAMILIA,9)).pack(anchor='w',pady=(4,10))
        columnas=tk.Frame(zona,bg=FONDO);columnas.pack(fill='both',expand=True)
        self.slots={};self.automaticos={}
        for columna,tipo,color in ((0,'pick',CIAN),(1,'ban',ACENTO)):
            panel=tk.Frame(columnas,bg=FONDO);panel.grid(row=0,column=columna,sticky='nsew',padx=(0,12) if columna==0 else 0)
            columnas.columnconfigure(columna,weight=1,uniform='draft')
            tk.Label(panel,text=ui('PICKS' if tipo=='pick' else 'BANEOS'),bg=FONDO,fg=color,font=(FAMILIA,11,'bold')).pack(anchor='w',pady=(0,8))
            for indice in range(3):
                cv=LienzoUI(panel,height=70,bg=FONDO,highlightthickness=0,takefocus=True,cursor='hand2')
                cv.pack(fill='x',pady=(0,7));self.slots[tipo,indice]=cv
                cv.bind('<Configure>',lambda e:self.dibujar())
                cv.bind('<Button-1>',lambda e,t=tipo,i=indice:self.abrir_selector(t,i))
                cv.bind('<Return>',lambda e,t=tipo,i=indice:self.abrir_selector(t,i))
                cv.bind('<space>',lambda e,t=tipo,i=indice:self.abrir_selector(t,i))
            v=tk.BooleanVar(value=self.config['auto_'+tipo]);self.automaticos[tipo]=v
            InterruptorCyber(panel,text='Confirmar picks automáticamente' if tipo=='pick' else 'Confirmar baneos automáticamente',
                variable=v,command=lambda t=tipo:self.cambiar_auto(t)).pack(fill='x')
        columnas.rowconfigure(0,weight=1)
        self.estado=tk.StringVar()
        tk.Label(f,textvariable=self.estado,bg=FONDO,fg=CIAN,font=(FAMILIA,10,'bold')).pack(anchor='w',padx=22,pady=(5,5))
        pie=tk.Frame(f,bg=FONDO);pie.pack(fill='x',padx=22,pady=(0,5))
        tk.Label(pie,text=ui('Tus cambios se guardan al instante'),bg=FONDO,fg=SUAVE,font=(FAMILIA,9)).pack(side='left')
        tk.Label(pie,text='DATA DRAGON / '+self.catalogo.version,bg=FONDO,fg=SUAVE,font=(FAMILIA,8)).pack(side='right')
        tk.Label(f,text=ui('Capri no está avalado por Riot Games. League of Legends y Riot Games son marcas de Riot Games, Inc.'),
                 bg=FONDO,fg=SUAVE,font=(FAMILIA,8),wraplength=900).pack(pady=(0,2))
        self.elegir_rol(self.rol);self.refrescar();w.update_idletasks();ajustar();w.deiconify()
        if consultar:threading.Thread(target=self._consultar,daemon=True).start()

    def elegir_rol(self,rol):
        self.rol=rol;self.titulo.set(ui(NOMBRES[ROLES.index(rol)]))
        for r,b in self.roles.items():b.configure(bg='#421327' if r==rol else TARJETA,fg=CIAN if r==rol else SUAVE)
        self.dibujar()

    def dibujar(self):
        for (tipo,i),cv in self.slots.items():
            cv.delete('all');w=max(240,cv.winfo_width());color=CIAN if tipo=='pick' else ACENTO
            identificador=self.config['roles'][self.rol][tipo][i];campeon=self.catalogo.campeones.get(identificador)
            cv.create_polygon(1,1,w-10,1,w-1,10,w-1,69,10,69,1,60,fill=TARJETA,outline='#55313e')
            cv.create_line(1,12,1,57,fill=color,width=3)
            if campeon:cv.create_image(34,35,image=self.catalogo.foto(identificador))
            else:
                cv.create_rectangle(12,13,57,57,outline='#55313e')
                cv.create_text(34,34,text='+',fill=color,font=(FAMILIA,22))
            cv.create_text(70,19,text=ui('Prioridad '+str(i+1)),anchor='w',fill=SUAVE,font=(FAMILIA,8))
            cv.create_text(70,40,text=campeon['name'] if campeon else ui('Elegir campeón'),anchor='w',fill=TEXTO,font=(FAMILIA,12,'bold'))

    def cambiar_auto(self,tipo):
        self.config['auto_'+tipo]=self.automaticos[tipo].get();self.persistir()

    def persistir(self):self.guardar('lol_seleccion',copy.deepcopy(self.config))

    def elegir(self,tipo,indice,identificador,rol=None):
        rol=rol or self.rol;lista=self.config['roles'][rol][tipo]
        if identificador:
            for i,v in enumerate(lista):
                if i!=indice and v==identificador:lista[i]=0
        lista[indice]=identificador;self.persistir();self.dibujar()

    def abrir_selector(self,tipo,indice):
        if self.selector and self.selector.winfo_exists():self.selector.destroy()
        rol=self.rol;w=self.selector=tk.Toplevel(self.ventana);w.title(ui('Elegir campeón'));w.geometry('710x580');w.minsize(600,420)
        w.configure(bg=FONDO);w.transient(self.ventana)
        self.busqueda=tk.StringVar()
        arriba=tk.Frame(w,bg=FONDO);arriba.pack(fill='x',padx=18,pady=14)
        tk.Label(arriba,text=ui('Elegir campeón'),bg=FONDO,fg=TEXTO,font=(FAMILIA,17,'bold')).pack(side='left')
        def elegir(identificador):self.elegir(tipo,indice,identificador,rol);w.destroy()
        BotonCyber(arriba,text='Quitar campeón',command=lambda:elegir(0),padx=8).pack(side='right')
        entrada=tk.Entry(w,textvariable=self.busqueda,bg=TARJETA,fg=TEXTO,insertbackground=CIAN,relief='flat',font=(FAMILIA,12))
        entrada.pack(fill='x',padx=18,ipady=9);entrada.focus_set()
        tk.Label(w,text=ui('Buscar campeón…'),bg=FONDO,fg=SUAVE,font=(FAMILIA,9)).pack(anchor='w',padx=18,pady=(4,8))
        contenedor=tk.Frame(w,bg=FONDO);contenedor.pack(fill='both',expand=True,padx=18,pady=(0,12))
        canvas=LienzoUI(contenedor,bg=FONDO,highlightthickness=0);canvas.pack(side='left',fill='both',expand=True)
        barra=tk.Scrollbar(contenedor,orient='vertical',command=canvas.yview);barra.pack(side='right',fill='y');canvas.configure(yscrollcommand=barra.set)
        grid=tk.Frame(canvas,bg=FONDO);item=canvas.create_window(0,0,window=grid,anchor='nw')
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(item,width=e.width))
        grid.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        w.bind('<MouseWheel>',lambda e:canvas.yview_scroll(-int(e.delta/120),'units'))
        w.bind('<Escape>',lambda e:w.destroy())
        def filtrar(*_):
            for hijo in grid.winfo_children():hijo.destroy()
            encontrados=sorted((c for c in self.catalogo.campeones.values() if clave(self.busqueda.get()) in clave(c['name'])),key=lambda c:clave(c['name']))
            for columna in range(7):grid.columnconfigure(columna,weight=1,uniform='campeones')
            for n,c in enumerate(encontrados):
                b=tk.Button(grid,text=c['name'],image=self.catalogo.foto(c['id']),compound='top',bg=TARJETA,fg=TEXTO,activebackground='#421327',
                    activeforeground=TEXTO,relief='flat',bd=0,font=(FAMILIA,8),cursor='hand2',command=lambda id=c['id']:elegir(id))
                b.grid(row=n//7,column=n%7,sticky='nsew',padx=3,pady=3,ipady=5)
            if not encontrados:tk.Label(grid,text=ui('Sin resultados'),bg=FONDO,fg=SUAVE).grid(row=0,column=0,columnspan=7,pady=30)
            canvas.yview_moveto(0)
        self.busqueda.trace_add('write',filtrar);filtrar()

    def _consultar(self):
        cliente=ClienteLCU()
        while not self._stop.is_set():
            try:estado=FASES.get(cliente.pedir('GET',FASE),'Cliente conectado')
            except ErrorCliente:estado='Abre LoL para conectar'
            self._eventos.put(estado)
            self._stop.wait(3)

    def refrescar(self):
        if self.cerrado:return
        while not self._eventos.empty():self.conexion.set(ui(self._eventos.get_nowait()))
        self.cola_estado.set(ui(self.control.estado));self.estado.set(ui(self.seleccion.estado))
        if hasattr(self.control,'permanente') and self.aceptar.get()!=self.control.permanente:
            self.aceptar.set(self.control.permanente);self.aceptar_widget.dibujar()
        self._after=self.ventana.after(300,self.refrescar)

    def cerrar(self):
        self.cerrado=True;self._stop.set()
        if getattr(self,'_after',None):self.ventana.after_cancel(self._after)
        self.ventana.destroy()
