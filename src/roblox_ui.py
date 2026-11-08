"""Biblioteca de experiencias y acompañamiento automático de Capri."""
import queue,threading,re
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,InterruptorCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from desplazamiento_ui import Desplazable
from fuentes import FAMILIA
from idiomas import ui
from roblox import normalizar,seleccionado,agregar_favorito,ErrorRoblox
from roblox_dialogos import PERFILES,elegir,opinion
from roblox_info import ubicacion

CIAN='#5ce2e7'
TEXTOS=('Tu próxima partida, con Capri.','Experiencias','Avatar','Acompañamiento','Filtrar favoritos',
 'Buscar en mis favoritos','Escribe el nombre del juego…',
 'Agregar experiencia','Abrir experiencia','Quitar favorito','Actualizar','Nombre de usuario o ID','Guardar usuario',
 'Mirar mi avatar','Comentar cambios de mi avatar','Elige una experiencia','Todavía no tienes favoritos.',
 'Tus favoritos son accesos rápidos para abrir los juegos que más usas.','Pega el enlace de un juego para empezar.',
 'Descripción de la experiencia','Capri se adapta a este juego','Perfil automático · {0}',
 'Según la descripción y las categorías publicadas por su creador.','Consultando la experiencia…',
 'Aún no hay información pública disponible para este enlace.','Por {0}',
 'Nuevo favorito','Enlace oficial o ID','Nombre personalizado (opcional)','Guardar favorito','Cancelar',
 'Si lo dejas vacío, Capri usa el nombre de la experiencia.','Favorito guardado.','Selecciona un favorito.',
 'No pude leer la información de esta experiencia.','Tu avatar, pieza por pieza','Lo que llevas',
 'Guarda tu usuario y Capri consultará el avatar público de esa cuenta.','Usa el nombre de usuario, no el nombre visible.',
 'La opinión usa los nombres y tipos de las prendas; el personaje de una experiencia puede ser distinto.',
 'Comenta cuando cambias tu conjunto, sin repetir la misma opinión continuamente.',
 'Capri te acompaña','Acompañamiento automático','Entiende el juego','Reconoce los avisos','Pregunta si tiene dudas',
 'Consulta su descripción y categoría para adaptar su personalidad automáticamente.',
 'Busca avisos de victoria, derrota o muerte sin que tengas que escribir palabras clave.',
 'Si solo aparece un final ambiguo, te pregunta qué ocurrió antes de celebrar o lamentarlo.',
 'Actívalo para que reaccione mientras Roblox está al frente. No necesitas contarle cada resultado.',
 'Algunos juegos usan avisos que todavía no puede reconocer. No detecta todos los sucesos.',
 'No graba partidas ni mueve tu personaje.','Última experiencia identificada: {0}',
 'Esperando a que abras una experiencia de Roblox.','Guardado en este equipo.','Escribe un usuario o ID válido de Roblox.',
 'Avatar de tu cuenta','Sin accesorios identificados','No hay coincidencias.','Cargando miniatura…')

