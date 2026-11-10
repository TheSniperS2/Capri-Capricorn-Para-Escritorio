"""Nombres fáciles y biblioteca persistente de playlists de Spotify."""
from pathlib import Path
from types import SimpleNamespace
import os
import queue
import threading
from datetime import datetime
from PIL import Image,ImageTk,ImageDraw
from tema_ui import tk,LienzoUI,color,observar
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO,VERDE
from desplazamiento_ui import Desplazable
from fuentes import FAMILIA
from idiomas import ui,idioma_actual
from playlists import uri_playlist,vincular,listar_vinculadas,clave,quitar_vinculo,actualizar_titulo
from playlists_metadata import consultar as consultar_playlist,archivo_portada,enlace_web,guardar_portada

EXPLICACION='¿Capri no entiende el nombre de tu playlist? Guárdala con un nombre fácil y pídela así.'
TEXTOS=('Playlists de Spotify',EXPLICACION,'Nombre fácil para Capri','Ej.: Para jugar',
        'Enlace de Spotify','Pegar enlace','ASÍ SE LA PIDES','Guardar playlist','Guardar cambios',
        'Nueva','GUARDADAS','Se conservan aunque cierres Capri.','Buscar guardadas…',
        'Todavía no guardaste ninguna.','Añade un nombre y su enlace a la izquierda.',
        'No hay coincidencias.','Playlist de Spotify','GUARDADA','Editar','Copiar enlace',
        'Spotify ↗','Quitar vínculo','¿Quitar este nombre de Capri?','Quitar','Cancelar','Cerrar',
        'Guardada como «{0}».','Editando «{0}».','Enlace copiado.','Vínculo quitado.',
        'Ese nombre ya está guardado. Elige otro o edita la playlist.',
        'Escribe un nombre para pedir esta playlist.','Usa un nombre de hasta 200 caracteres.',
        'Pega un enlace de playlist de Spotify válido.','No pude guardar la playlist. Inténtalo de nuevo.',
        'No pude leer tus playlists guardadas. No se han reemplazado.',
        'No pude quitar el vínculo. Inténtalo de nuevo.','El portapapeles no contiene texto.',
        'Capri, pon mi playlist «{0}».','Guardada el {0}','Pídela como',
        'Tu primera playlist','Guárdala con un nombre fácil para pedírsela a Capri.',
        'Añadir playlist','Prueba con otro nombre.','Limpiar búsqueda',
        'Si la playlist es privada, Spotify no comparte su portada. Pulsa «Portada» → «Capturar» para tomar un pantallazo y seleccionar la imagen.')


class CampoPlaylist(LienzoUI):
    """Entrada nativa, sin etiquetas superpuestas que intercepten clics."""
    def __init__(self,padre,variable,tipo,pegar):
        super().__init__(padre,height=40 if tipo=='buscar' else 48,bg=FONDO,highlightthickness=0,cursor='xterm')
        self.tipo=tipo;self.activo=False
        self.entrada=tk.Entry(self,textvariable=variable,width=1,bg='#17121e',fg=TEXTO,insertbackground=ACENTO,
            selectbackground='#5e1a30',selectforeground=TEXTO,bd=0,relief='flat',highlightthickness=0,
            exportselection=False,font=(FAMILIA,14 if tipo=='nombre' else 10 if tipo=='buscar' else 11))
        self.item=self.create_window(44,28,window=self.entrada,anchor='w')
        self.bind('<Configure>',self.dibujar)
        self.bind('<Button-1>',lambda e:self.enfocar(True))
        self.entrada.bind('<Button-1>',lambda e:self.enfocar())
        self.entrada.bind('<FocusIn>',lambda e:self.enfocado(True))
        self.entrada.bind('<FocusOut>',lambda e:self.enfocado(False))
        for evento in ('<Control-v>','<Control-V>','<Shift-Insert>','<<Paste>>'):
            self.entrada.bind(evento,lambda e:pegar(self.entrada))

    def enfocar(self,al_final=False):
        self.entrada.focus_force()
        if al_final:self.entrada.icursor('end')

    def enfocado(self,valor):self.activo=valor;self.dibujar()

    def dibujar(self,e=None):
        self.delete('campo');w=max(70,self.winfo_width());h=self.winfo_height()
        borde=ACENTO if self.activo else '#51405f'
        self.create_polygon(1,1,w-9,1,w-1,9,w-1,h-1,9,h-1,1,h-9,
            fill='#17121e',outline=borde,width=1.5,tags='campo')
        self.create_line(13,h-3,47 if self.activo else 28,h-3,fill=ACENTO,width=2,tags='campo')
        if self.tipo=='nombre':self.create_text(22,h/2,text='Aa',fill=ACENTO,font=(FAMILIA,10,'bold'),tags='campo')
        elif self.tipo=='buscar':
            self.create_oval(14,h/2-8,26,h/2+4,outline=ACENTO,width=1.5,tags='campo')
            self.create_line(25,h/2+3,32,h/2+10,fill=ACENTO,width=1.5,tags='campo')
        else:
            self.create_oval(13,h/2-6,26,h/2+3,outline=ACENTO,width=1.5,tags='campo')
            self.create_oval(20,h/2-2,33,h/2+7,outline=ACENTO,width=1.5,tags='campo')
        self.coords(self.item,44,h/2);self.itemconfigure(self.item,width=max(20,w-62),height=max(20,h-8))
        self.tag_lower('campo')


