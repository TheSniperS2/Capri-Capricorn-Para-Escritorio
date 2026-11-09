"""Vinculación local de playlists en una sola ventana de Capri."""
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO,VERDE
from fuentes import FAMILIA
from idiomas import ui
from playlists import uri_playlist,vincular

TEXTOS=('Vincular playlist','Guarda su nombre y pídesela a Capri cuando quieras.',
        'Nombre para pedirla','Por ejemplo: Capricorn','Enlace de la playlist',
        'Pega su enlace de Spotify. Puede seguir siendo privada.','Pegar enlace','Cancelar',
        'Escribe un nombre para pedir esta playlist.',
        'Pega un enlace de playlist de Spotify válido.',
        'No pude guardar la playlist. Inténtalo de nuevo.',
        'El portapapeles no contiene texto.','Playlist vinculada','Pídela por su nombre.',
        'PUEDES DECIR','Capri, pon mi playlist «{0}».','Vincular otra','Listo')


class DialogoPlaylist:
    def __init__(self,padre,carpeta):
        self.carpeta=carpeta;self.cerrado=False;self.guardado=False
        v=self.ventana=tk.Toplevel(padre);v.withdraw();v.title(ui('Vincular playlist'))
        v.transient(padre);v.minsize(540,550)
        from ventanas import area_trabajo
        l,t,r,b=area_trabajo();w=min(640,r-l-64);h=min(600,b-t-64)
        v.geometry(f'{w}x{h}+{max(l+32,l+(r-l-w)//2)}+{max(t+32,t+(b-t-h)//2)}')
        self.marco=VentanaCyber(v,'SPOTIFY',cerrar=self.cerrar)
        cuerpo=self.cuerpo=tk.Frame(self.marco.cuerpo,bg=FONDO,padx=18,pady=10)
        cuerpo.pack(fill='both',expand=True)
        cabecera=tk.Frame(cuerpo,bg=FONDO);cabecera.pack(fill='x',pady=(0,12))
        icono=LienzoUI(cabecera,width=54,height=54,bg=FONDO,highlightthickness=0)
        icono.pack(side='left',padx=(0,12))
        icono.create_polygon(1,1,42,1,53,12,53,53,1,53,fill=TARJETA,outline=ACENTO)
        icono.create_line(24,36,24,16,39,12,39,32,fill=VERDE,width=3)
        icono.create_line(24,21,39,17,fill=VERDE,width=3)
        for x,y in ((20,37),(35,33)):icono.create_oval(x-5,y-3,x+4,y+3,fill=VERDE,outline='')
        textos=tk.Frame(cabecera,bg=FONDO);textos.pack(side='left',fill='both',expand=True)
        self.titulo=tk.Label(textos,text=ui('Vincular playlist'),bg=FONDO,fg=TEXTO,font=(FAMILIA,20,'bold'),anchor='w')
        self.titulo.pack(fill='x')
        self.subtitulo=tk.Label(textos,text=ui(TEXTOS[1]),bg=FONDO,fg=SUAVE,font=(FAMILIA,10),anchor='w',justify='left')
        self.subtitulo.pack(fill='x',pady=(4,0))
        self.pie=tk.Frame(cuerpo,bg=FONDO);self.pie.pack(side='bottom',fill='x',pady=(12,0))
        tk.Frame(self.pie,bg='#542333',height=1).pack(fill='x',pady=(0,12))
        self.cancelar=BotonCyber(self.pie,text='Cancelar',command=self.cerrar,estilo='secundario',bg=TARJETA)
        self.cancelar.pack(side='left')
        self.boton_guardar=BotonCyber(self.pie,text='Vincular playlist',command=self.guardar,estilo='principal',bg=ACENTO,fg=FONDO)
        self.boton_guardar.pack(side='right')
        self.formulario=tk.Frame(cuerpo,bg=FONDO);self.formulario.pack(fill='x')
        self.nombre=tk.StringVar();self.enlace=tk.StringVar();self.estado=tk.StringVar()
        self.bordes={}
        self.entrada_nombre=self.campo('nombre',self.nombre,'Nombre para pedirla','Por ejemplo: Capricorn')
        self.entrada_enlace=self.campo('enlace',self.enlace,'Enlace de la playlist',TEXTOS[5],pegar=True)
        self.error=tk.Label(self.formulario,textvariable=self.estado,bg=FONDO,fg=ACENTO,font=(FAMILIA,10),
                            anchor='w',justify='left',height=2)
        self.error.pack(fill='x')
        self.confirmacion=tk.Frame(cuerpo,bg=TARJETA,padx=20,pady=24,highlightbackground=ACENTO,highlightthickness=1)
        tk.Label(self.confirmacion,text=ui('PUEDES DECIR'),bg=TARJETA,fg=VERDE,font=(FAMILIA,10,'bold')).pack(anchor='w')
        self.frase=tk.StringVar()
        self.ejemplo=tk.Label(self.confirmacion,textvariable=self.frase,bg=TARJETA,fg=TEXTO,font=(FAMILIA,16,'bold'),justify='left',anchor='w')
        self.ejemplo.pack(fill='x',pady=(12,8))
        cuerpo.bind('<Configure>',self.adaptar)
        textos.bind('<Configure>',lambda e:self.subtitulo.configure(wraplength=max(120,e.width)))
        v.bind('<Destroy>',self.destruir,add='+')
        v.protocol('WM_DELETE_WINDOW',self.cerrar)
        from idiomas import localizar_widgets
        localizar_widgets(v,True)
        v.deiconify();v.lift();v.grab_set()
        v._root().after_idle(lambda:self.entrada_nombre.focus_set() if not self.cerrado else None)

    def campo(self,clave,variable,titulo,ayuda,pegar=False):
        f=self.formulario
        tk.Label(f,text=ui(titulo),bg=FONDO,fg=TEXTO,font=(FAMILIA,11,'bold')).pack(anchor='w',pady=(0,7))
        borde=self.bordes[clave]=tk.Frame(f,bg=TARJETA,highlightbackground='#69404c',highlightcolor=ACENTO,highlightthickness=1,padx=12,pady=9)
        borde.pack(fill='x')
        entrada=tk.Entry(borde,textvariable=variable,bg=TARJETA,fg=TEXTO,insertbackground=VERDE,selectbackground='#5e1a30',
                         selectforeground=TEXTO,relief='flat',bd=0,highlightthickness=0,font=(FAMILIA,12))
        entrada.pack(side='left',fill='x',expand=True,ipady=3)
        entrada.bind('<FocusIn>',lambda e:borde.configure(highlightbackground=ACENTO))
        entrada.bind('<FocusOut>',lambda e:borde.configure(highlightbackground='#69404c'))
        entrada.bind('<Return>',lambda e:(self.guardar(),'break')[1])
        entrada.bind('<KeyRelease>',lambda e:self.estado.set('') if self.estado.get() else None)
        if pegar:BotonCyber(borde,text='Pegar enlace',command=self.pegar,estilo='secundario',bg=TARJETA,padx=9,pady=5).pack(side='right',padx=(12,0))
        etiqueta=tk.Label(f,text=ui(ayuda),bg=FONDO,fg=SUAVE,font=(FAMILIA,9),anchor='w',justify='left')
        etiqueta.pack(fill='x',pady=(4,10))
        etiqueta.bind('<Configure>',lambda e:etiqueta.configure(wraplength=max(180,e.width)))
        return entrada

    def adaptar(self,e):
        ancho=max(180,e.width-40)
        for etiqueta in (self.error,self.ejemplo):etiqueta.configure(wraplength=ancho)

    def pegar(self):
        try:self.enlace.set(self.ventana.clipboard_get().strip());self.estado.set('');self.entrada_enlace.focus_set()
        except tk.TclError:self.estado.set(ui('El portapapeles no contiene texto.'))

    def guardar(self):
        nombre=self.nombre.get().strip();enlace=self.enlace.get().strip()
        if not nombre:
            self.estado.set(ui('Escribe un nombre para pedir esta playlist.'));self.entrada_nombre.focus_set();return
        try:uri=uri_playlist(enlace)
        except ValueError:
            self.estado.set(ui('Pega un enlace de playlist de Spotify válido.'));self.entrada_enlace.focus_set();return
        try:vincular(nombre,uri,self.carpeta)
        except OSError:self.estado.set(ui('No pude guardar la playlist. Inténtalo de nuevo.'));return
        self.guardado=True;self.estado.set('')
        self.titulo.configure(text=ui('Playlist vinculada'));self.subtitulo.configure(text=ui('Pídela por su nombre.'))
        self.formulario.pack_forget();self.confirmacion.pack(fill='x',pady=(20,0))
        self.frase.set(ui('Capri, pon mi playlist «{0}».').format(nombre))
        self.cancelar.configure(text='Vincular otra',command=self.reiniciar)
        self.boton_guardar.configure(text='Listo',command=self.cerrar);self.boton_guardar.focus_set()

    def reiniciar(self):
        self.guardado=False;self.nombre.set('');self.enlace.set('');self.estado.set('')
        self.titulo.configure(text=ui('Vincular playlist'));self.subtitulo.configure(text=ui(TEXTOS[1]))
        self.confirmacion.pack_forget();self.formulario.pack(fill='x')
        self.cancelar.configure(text='Cancelar',command=self.cerrar)
        self.boton_guardar.configure(text='Vincular playlist',command=self.guardar);self.entrada_nombre.focus_set()

    def cerrar(self):
        if self.cerrado:return
        self.cerrado=True
        if self.ventana.grab_current() is self.ventana:self.ventana.grab_release()
        self.ventana.destroy()

    def destruir(self,e):
        if e.widget is self.ventana:self.cerrado=True