class PanelRoblox:
    def __init__(self,padre,config,guardar,enviar,control,ocultar=None):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.control=control;self.cerrado=False
        self.cola=queue.Queue();self._after=None;self._seleccion=None;self._avatar_clave=None;self._cargando_info=set()
        self._fotos_juegos={};self._stop=threading.Event()
        self.foto=None;self.foto_juego=None;self._firmas=None;self.formulario=None;self.ayudas=[]
        self.estado=tk.StringVar(value=ui('Guardado en este equipo.'));self.filtro=tk.StringVar();self._idioma=None
        self.ventana=w=tk.Toplevel(padre);w.withdraw();w.title('Capri · Roblox')
        w.geometry(f'{min(1040,w.winfo_screenwidth()-64)}x{min(760,w.winfo_screenheight()-80)}');w.minsize(820,580)
        self.marco=VentanaCyber(w,'ROBLOX',self.cerrar,minimizar=ocultar);w.protocol('WM_DELETE_WINDOW',self.cerrar)
        f=self.marco.cuerpo
        cab=tk.Frame(f,bg=FONDO);cab.pack(fill='x',padx=20,pady=(5,16))
        self.etiqueta(cab,'Tu próxima partida, con Capri.',TEXTO,21,negrita=True).pack(anchor='w')
        navegacion=tk.Frame(f,bg=FONDO);navegacion.pack(fill='x',padx=20,pady=(0,16))
        self.botones_pestanas={};self.pestanas={}
        for i,n in enumerate(('Experiencias','Avatar','Acompañamiento')):
            navegacion.columnconfigure(i,weight=1,uniform='tabs')
            b=BotonCyber(navegacion,text=n,command=lambda v=n:self.mostrar(v),estilo='secundario',bg=FONDO,pady=11)
            b.grid(row=0,column=i,sticky='ew',padx=(0,8 if i<2 else 0));self.botones_pestanas[n]=b
        self.contenido=tk.Frame(f,bg=FONDO);self.contenido.pack(fill='both',expand=True,padx=20)
        for n in self.botones_pestanas:self.pestanas[n]=tk.Frame(self.contenido,bg=FONDO)
        self.crear_experiencias(self.pestanas['Experiencias']);self.crear_avatar(self.pestanas['Avatar']);self.crear_acompanamiento(self.pestanas['Acompañamiento'])
        self.etiqueta(f,'',SUAVE,9,textvariable=self.estado).pack(anchor='w',padx=20,pady=(12,8))
        self.mostrar('Experiencias');self.filtro.trace_add('write',self.filtrar)
        self.pintar_filtro()
        self.refrescar();w.deiconify()
    @staticmethod
    def etiqueta(p,texto,color=TEXTO,tamano=11,negrita=False,**kw):
        return tk.Label(p,text=ui(texto),bg=p.cget('bg'),fg=color,font=(FAMILIA,tamano,'bold' if negrita else 'normal'),anchor='w',justify='left',**kw)
    def parrafo(self,p,texto,color=SUAVE):
        l=self.etiqueta(p,texto,color,10,wraplength=600);l.pack(fill='x',pady=(5,12))
        def ajustar(e):
            ancho=max(160,e.width-8)
            if int(l.cget('wraplength'))!=ancho:l.configure(wraplength=ancho)
        l.bind('<Configure>',ajustar);return l
    def campo(self,p,texto):
        self.etiqueta(p,texto,SUAVE,10).pack(anchor='w',pady=(7,5))
        e=tk.Entry(p,bg=TARJETA,fg=TEXTO,insertbackground=CIAN,relief='flat',font=(FAMILIA,11),highlightthickness=1,highlightbackground='#63334e',highlightcolor=CIAN)
        e.pack(fill='x',ipady=8);return e
    def boton(self,p,texto,accion,principal=False):
        return BotonCyber(p,text=texto,command=accion,estilo='principal' if principal else 'secundario',bg=ACENTO if principal else TARJETA,fg=FONDO if principal else TEXTO,pady=10)
    def mostrar(self,n):
        if n=='Experiencia':n='Experiencias'
        for k,f in self.pestanas.items():f.pack_forget()
        for k,b in self.botones_pestanas.items():b.configure(bg=TARJETA if k==n else FONDO,fg=CIAN if k==n else SUAVE)
        self.pestanas[n].pack(fill='both',expand=True);self.actual=n
    def crear_experiencias(self,p):
        lado=tk.Frame(p,bg=FONDO,width=245);lado.pack(side='left',fill='y',padx=(0,18));lado.pack_propagate(False)
        self.crear_buscador(lado)
        self.biblioteca=Desplazable(lado,bg=FONDO);self.biblioteca.pack(fill='both',expand=True,pady=(12,10))
        self.agregar_boton=self.boton(lado,'Agregar experiencia',self.nuevo_favorito,True)
        self.agregar_boton.pack(side='bottom',fill='x',before=self.biblioteca)
        self.detalle=Desplazable(p,bg=FONDO);self.detalle.pack(side='left',fill='both',expand=True)
        d=self.detalle.interior
        self.hero=tk.Frame(d,bg=TARJETA);self.hero.pack(fill='x',pady=(0,16))
        self.icono=tk.Label(self.hero,text='◇',bg=TARJETA,fg=CIAN,font=(FAMILIA,34),width=5);self.icono.pack(side='left',padx=14,pady=14)
        datos=tk.Frame(self.hero,bg=TARJETA);datos.pack(side='left',fill='both',expand=True,pady=16,padx=(0,14))
        self.titulo=tk.StringVar(value=ui('Elige una experiencia'));self.categoria=tk.StringVar();self.creador=tk.StringVar()
        self.etiqueta(datos,'',TEXTO,18,True,textvariable=self.titulo,wraplength=440).pack(fill='x')
        self.etiqueta(datos,'',CIAN,10,textvariable=self.categoria,wraplength=440).pack(fill='x',pady=(8,4))
        self.etiqueta(datos,'',SUAVE,10,textvariable=self.creador).pack(fill='x')
        datos.bind('<Configure>',lambda e:[w.configure(wraplength=max(100,e.width)) for w in datos.winfo_children() if isinstance(w,tk.Label)])
        acciones=tk.Frame(d,bg=FONDO);acciones.pack(fill='x',pady=(0,18))
        self.abrir=self.boton(acciones,'Abrir experiencia',self.abrir_favorito,True);self.abrir.pack(side='left',fill='x',expand=True,padx=(0,8))
        self.boton(acciones,'Actualizar',lambda:self.cargar_info(True)).pack(side='left')
        tarjeta=tk.Frame(d,bg=TARJETA,padx=16,pady=12);tarjeta.pack(fill='x',pady=(0,18))
        self.etiqueta(tarjeta,'Capri se adapta a este juego',SUAVE,10).pack(anchor='w')
        self.perfil_texto=tk.StringVar();self.etiqueta(tarjeta,'',CIAN,14,True,textvariable=self.perfil_texto).pack(anchor='w',pady=6)
        self.parrafo(tarjeta,'Según la descripción y las categorías publicadas por su creador.')
        self.etiqueta(d,'Descripción de la experiencia',TEXTO,12,True).pack(anchor='w')
        self.descripcion=self.parrafo(d,'Tus favoritos son accesos rápidos para abrir los juegos que más usas.')
        self.quitar_boton=self.boton(d,'Quitar favorito',self.quitar);self.quitar_boton.pack(anchor='w',pady=(10,0))
        self.detalle.conectar()
    def crear_buscador(self,p):
        self.etiqueta(p,'Buscar en mis favoritos',SUAVE,10).pack(anchor='w',pady=(7,6))
        self.filtro_marco=m=tk.Frame(p,bg=TARJETA,highlightthickness=1,highlightbackground='#63334e')
        m.pack(fill='x')
        icono=LienzoUI(m,width=31,height=42,bg=TARJETA,highlightthickness=0)
        icono.pack(side='left');icono.create_oval(9,12,20,23,outline=SUAVE,width=1.5);icono.create_line(19,22,25,28,fill=SUAVE,width=1.5)
        self.borrar_filtro=LienzoUI(m,width=28,height=42,bg=TARJETA,highlightthickness=0,cursor='hand2',takefocus=True)
        self.borrar_filtro.create_line(9,17,18,26,fill=SUAVE,width=1.5);self.borrar_filtro.create_line(18,17,9,26,fill=SUAVE,width=1.5)
        self.borrar_filtro.bind('<Button-1>',lambda e:self.limpiar_filtro());self.borrar_filtro.bind('<Return>',lambda e:self.limpiar_filtro())
        self.filtro_entrada=tk.Entry(m,textvariable=self.filtro,bg=TARJETA,fg=TEXTO,insertbackground=CIAN,
            relief='flat',bd=0,highlightthickness=0,font=(FAMILIA,10),width=12)
        self.filtro_entrada.pack(side='left',fill='both',expand=True,padx=(0,5))
        self.filtro_ayuda=self.etiqueta(m,'Escribe el nombre del juego…',SUAVE,9)
        self.filtro_ayuda.bind('<Button-1>',lambda e:self.filtro_entrada.focus_set())
        self.filtro_entrada.bind('<FocusIn>',lambda e:self.enfocar_filtro(True))
        self.filtro_entrada.bind('<FocusOut>',lambda e:self.enfocar_filtro(False))
        self.filtro_entrada.bind('<Escape>',lambda e:self.limpiar_filtro())
        self._filtro_enfocado=False
    def enfocar_filtro(self,activo):
        self._filtro_enfocado=activo;self.filtro_marco.configure(highlightbackground=CIAN if activo else '#63334e');self.pintar_filtro()
    def pintar_filtro(self):
        if self.filtro.get():self.borrar_filtro.pack(side='right',before=self.filtro_entrada)
        else:self.borrar_filtro.pack_forget()
        if not self.filtro.get() and not self._filtro_enfocado:
            self.filtro_ayuda.place(in_=self.filtro_entrada,x=0,y=0,relwidth=1,relheight=1);self.filtro_ayuda.lift()
        else:self.filtro_ayuda.place_forget()
    def limpiar_filtro(self):
        self.filtro.set('');self.filtro_entrada.focus_set()
        return 'break'
    def filtrar(self,*a):
        self.pintar_filtro();self.reconstruir_favoritos(reiniciar=True)
    def reconstruir_favoritos(self,reiniciar=False):
        for w in self.biblioteca.interior.winfo_children():w.destroy()
        from roblox import clave
        filtro=clave(self.filtro.get());filas=[f for f in self.config['favoritos'] if filtro in clave(f['nombre'])]
        for f in filas:
            activo=f['id']==self.config['seleccion'];card=tk.Frame(self.biblioteca.interior,bg=TARJETA if activo else FONDO,cursor='hand2',padx=12,pady=11,highlightthickness=1,highlightbackground=ACENTO if activo else '#3b2330')
            card.pack(fill='x',pady=(0,8));self.etiqueta(card,f['nombre'],TEXTO,11,activo,wraplength=194).pack(fill='x')
            info=self.control.informacion.get(f['id']);self.etiqueta(card,info.get('genero','Roblox') if info else 'Roblox',CIAN if activo else SUAVE,9).pack(fill='x',pady=(4,0))
            for w in [card]+card.winfo_children():w.bind('<Button-1>',lambda e,i=f['id']:self.seleccionar(i))
        if not filas:self.parrafo(self.biblioteca.interior,'No hay coincidencias.' if filtro else 'Todavía no tienes favoritos.')
        self.biblioteca.conectar();self.biblioteca.ajustar()
        if reiniciar:self.biblioteca.lienzo.yview_moveto(0);self.biblioteca.restante=0
    def seleccionar(self,identidad):
        d=self.control.copia();d['seleccion']=identidad;self.actualizar(d)
    def actualizar(self,d):
        self.guardar('roblox',normalizar(d));self.config=self.control.copia();self.estado.set(ui('Guardado en este equipo.'));self._firmas=None;self.refrescar_seleccion()
    def refrescar_seleccion(self):
        f=seleccionado(self.config);identidad=f['id'] if f else ''
        self.reconstruir_favoritos()
        if identidad!=self._seleccion:
            self._seleccion=identidad;self.foto_juego=None;self.icono.configure(image='',text='◇',width=5)
            self.detalle.lienzo.yview_moveto(0);self.pintar_info();self.cargar_info()
    def pintar_info(self):
        f=seleccionado(self.config);info=self.control.informacion.get(f['id']) if f else None
        self.titulo.set(info['nombre'] if info else f['nombre'] if f else ui('Elige una experiencia'))
        self.categoria.set(' · '.join(filter(None,(info.get('genero'),info.get('subgenero')))) if info else '')
        self.creador.set(ui('Por {0}').format(info['creador']) if info and info.get('creador') else '')
        self.perfil_texto.set(ui('Perfil automático · {0}').format(elegir(PERFILES[info['perfil'] if info else 'clasica'])))
        self.descripcion.configure(text=info['descripcion'] if info else ui('Consultando la experiencia…') if f and f['id'] in self._cargando_info else ui('Aún no hay información pública disponible para este enlace.') if f else ui('Pega el enlace de un juego para empezar.'))
        for b in (self.abrir,self.quitar_boton):b.configure(state='normal' if f else 'disabled')
    def cargar_info(self,forzar=False):
        f=seleccionado(self.config)
        if not f:return
        info=self.control.informacion_guardada(f)
        if info:self.pintar_info();self.restaurar_icono(info)
        if f['id'] in self._cargando_info:return
        self._cargando_info.add(f['id']);self.pintar_info()
        def trabajar(f=dict(f),control=self.control,cola=self.cola,detener=self._stop):
            try:
                info=control.detalles(f,forzar);cola.put(('info',f['id'],info));im=None
                for intento in range(3):
                    if detener.is_set() or control.fin.is_set():return
                    try:im=control.cliente.icono_experiencia(info['universo'],forzar=forzar or intento>0)
                    except (ErrorRoblox,OSError,ValueError):im=None
                    if im is not None:break
                    if intento<2 and detener.wait(intento+1):return
                cola.put(('icono',f['id'],(info['universo'],im)))
            except (ErrorRoblox,OSError,ValueError) as e:cola.put(('error',f['id'],str(e)))
            finally:cola.put(('carga_fin',f['id'],None))
        threading.Thread(target=trabajar,daemon=True,name='Capri-experiencia-publica').start()
    def guardar_foto(self,universo,imagen):
        from PIL import Image,ImageTk
        foto=ImageTk.PhotoImage(imagen.resize((112,112),Image.Resampling.LANCZOS),master=self.ventana)
        self._fotos_juegos[str(universo)]=foto;return foto
    def restaurar_icono(self,info):
        universo=str(info['universo']);foto=self._fotos_juegos.get(universo)
        if foto is None:
            im=self.control.cliente.icono_guardado(universo)
            if im is not None:foto=self.guardar_foto(universo,im)
        if foto is not None:
            self.foto_juego=foto;self.icono.configure(image=foto,text='',width=112)
    def abrir_favorito(self):
        f=seleccionado(self.control.copia())
        if f:self.enviar('abre '+f['nombre']+' en roblox')
    def quitar(self):
        d=self.control.copia();f=seleccionado(d)
        if f:self.actualizar({**d,'favoritos':[x for x in d['favoritos'] if x['id']!=f['id']],'seleccion':''})
    def nuevo_favorito(self):
        if self.formulario and self.formulario.winfo_exists():self.formulario.lift();return
        w=self.formulario=tk.Toplevel(self.ventana);w.geometry('580x345');w.minsize(500,320);w.title('Capri · Nuevo favorito')
        m=VentanaCyber(w,'ROBLOX',w.destroy);p=tk.Frame(m.cuerpo,bg=FONDO,padx=18);p.pack(fill='both',expand=True)
        self.url=self.campo(p,'Enlace oficial o ID');self.nombre=self.campo(p,'Nombre personalizado (opcional)')
        self.parrafo(p,'Si lo dejas vacío, Capri usa el nombre de la experiencia.')
        fila=tk.Frame(p,bg=FONDO);fila.pack(fill='x',pady=8)
        self.boton(fila,'Guardar favorito',self.agregar,True).pack(side='left',fill='x',expand=True,padx=(0,8))
        self.boton(fila,'Cancelar',w.destroy).pack(side='left');self.url.focus_set()
    def agregar(self):
        try:
            self.actualizar(agregar_favorito(self.control.copia(),self.nombre.get(),self.url.get()))
            if self.formulario:self.formulario.destroy();self.formulario=None
            self.estado.set(ui('Favorito guardado.'))
        except (ErrorRoblox,ValueError) as e:self.estado.set(ui(str(e)))
    def crear_avatar(self,p):
        self.avatar_scroll=Desplazable(p,bg=FONDO);self.avatar_scroll.pack(fill='both',expand=True);d=self.avatar_scroll.interior
        self.etiqueta(d,'Tu avatar, pieza por pieza',TEXTO,18,True).pack(anchor='w',pady=(0,8))
        fila=tk.Frame(d,bg=FONDO);fila.pack(fill='x');entrada=tk.Frame(fila,bg=FONDO);entrada.pack(side='left',fill='x',expand=True,padx=(0,12))
        self.usuario=self.campo(entrada,'Nombre de usuario o ID');self.usuario.insert(0,self.config['usuario'])
        self.boton(fila,'Guardar usuario',self.guardar_usuario).pack(side='left',anchor='s',padx=(0,8));self.boton(fila,'Mirar mi avatar',self.mirar,True).pack(side='left',anchor='s')
        self.parrafo(d,'Usa el nombre de usuario, no el nombre visible.')
        tarjeta=tk.Frame(d,bg=TARJETA,padx=18,pady=18);tarjeta.pack(fill='x',pady=(5,16))
        self.imagen_avatar=tk.Label(tarjeta,text='◇',bg=TARJETA,fg=CIAN,font=(FAMILIA,48),width=5);self.imagen_avatar.pack(side='left',anchor='n',padx=(0,18))
        self.texto_avatar=self.etiqueta(tarjeta,'Guarda tu usuario y Capri consultará el avatar público de esa cuenta.',TEXTO,12,wraplength=650);self.texto_avatar.pack(side='left',fill='both',expand=True)
        tarjeta.bind('<Configure>',lambda e:self.texto_avatar.configure(wraplength=max(240,e.width-220)))
        self.etiqueta(d,'Lo que llevas',TEXTO,12,True).pack(anchor='w',pady=(0,8));self.piezas_frame=tk.Frame(d,bg=FONDO);self.piezas_frame.pack(fill='x')
        self.auto_avatar=tk.BooleanVar(value=self.config['avatar_auto'])
        InterruptorCyber(d,text='Comentar cambios de mi avatar',variable=self.auto_avatar,command=self.cambiar_auto_avatar,bg=FONDO,fg=TEXTO).pack(anchor='w',pady=(16,0))
        self.parrafo(d,'Comenta cuando cambias tu conjunto, sin repetir la misma opinión continuamente.')
        self.parrafo(d,'La opinión usa los nombres y tipos de las prendas; el personaje de una experiencia puede ser distinto.')
        self.avatar_scroll.conectar()
    def guardar_usuario(self):
        valor=self.usuario.get().strip();d=normalizar({**self.control.copia(),'usuario':valor})
        if valor and d['usuario']!=valor:self.estado.set(ui('Escribe un usuario o ID válido de Roblox.'));return False
        self.actualizar(d);return True
    def mirar(self):
        if self.guardar_usuario():self.enviar('mira mi avatar en roblox')
    def cambiar_auto_avatar(self):self.actualizar({**self.control.copia(),'avatar_auto':self.auto_avatar.get()})
    def crear_acompanamiento(self,p):
        self.acompanamiento_scroll=Desplazable(p,bg=FONDO);self.acompanamiento_scroll.pack(fill='both',expand=True);d=self.acompanamiento_scroll.interior
        self.etiqueta(d,'Capri te acompaña',TEXTO,20,True).pack(anchor='w')
        self.parrafo(d,'Actívalo para que reaccione mientras Roblox está al frente. No necesitas contarle cada resultado.')
        self.auto_eventos=tk.BooleanVar(value=self.config['acompanar'])
        InterruptorCyber(d,text='Acompañamiento automático',variable=self.auto_eventos,command=self.cambiar_acompanamiento,bg=FONDO,fg=TEXTO).pack(anchor='w',pady=(8,20))
        for num,t,detalle in (('01','Entiende el juego','Consulta su descripción y categoría para adaptar su personalidad automáticamente.'),
                              ('02','Reconoce los avisos','Busca avisos de victoria, derrota o muerte sin que tengas que escribir palabras clave.'),
                              ('03','Pregunta si tiene dudas','Si solo aparece un final ambiguo, te pregunta qué ocurrió antes de celebrar o lamentarlo.')):
            card=tk.Frame(d,bg=TARJETA,padx=16,pady=10);card.pack(fill='x',pady=(0,10))
            self.etiqueta(card,num,CIAN,12,True).pack(side='left',anchor='n',padx=(0,18))
            texto=tk.Frame(card,bg=TARJETA);texto.pack(side='left',fill='x',expand=True)
            self.etiqueta(texto,t,TEXTO,12,True).pack(anchor='w');self.parrafo(texto,detalle)
        self.juego_detectado=tk.StringVar();self.etiqueta(d,'',CIAN,10,textvariable=self.juego_detectado,wraplength=760).pack(fill='x',pady=(8,4))
        self.parrafo(d,'Algunos juegos usan avisos que todavía no puede reconocer. No detecta todos los sucesos.')
        self.parrafo(d,'No graba partidas ni mueve tu personaje.');self.acompanamiento_scroll.conectar()
    def cambiar_acompanamiento(self):self.actualizar({**self.control.copia(),'acompanar':self.auto_eventos.get()})
    def pintar_avatar(self,a):
        self.texto_avatar.configure(text=opinion(a) if a else ui('Guarda tu usuario y Capri consultará el avatar público de esa cuenta.'))
        for w in self.piezas_frame.winfo_children():w.destroy()
        piezas=[p for p in a.get('piezas',[]) if ubicacion(p)] if a else []
        for p in piezas[:30]:
            self.etiqueta(self.piezas_frame,p['nombre'],TEXTO,10).pack(anchor='w',pady=3)
        if not piezas:self.etiqueta(self.piezas_frame,'Sin accesorios identificados',SUAVE,10).pack(anchor='w')
        self.avatar_scroll.conectar()
    def refrescar(self):
        if self.cerrado:return
        d=self.control.copia()
        firma=tuple((f['id'],f['nombre']) for f in d['favoritos']),d['seleccion']
        self.config=d
        if firma!=self._firmas:self._firmas=firma;self.refrescar_seleccion()
        self.auto_avatar.set(d['avatar_auto']);self.auto_eventos.set(d['acompanar'])
        a=self.control.avatar_actual;marca=(a['usuario'],a['huella']) if a else None
        if marca!=self._avatar_clave:
            self._avatar_clave=marca;self.foto=None;self.imagen_avatar.configure(image='',text='◇',width=5);self.pintar_avatar(a)
            if a:
                def cargar(a=dict(a),marca=marca):
                    try:im=self.control.cliente.miniatura(a['user_id'])
                    except Exception:im=None
                    self.cola.put(('avatar',marca,im))
                threading.Thread(target=cargar,daemon=True,name='Capri-avatar-publico').start()
        while not self.cola.empty():
            tipo,identidad,valor=self.cola.get_nowait()
            if tipo=='carga_fin':
                self._cargando_info.discard(identidad);continue
            if tipo in ('info','error'):
                if identidad==self._seleccion:
                    if tipo=='error':self.estado.set(ui(valor))
                    else:
                        f=seleccionado(self.config)
                        if f and re.fullmatch(r'Experiencia [\da-f]+',f['nombre']):
                            nuevo=self.control.copia();nombre=valor['nombre'][:55]
                            from roblox import clave
                            if not any(x['id']!=identidad and clave(x['nombre'])==clave(nombre) for x in nuevo['favoritos']):
                                nuevo['favoritos']=[{**x,'nombre':nombre} if x['id']==identidad else x for x in nuevo['favoritos']];self.actualizar(nuevo)
                    self.pintar_info();self.reconstruir_favoritos()
                    info=self.control.informacion.get(identidad)
                    if info:self.restaurar_icono(info)
            elif tipo=='icono':
                universo,im=valor
                if im is not None:
                    self.guardar_foto(universo,im)
                    info=self.control.informacion.get(self._seleccion)
                    if info and str(info['universo'])==str(universo):self.restaurar_icono(info)
            elif tipo=='avatar' and valor is not None:
                from PIL import ImageTk
                if identidad==self._avatar_clave:
                    self.foto=ImageTk.PhotoImage(valor,master=self.ventana);self.imagen_avatar.configure(image=self.foto,text='',width=150)
        actual=self.control.experiencia_actual
        self.juego_detectado.set(ui('Última experiencia identificada: {0}').format(actual['nombre']) if actual else ui('Esperando a que abras una experiencia de Roblox.'))
        self._after=self.ventana.after(350,self.refrescar)
    def cerrar(self):
        self.cerrado=True;self._stop.set()
        if self._after:self.ventana.after_cancel(self._after)
        if self.formulario and self.formulario.winfo_exists():self.formulario.destroy()
        self.ventana.destroy()