class EstadoBiblioteca(LienzoUI):
    """Mensaje alineado dentro del espacio de listas, sin una tarjeta adicional."""
    def __init__(self,padre,filtrado,accion):
        super().__init__(padre,bg=FONDO,highlightthickness=0)
        self._ancho_texto=None
        self.filtrado=filtrado
        self.contenido=f=tk.Frame(self,bg=FONDO)
        self.item=self.create_window(0,0,window=f,anchor='n')
        icono=self.icono=LienzoUI(f,width=68,height=68,bg=FONDO,highlightthickness=0)
        icono.pack()
        self.dibujar_icono();observar(self.dibujar_icono)
        familia='Yu Gothic UI' if idioma_actual()=='ja' else FAMILIA
        self.titulo=tk.Label(f,text=ui('No hay coincidencias.' if filtrado else 'Todavía no guardaste ninguna.'),
            bg=FONDO,fg=TEXTO,font=(familia,12,'bold'),justify='center',anchor='center')
        self.titulo.pack(fill='x',pady=(8,4))
        self.ayuda=tk.Label(f,text=ui('Prueba con otro nombre.' if filtrado else 'Añade un nombre y su enlace a la izquierda.'),
            bg=FONDO,fg=SUAVE,font=(familia,9),justify='center',anchor='center')
        self.ayuda.pack(fill='x')
        self.boton=None
        if filtrado:
            self.boton=BotonCyber(f,text='Limpiar búsqueda',command=accion,
                estilo='secundario',bg=FONDO,font=(familia,9),padx=16,pady=5)
            self.boton.pack(pady=(12,0))
        self.bind('<Configure>',self.dibujar);f.bind('<Configure>',self.dibujar)

    def dibujar_icono(self):
        if not self.winfo_exists():return
        imagen=Image.new('RGBA',(272,272));d=ImageDraw.Draw(imagen)
        def caja(*p):return tuple(round(n*4) for n in p)
        if self.filtrado:
            d.ellipse(caja(15,12,44,41),outline=color(ACENTO),width=7)
            d.line(caja(40,38,53,51),fill=color(ACENTO),width=8)
        else:
            d.ellipse(caja(10,10,58,58),fill=color(TARJETA),outline=color(ACENTO),width=6)
            d.ellipse(caja(17,17,51,51),outline=color('#51405f'),width=4)
            for inicio in (38,218):d.arc(caja(13,13,55,55),inicio,inicio+44,fill=color(VERDE),width=7)
            d.ellipse(caja(27,27,41,41),fill=color(ACENTO))
            d.ellipse(caja(32,32,36,36),fill=color(FONDO))
        self.foto_icono=ImageTk.PhotoImage(imagen.resize((68,68),Image.Resampling.LANCZOS),master=self)
        self.icono.delete('all');self.icono.create_image(34,34,image=self.foto_icono)

    def dibujar(self,e=None):
        w,h=self.winfo_width(),self.winfo_height();ancho=max(120,min(440,w-20));texto=max(80,ancho-44)
        if texto!=self._ancho_texto:
            self._ancho_texto=texto
            for label in (self.titulo,self.ayuda):label.configure(wraplength=texto)
            self.itemconfigure(self.item,width=texto)
        self.coords(self.item,w/2,16)


class DialogoPlaylist:
    def __init__(self,padre,carpeta):
        self.carpeta=Path(carpeta);self.cerrado=False;self.guardado=False;self.editando=None
        self.registros=[];self.tarjetas={};self.fotos={};self._pedidas=set();self.captura=None
        self._fin=threading.Event();self._solicitudes=queue.Queue();self._resultados=queue.Queue();self._hilo=None;self._poll=None
        self.nombre=tk.StringVar();self.enlace=tk.StringVar();self.estado=tk.StringVar();self.frase=tk.StringVar();self.filtro=tk.StringVar()
        v=self.ventana=tk.Toplevel(padre._root());v.withdraw();v.title(ui('Playlists de Spotify'))
        self.reloj=v._root()
        from ventanas import area_trabajo
        l,t,r,b=area_trabajo();w=min(1060,r-l-48);h=min(780,b-t-48)
        v.geometry(f'{w}x{h}+{max(l+24,l+(r-l-w)//2)}+{max(t+24,t+(b-t-h)//2)}')
        v.minsize(min(840,w),min(700,h))
        self.marco=VentanaCyber(v,'SPOTIFY',cerrar=self.cerrar)
        cuerpo=self.cuerpo=tk.Frame(self.marco.cuerpo,bg=FONDO,padx=18,pady=10);cuerpo.pack(fill='both',expand=True)
        cabecera=tk.Frame(cuerpo,bg=FONDO);cabecera.pack(fill='x',pady=(0,14))
        icono=LienzoUI(cabecera,width=60,height=66,bg=FONDO,highlightthickness=0);icono.pack(side='left',padx=(0,15))
        for x,hbarra in ((8,18),(17,30),(26,48),(35,38),(44,25)):
            icono.create_line(x,36-hbarra/2,x,36+hbarra/2,fill=ACENTO,width=4)
        icono.create_line(5,66,49,66,fill=VERDE,width=2)
        textos=tk.Frame(cabecera,bg=FONDO);textos.pack(side='left',fill='both',expand=True)
        self.kicker=self.etiqueta(textos,'SPOTIFY / PLAYLISTS',8,ACENTO,True);self.kicker.pack(anchor='w',pady=(0,4))
        self.titulo=self.etiqueta(textos,'Tu música, con tu voz.',25,TEXTO,True);self.titulo.pack(fill='x')
        self.subtitulo=self.etiqueta(textos,EXPLICACION,10,SUAVE);self.subtitulo.pack(fill='x',pady=(5,0))
        self.pie=tk.Frame(cuerpo,bg=FONDO);self.pie.pack(side='bottom',fill='x',pady=(12,0))
        tk.Frame(self.pie,bg='#542333',height=1).pack(fill='x',pady=(0,10))
        self.cancelar=BotonCyber(self.pie,text='Cerrar',command=self.cerrar,estilo='secundario',bg=TARJETA)
        self.cancelar.pack(side='right')
        columnas=tk.Frame(cuerpo,bg=FONDO);columnas.pack(fill='both',expand=True)
        columnas.columnconfigure(0,weight=4,uniform='biblioteca');columnas.columnconfigure(1,weight=6,uniform='biblioteca');columnas.rowconfigure(0,weight=1)
        izquierda=tk.Frame(columnas,bg=FONDO,padx=0,pady=0)
        izquierda.grid(row=0,column=0,sticky='new',padx=(0,25))
        self.formulario=izquierda
        fila=tk.Frame(izquierda,bg=FONDO);fila.pack(fill='x',pady=(0,12))
        self.encabezado=self.etiqueta(fila,'Nuevo vínculo',15,TEXTO,True);self.encabezado.pack(side='left',anchor='s')
        self.nueva=BotonCyber(fila,text='Nueva',command=self.reiniciar,estilo='secundario',bg=FONDO,font=(FAMILIA,8),padx=7,pady=2)
        self.nueva.pack(side='right',padx=(9,0))
        self.bordes={}
        self.etiqueta(izquierda,'Nombre para Capri',10,SUAVE,True).pack(anchor='w',pady=(0,5))
        self.entrada_nombre=self.campo('nombre',self.nombre,'')
        self.ayuda_nombre=self.etiqueta(izquierda,'Por ejemplo: Música para jugar',9,SUAVE);self.ayuda_nombre.pack(anchor='w',pady=(6,0))
        fila_enlace=tk.Frame(izquierda,bg=FONDO);fila_enlace.pack(fill='x',pady=(12,5))
        self.etiqueta(fila_enlace,'Enlace de Spotify',10,SUAVE,True).pack(side='left',anchor='s')
        self.pegar_boton=BotonCyber(fila_enlace,text='Pegar enlace',command=self.pegar,estilo='secundario',bg=FONDO,font=(FAMILIA,8),padx=7,pady=2)
        self.pegar_boton.pack(side='right',padx=(8,0))
        self.entrada_enlace=self.campo('enlace',self.enlace,'https://open.spotify.com/playlist/…')
        self.ayuda_enlace=self.etiqueta(izquierda,'Puedes pegarlo con Ctrl + V.',9,SUAVE);self.ayuda_enlace.pack(anchor='w',pady=(6,0))
        preview=self.preview=tk.Frame(izquierda,bg='#1b1620',padx=15,pady=10);preview.pack(fill='x',pady=(14,12))
        self.titulo_ejemplo=self.etiqueta(preview,'ASÍ SE LA PIDES',8,ACENTO,True);self.titulo_ejemplo.pack(anchor='w',pady=(0,6))
        self.ejemplo=self.etiqueta(preview,'',11,TEXTO,True,literal=True);self.ejemplo.configure(textvariable=self.frase);self.ejemplo.pack(fill='x')
        self.boton_guardar=BotonCyber(izquierda,text='Guardar playlist',command=self.guardar,estilo='principal',bg=ACENTO,fg=FONDO,pady=10)
        self.boton_guardar.pack(fill='x')
        self.confirmacion=tk.Frame(izquierda,bg=FONDO);self.confirmacion.pack(fill='x',pady=(8,0))
        self.error=self.etiqueta(self.confirmacion,'',9,VERDE);self.error.configure(textvariable=self.estado);self.error.pack(fill='x')
        derecha=tk.Frame(columnas,bg=FONDO);derecha.grid(row=0,column=1,sticky='nsew')
        fila=tk.Frame(derecha,bg=FONDO);fila.pack(fill='x')
        self.etiqueta(fila,'Tu biblioteca',15,TEXTO,True).pack(side='left')
        self.contador=tk.StringVar()
        self.cuenta=self.etiqueta(fila,'',10,SUAVE,True);self.cuenta.configure(textvariable=self.contador);self.cuenta.pack(side='right')
        self.etiqueta(derecha,'Se conservan aunque cierres Capri.',9,SUAVE).pack(anchor='w',pady=(5,10))
        self.filtro_panel=tk.Frame(derecha,bg=FONDO)
        self.etiqueta(self.filtro_panel,'Buscar guardadas',9,SUAVE).pack(anchor='w',pady=(0,4))
        self.campo_busqueda=CampoPlaylist(self.filtro_panel,self.filtro,'buscar',self.pegar_en)
        self.campo_busqueda.pack(fill='x');self.busqueda=self.campo_busqueda.entrada
        self.estado_biblioteca=None
        self.lista=Desplazable(derecha,bg=FONDO);self.lista.pack(fill='both',expand=True)
        self.filtro.trace_add('write',lambda *args:self.pintar_guardadas())
        self.nombre.trace_add('write',lambda *args:self.actualizar_frase())
        self.actualizar_frase();self.refrescar()
        self._compacto=None
        v.bind('<Configure>',self.adaptar,add='+')
        v.bind('<Destroy>',self.destruir,add='+');v.protocol('WM_DELETE_WINDOW',self.cerrar)
        self.marco.mostrar_completa()
        from ventanas import traer_al_frente
        traer_al_frente(v);self.entrada_nombre.focus_set()
        self._poll=self.reloj.after(80,self.procesar_resultados)

    def adaptar(self,e):
        if e.widget is not self.ventana:return
        compacto=e.height<720
        if compacto==self._compacto:return
        self._compacto=compacto
        if compacto:
            self.kicker.pack_forget();self.ayuda_nombre.pack_forget();self.ayuda_enlace.pack_forget();self.titulo_ejemplo.pack_forget()
            self.preview.pack_configure(pady=(8,8))
        else:
            self.kicker.pack(anchor='w',pady=(0,4),before=self.titulo)
            self.ayuda_nombre.pack(anchor='w',pady=(6,0),after=self.bordes['nombre'])
            self.ayuda_enlace.pack(anchor='w',pady=(6,0),after=self.bordes['enlace'])
            self.titulo_ejemplo.pack(anchor='w',pady=(0,6),before=self.ejemplo)
            self.preview.pack_configure(pady=(14,12))
        self.titulo.configure(font=('Yu Gothic UI' if idioma_actual()=='ja' else FAMILIA,18 if compacto else 25,'bold'))

    def etiqueta(self,padre,texto,tamano,tinta,negrita=False,literal=False):
        familia='Yu Gothic UI' if idioma_actual()=='ja' else FAMILIA
        l=tk.Label(padre,text=texto if literal else ui(texto),bg=padre.cget('bg'),fg=tinta,anchor='nw',justify='left',
                   font=(familia,tamano,'bold') if negrita else (familia,tamano),wraplength=270)
        l._capri_contenido_usuario=literal;anterior=[0];medida=[None,0]
        def ajustar(e):
            if e.width<=50 or e.width==anterior[0]:return
            anterior[0]=e.width;limite=e.width-2
            if not l.cget('textvariable'):
                firma=(l.cget('text'),l.cget('font'))
                if medida[0]!=firma:
                    medida[:]=[firma,max((int(l.tk.call('font','measure',firma[1],s)) for s in str(firma[0]).splitlines()),default=0)]
                if medida[1]<=min(l.winfo_pixels(l.cget('wraplength')),limite):return
            l.configure(wraplength=limite)
        l.bind('<Configure>',ajustar)
        return l

    def campo(self,clave_campo,variable,ayuda):
        campo=self.bordes[clave_campo]=CampoPlaylist(self.formulario,variable,clave_campo,self.pegar_en)
        campo.pack(fill='x');entrada=campo.entrada
        entrada.bind('<Return>',lambda e:(self.guardar(),'break')[1])
        entrada.bind('<KeyRelease>',lambda e:self.estado.set('') if self.estado.get() else None)
        return entrada

    def pegar_en(self,entrada):
        try:contenido=entrada.clipboard_get().replace('\r','').replace('\n',' ')
        except tk.TclError:self.mensaje('El portapapeles no contiene texto.',False);return 'break'
        try:entrada.delete('sel.first','sel.last')
        except tk.TclError:pass
        entrada.insert('insert',contenido);entrada.focus_force();self.estado.set('')
        return 'break'

    def actualizar_frase(self):
        self.frase.set(ui('Capri, pon mi playlist «{0}».').format(self.nombre.get().strip() or ui('Para jugar')))

    def pegar(self):
        try:self.enlace.set(self.ventana.clipboard_get().strip());self.estado.set('');self.entrada_enlace.focus_force()
        except tk.TclError:self.mensaje('El portapapeles no contiene texto.',False)

    def mensaje(self,texto,bien=True):
        self.error.configure(fg=VERDE if bien else ACENTO);self.estado.set(ui(texto))

    def guardar(self):
        nombre=' '.join(self.nombre.get().split());enlace=self.enlace.get().strip()
        if not nombre:self.mensaje('Escribe un nombre para pedir esta playlist.',False);self.entrada_nombre.focus_set();return
        if len(nombre)>200:self.mensaje('Usa un nombre de hasta 200 caracteres.',False);return
        try:uri=uri_playlist(enlace)
        except ValueError:self.mensaje('Pega un enlace de playlist de Spotify válido.',False);self.entrada_enlace.focus_set();return
        destino=next((r for r in self.registros if r['clave']==clave(nombre)),None)
        if destino and destino['clave']!=self.editando and (destino['uri']!=uri or self.editando):
            self.mensaje('Ese nombre ya está guardado. Elige otro o edita la playlist.',False);return
        try:vincular(nombre,uri,self.carpeta,anterior=self.editando)
        except (OSError,ValueError):self.mensaje('No pude guardar la playlist. Inténtalo de nuevo.',False);return
        self.guardado=True;self.editando=clave(nombre);self.nombre.set(nombre)
        self.boton_guardar.configure(text='Guardar cambios');self.mensaje(ui('Guardada como «{0}».').format(nombre))
        self.filtro.set('');self.refrescar()

    def refrescar(self):
        try:self.registros=listar_vinculadas(self.carpeta)
        except (OSError,ValueError):
            self.registros=[];self.mensaje('No pude leer tus playlists guardadas. No se han reemplazado.',False)
        self.registros.sort(key=lambda r:(r.get('guardada',''),r['nombre'].casefold()),reverse=True)
        self.contador.set(f'{len(self.registros):02d}')
        self.pintar_guardadas()
        for r in self.registros:
            if r['uri'] not in self._pedidas and (not r.get('titulo') or not archivo_portada(r['uri'],self.carpeta).is_file()):
                self._pedidas.add(r['uri']);self._solicitudes.put(r['uri'])
        if self._hilo is None and not self._solicitudes.empty():
            self._hilo=threading.Thread(target=self.leer_metadatos,daemon=True,name='Capri-playlists');self._hilo.start()

    def leer_metadatos(self):
        while not self._fin.is_set():
            try:uri=self._solicitudes.get(timeout=.2)
            except queue.Empty:continue
            try:
                titulo=consultar_playlist(uri,self.carpeta)
                if self._fin.is_set():return
                if titulo:actualizar_titulo(uri,titulo,self.carpeta)
                self._resultados.put(uri)
            except (OSError,ValueError,TypeError):pass

    def procesar_resultados(self):
        self._poll=None
        if self.cerrado:return
        cambios=False
        while True:
            try:self._resultados.get_nowait();cambios=True
            except queue.Empty:break
        if cambios:self.refrescar()
        self._poll=self.reloj.after(100,self.procesar_resultados)

    def pintar_guardadas(self):
        if self.cerrado:return
        if self.estado_biblioteca:self.estado_biblioteca.destroy();self.estado_biblioteca=None
        self.lista.pack_forget()
        if not self.filtro_panel.winfo_manager():self.filtro_panel.pack(fill='x',pady=(0,12))
        for w in self.lista.interior.winfo_children():w.destroy()
        self.tarjetas={};buscado=clave(self.filtro.get())
        registros=[r for r in self.registros if not buscado or buscado in clave(r['nombre']+' '+str(r.get('titulo','')))]
        if not registros:
            filtrado=bool(buscado)
            def accion():
                if filtrado:self.filtro.set('');self.busqueda.focus_force()
                else:self.entrada_nombre.focus_force()
            self.estado_biblioteca=EstadoBiblioteca(self.lista.master,filtrado,accion)
            self.estado_biblioteca.pack(fill='both',expand=True)
        else:self.lista.pack(fill='both',expand=True)
        for r in registros:self.crear_tarjeta(r)
        self.lista.conectar();self.lista.ajustar()

    def crear_tarjeta(self,r):
        f=tk.Frame(self.lista.interior,bg=TARJETA,padx=13,pady=12,highlightthickness=1,
                   highlightbackground=ACENTO if r['clave']==self.editando else '#542333')
        f.pack(fill='x',pady=(0,10),padx=(0,2));f.columnconfigure(1,weight=1)
        portada=LienzoUI(f,width=88,height=88,bg=TARJETA,highlightthickness=0,cursor='hand2');portada.grid(row=0,column=0,rowspan=3,sticky='n',padx=(0,15))
        portada.bind('<Button-1>',lambda e:self.capturar_portada(r['uri']))
        tiene_portada=self.pintar_portada(portada,r['uri'])
        fila=tk.Frame(f,bg=TARJETA);fila.grid(row=0,column=1,sticky='ew')
        self.etiqueta(fila,'Pídela como',8,SUAVE).pack(side='left')
        self.etiqueta(fila,'GUARDADA',7,VERDE,True).pack(side='right')
        nombre=self.etiqueta(f,r['nombre'],14,TEXTO,True,literal=True);nombre.grid(row=1,column=1,sticky='ew',pady=(2,4))
        titulo=str(r.get('titulo') or ui('Playlist de Spotify')+' · …'+r['uri'][-8:])
        original=self.etiqueta(f,titulo,10,SUAVE,literal=True);original.grid(row=2,column=1,sticky='ew')
        fecha=r.get('guardada')
        try:fecha=datetime.fromisoformat(fecha).strftime('%d/%m/%Y · %H:%M') if fecha else ''
        except (ValueError,TypeError):fecha=''
        origen=self.etiqueta(f,ui('Guardada el {0}').format(fecha) if fecha else enlace_web(r['uri']),8,SUAVE,literal=True)
        origen.grid(row=3,column=0,columnspan=2,sticky='ew',pady=(10,8))
        ayuda_portada=None
        if not tiene_portada:
            ayuda_portada=self.etiqueta(f,'Si la playlist es privada, Spotify no comparte su portada. Pulsa «Portada» → «Capturar» para tomar un pantallazo y seleccionar la imagen.',9,SUAVE)
            ayuda_portada.grid(row=4,column=0,columnspan=2,sticky='ew',pady=(0,10))
        acciones=tk.Frame(f,bg=TARJETA);acciones.grid(row=5,column=0,columnspan=2,sticky='ew')
        opciones=(('Spotify ↗',lambda:self.abrir(r['uri'])),('Editar',lambda:self.editar(r['clave'])),
                  ('Portada',lambda:self.capturar_portada(r['uri'])),('Quitar vínculo',lambda:self.confirmar_quitar(r['clave'])))
        botones={}
        for i,(texto,comando) in enumerate(opciones):
            b=BotonCyber(acciones,text=texto,command=comando,estilo='secundario',bg=TARJETA,font=(FAMILIA,8),padx=6,pady=3)
            botones[texto]=b
        def distribuir(e=None):
            columnas=4 if acciones.winfo_width()>=410 else 2
            for i,b in enumerate(botones.values()):b.grid(row=i//columnas,column=i%columnas,sticky='ew',padx=(0,6),pady=(0,5))
            for i in range(4):acciones.columnconfigure(i,weight=1 if i<columnas else 0)
        acciones.bind('<Configure>',distribuir);distribuir()
        self.tarjetas[r['clave']]=SimpleNamespace(frame=f,nombre=nombre,titulo=original,acciones=acciones,botones=botones,registro=r,ayuda_portada=ayuda_portada)

    def pintar_portada(self,c,uri):
        ruta=archivo_portada(uri,self.carpeta)
        try:
            marca=ruta.stat().st_mtime_ns
            if uri not in self.fotos or self.fotos[uri][0]!=marca:
                with Image.open(ruta) as imagen:foto=ImageTk.PhotoImage(imagen.convert('RGB').resize((88,88),Image.Resampling.LANCZOS))
                self.fotos[uri]=(marca,foto)
            c.create_image(44,44,image=self.fotos[uri][1]);return True
        except (OSError,ValueError):pass
        c.create_polygon(1,1,74,1,87,14,87,87,1,87,fill='#1b1620',outline='#683044')
        for x,h in ((20,18),(32,35),(44,49),(56,31),(68,15)):
            c.create_line(x,39-h/2,x,39+h/2,fill=ACENTO,width=3)
        c.create_text(44,75,text='Portada',fill=VERDE,font=(FAMILIA,8,'bold'))
        return False

    def capturar_portada(self,uri):
        if self.captura and not self.captura.cerrado:return
        from portadas_ui import CapturaPortada
        def guardar(imagen):
            if self.cerrado:return
            try:guardar_portada(imagen,uri,self.carpeta)
            except (OSError,ValueError):self.mensaje('No pude guardar la portada.',False);return
            self.fotos.pop(uri,None);self.pintar_guardadas();self.mensaje('Portada guardada.')
        self.captura=CapturaPortada(self.ventana,uri,guardar,
            lambda:self.mensaje('Captura cancelada.') if not self.cerrado else None)

    def editar(self,k):
        r=next((r for r in self.registros if r['clave']==k),None)
        if not r:return
        self.editando=k;self.guardado=False;self.nombre.set(r['nombre']);self.enlace.set(enlace_web(r['uri']))
        self.boton_guardar.configure(text='Guardar cambios');self.mensaje(ui('Editando «{0}».').format(r['nombre']))
        self.pintar_guardadas();self.entrada_nombre.focus_set()

    def confirmar_quitar(self,k):
        tarjeta=self.tarjetas.get(k)
        if not tarjeta:return
        tarjeta.acciones.unbind('<Configure>')
        for w in tarjeta.acciones.winfo_children():w.destroy()
        self.etiqueta(tarjeta.acciones,'¿Quitar este nombre de Capri?',9,TEXTO).pack(anchor='w',pady=(0,5))
        fila=tk.Frame(tarjeta.acciones,bg=TARJETA);fila.pack(fill='x')
        for texto,comando in (('Cancelar',self.pintar_guardadas),('Quitar',lambda:self.quitar(k))):
            BotonCyber(fila,text=texto,command=comando,estilo='secundario',bg=TARJETA,font=(FAMILIA,8),padx=7,pady=3).pack(side='left',padx=(0,6))
        self.lista.conectar()

    def quitar(self,k):
        try:quitar_vinculo(k,self.carpeta)
        except (OSError,ValueError):self.mensaje('No pude quitar el vínculo. Inténtalo de nuevo.',False);return
        if self.editando==k:self.reiniciar()
        self.refrescar();self.mensaje('Vínculo quitado.')

    def copiar(self,uri):
        self.ventana.clipboard_clear();self.ventana.clipboard_append(enlace_web(uri));self.mensaje('Enlace copiado.')

    def abrir(self,uri):
        try:os.startfile(enlace_web(uri))
        except OSError:self.copiar(uri)

    def reiniciar(self):
        self.editando=None;self.guardado=False;self.nombre.set('');self.enlace.set('');self.estado.set('')
        self.boton_guardar.configure(text='Guardar playlist');self.pintar_guardadas();self.entrada_nombre.focus_set()

    def cerrar(self):
        if self.cerrado:return
        self.cerrado=True;self._fin.set()
        if self.captura and not self.captura.cerrado:self.captura.cancelar()
        if self._poll is not None:self.reloj.after_cancel(self._poll);self._poll=None
        if self.ventana.grab_current() is self.ventana:self.ventana.grab_release()
        self.ventana.destroy()

    def destruir(self,e):
        if e.widget is self.ventana:
            self.cerrado=True;self._fin.set()
            if self.captura and not self.captura.cerrado:self.captura.cancelar()
            if self._poll is not None:self.reloj.after_cancel(self._poll);self._poll=None
