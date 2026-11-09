"""Agenda de Capri: creación rápida y próximos avisos ordenados por fecha."""
import datetime
import math
import time
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,SelectorCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO,VERDE
from desplazamiento_ui import Desplazable
from fuentes import FAMILIA
from idiomas import ui,idioma_actual
from recordatorios import agregar,normalizar,ErrorRecordatorio

TEXTOS=('Recordatorios','Yo te aviso.','Deja aquí lo que no quieres olvidar.','Crear un aviso',
        'Por ejemplo: estirar las piernas…','Avisarme en','Minutos','Horas','Días','{0} min','1 h',
        'Crear recordatorio','Tu agenda','PRÓXIMOS AVISOS','{0} pendientes','1 pendiente','PRÓXIMO · {0}',
        'Todo bajo control.','No tienes avisos pendientes. Crea el primero y yo me encargo.',
        'Capri te avisa mientras está abierta.','Hoy','Mañana','Quitar','Listo para avisar',
        'En menos de 1 min','En {0} min','En {0} h {1} min','En {0} días','En 1 día','Te aviso: {0} · {1}',
        'Elige cuándo quieres que te avise.','Recordatorio creado.','Recordatorio eliminado.',
        'Usa hasta 300 caracteres.','Ctrl + Enter para crear',
        'Elige un plazo entre un segundo y siete días.','Puedes guardar hasta 100 recordatorios.',
        'Escribe qué quieres recordar.','Recordatorio: {0}','Te lo recordaré en {0} minutos.','Cancelé tus recordatorios.')


def restante(vence,ahora):
    segundos=vence-ahora
    if segundos<=0:return ui('Listo para avisar')
    if segundos<60:return ui('En menos de 1 min')
    minutos=math.ceil(segundos/60)
    if minutos<60:return ui('En {0} min').format(minutos)
    if minutos<1440:return ui('En {0} h {1} min').format(*divmod(minutos,60))
    if minutos<2880:return ui('En 1 día')
    return ui('En {0} días').format(math.ceil(minutos/1440))


class PanelRecordatorios:
    def __init__(self,padre,leer,guardar,ocultar=None):
        self.leer=leer;self.guardar=guardar;self.cerrado=False;self._after=None;self._firma=None
        self.raiz=padre._root();self._tiempos=[];self.tarjetas={};self._compacto=None
        self.ventana=w=tk.Toplevel(padre);w.withdraw();w.title('Capri · Recordatorios')
        w.geometry(f'{min(940,w.winfo_screenwidth()-64)}x{min(760,w.winfo_screenheight()-80)}');w.minsize(720,660)
        self.marco=VentanaCyber(w,'RECORDATORIOS',self.cerrar,minimizar=ocultar);w.protocol('WM_DELETE_WINDOW',self.cerrar)
        p=tk.Frame(self.marco.cuerpo,bg=FONDO,padx=18,pady=8);p.pack(fill='both',expand=True)
        cab=tk.Frame(p,bg=FONDO);cab.pack(fill='x',pady=(0,18))
        reloj=LienzoUI(cab,width=58,height=58,bg=FONDO,highlightthickness=0);reloj.pack(side='left',padx=(0,14))
        reloj.create_polygon(2,12,12,2,56,2,56,46,46,56,2,56,fill=TARJETA,outline='#603548')
        reloj.create_oval(14,14,44,44,outline=VERDE,width=2)
        reloj.create_line(29,20,29,29,37,33,fill=VERDE,width=2)
        reloj.create_line(29,8,29,11,fill=ACENTO);reloj.create_line(47,29,50,29,fill=ACENTO)
        titulos=tk.Frame(cab,bg=FONDO);titulos.pack(side='left',fill='both',expand=True)
        self.etiqueta(titulos,'Yo te aviso.',TEXTO,25,True).pack(anchor='w')
        self.etiqueta(titulos,'Deja aquí lo que no quieres olvidar.',SUAVE,10).pack(anchor='w',pady=(3,0))
        self.proximo=tk.StringVar()
        self.etiqueta(cab,'',VERDE,9,True,textvariable=self.proximo).pack(side='right',anchor='n',pady=12)
        pie=tk.Frame(p,bg=FONDO);pie.pack(side='bottom',fill='x',pady=(12,0))
        tk.Frame(pie,bg='#442637',height=1).pack(fill='x',pady=(0,8))
        self.etiqueta(pie,'Capri te avisa mientras está abierta.',SUAVE,9).pack(anchor='w')
        cuerpo=tk.Frame(p,bg=FONDO);cuerpo.pack(fill='both',expand=True)
        cuerpo.columnconfigure(0,weight=0,minsize=278);cuerpo.columnconfigure(1,weight=1,minsize=280);cuerpo.rowconfigure(0,weight=1)
        form=self.formulario=tk.Frame(cuerpo,bg=TARJETA,padx=16,pady=16,highlightthickness=1,highlightbackground='#442637')
        form.grid(row=0,column=0,sticky='ns',padx=(0,18))
        form.pack_propagate(False);form.configure(width=300)
        acciones=tk.Frame(form,bg=TARJETA);acciones.pack(side='bottom',fill='x')
        self.titulo_formulario=self.etiqueta(form,'Crear un aviso',TEXTO,17,True)
        self.titulo_formulario.pack(anchor='w',pady=(0,10))
        caja=self.caja_texto=tk.Frame(form,bg=FONDO,highlightbackground='#69404c',highlightthickness=1,padx=10,pady=8);caja.pack(fill='x')
        self.texto=tk.Text(caja,height=2,width=20,wrap='word',bg=FONDO,fg=TEXTO,insertbackground=VERDE,
                           selectbackground='#5e1a30',relief='flat',bd=0,highlightthickness=0,font=(FAMILIA,12),undo=True)
        self.texto.pack(fill='x')
        self.placeholder=tk.Label(self.texto,text=ui('Por ejemplo: estirar las piernas…'),bg=FONDO,fg=SUAVE,
                                  font=(FAMILIA,10),wraplength=220,justify='left',anchor='nw',cursor='xterm')
        self.placeholder.bind('<Button-1>',lambda e:self.texto.focus_set())
        self.texto.bind('<FocusIn>',lambda e:(caja.configure(highlightbackground=ACENTO),self.pintar_placeholder(True)))
        self.texto.bind('<FocusOut>',lambda e:(caja.configure(highlightbackground='#69404c'),self.pintar_placeholder()))
        self.texto.bind('<KeyRelease>',lambda e:self.pintar_placeholder())
        self.texto.bind('<Control-Return>',lambda e:(self.crear(),'break')[1])
        self.etiqueta_plazo=self.etiqueta(form,'Avisarme en',SUAVE,10)
        self.etiqueta_plazo.pack(anchor='w',pady=(18,6))
        plazo=tk.Frame(form,bg=TARJETA);plazo.pack(fill='x');plazo.columnconfigure(1,weight=1)
        campo=tk.Frame(plazo,bg=FONDO,highlightbackground='#69404c',highlightthickness=1,padx=8)
        campo.grid(row=0,column=0,sticky='nsew',padx=(0,8))
        self.minutos=tk.Entry(campo,width=4,justify='center',font=(FAMILIA,17,'bold'),bg=FONDO,fg=TEXTO,
                              insertbackground=VERDE,selectbackground='#5e1a30',relief='flat',bd=0,highlightthickness=0)
        self.minutos.insert(0,'20');self.minutos.pack(fill='both',expand=True,ipady=5)
        self.minutos.bind('<KeyRelease>',lambda e:self.actualizar_plazo())
        self.minutos.bind('<Return>',lambda e:(self.crear(),'break')[1])
        self.unidad=SelectorCyber(plazo,values=('Minutos','Horas','Días'));self.unidad.configure(width=130)
        self.unidad.current(0);self.unidad.grid(row=0,column=1,sticky='ew')
        self.unidad.bind('<<ComboboxSelected>>',lambda e:self.actualizar_plazo())
        chips=tk.Frame(form,bg=TARJETA);chips.pack(fill='x',pady=(10,0));self.atajos={}
        for i,minutos in enumerate((5,15,30,60)):
            chips.columnconfigure(i,weight=1,uniform='plazos')
            boton=BotonCyber(chips,text=ui('1 h') if minutos==60 else ui('{0} min').format(minutos),
                command=lambda m=minutos:self.elegir_plazo(m),estilo='secundario',bg=TARJETA,padx=2,pady=4,font=(FAMILIA,9))
            boton.grid(row=0,column=i,sticky='ew',padx=(0,4) if i<3 else 0);self.atajos[minutos]=boton
        self.prevision=tk.StringVar()
        self.etiqueta_prevision=self.etiqueta(form,'',VERDE,10,textvariable=self.prevision)
        self.etiqueta_prevision.pack(anchor='w',pady=(12,12))
        self.boton_crear=BotonCyber(acciones,text='Crear recordatorio',command=self.crear,estilo='principal',bg=ACENTO,fg=FONDO)
        self.boton_crear.pack(fill='x')
        self.atajo_etiqueta=self.etiqueta(acciones,'Ctrl + Enter para crear',SUAVE,9)
        self.atajo_etiqueta.pack(anchor='w',pady=(8,0))
        self.estado=tk.StringVar()
        self.etiqueta_estado=self.etiqueta(acciones,'',ACENTO,10,textvariable=self.estado,wraplength=250,height=2)
        self.etiqueta_estado.pack(fill='x',pady=(14,0))
        agenda=tk.Frame(cuerpo,bg=FONDO);agenda.grid(row=0,column=1,sticky='nsew')
        arriba=tk.Frame(agenda,bg=FONDO);arriba.pack(fill='x',pady=(0,12))
        self.etiqueta(arriba,'PRÓXIMOS AVISOS',SUAVE,9,True).pack(anchor='w')
        self.etiqueta(arriba,'Tu agenda',TEXTO,18,True).pack(side='left',pady=(5,0))
        self.cantidad=tk.StringVar()
        self.etiqueta(arriba,'',VERDE,10,textvariable=self.cantidad).pack(side='right',pady=(5,0))
        self.lista=Desplazable(agenda,bg=FONDO);self.lista.pack(fill='both',expand=True)
        self.vacio=LienzoUI(agenda,bg=FONDO,highlightthickness=0)
        self.vacio.bind('<Configure>',self.dibujar_vacio)
        form.bind('<Configure>',self.adaptar_formulario)
        w.bind('<Destroy>',self.destruir,add='+')
        self.pintar_placeholder();self.refrescar();w.deiconify()

    @staticmethod
    def etiqueta(p,t,color,tamano,negrita=False,**kw):
        return tk.Label(p,text=ui(t),bg=p.cget('bg'),fg=color,font=(FAMILIA,tamano,'bold' if negrita else 'normal'),
                        anchor='w',justify='left',**kw)

    def adaptar_formulario(self,e):
        ancho=max(160,e.width-40)
        self.placeholder.configure(wraplength=ancho-22)
        for w in (self.etiqueta_prevision,self.etiqueta_estado):w.configure(wraplength=ancho)
        compacto=e.height<470
        if compacto==self._compacto:return
        self._compacto=compacto
        self.texto.configure(height=2,font=(FAMILIA,11 if compacto else 12))
        self.caja_texto.configure(pady=5 if compacto else 8)
        self.titulo_formulario.configure(font=(FAMILIA,15 if compacto else 17,'bold'))
        self.titulo_formulario.pack_configure(pady=(0,6 if compacto else 10))
        self.etiqueta_plazo.pack_configure(pady=(10 if compacto else 18,5 if compacto else 6))
        self.etiqueta_prevision.pack_configure(pady=(6 if compacto else 12,6 if compacto else 12))
        if compacto:self.atajo_etiqueta.pack_forget()
        else:self.atajo_etiqueta.pack(anchor='w',pady=(8,0),after=self.boton_crear)

    def pintar_placeholder(self,enfocada=False):
        if enfocada or self.texto.focus_get() is self.texto or self.texto.get('1.0','end-1c').strip():self.placeholder.place_forget()
        else:self.placeholder.place(x=1,y=0,relwidth=1,relheight=1)

    def plazo(self):
        return float(self.minutos.get().replace(',','.'))*(1,60,1440)[max(0,self.unidad.current())]

    def actualizar_plazo(self):
        try:
            minutos=self.plazo()
            if not math.isfinite(minutos) or not 1/60<=minutos<=10080:raise ValueError()
            fecha=datetime.datetime.fromtimestamp(time.time()+minutos*60)
            self.prevision.set(ui('Te aviso: {0} · {1}').format(self.grupo(fecha.timestamp(),datetime.date.today()),fecha.strftime('%H:%M')))
        except (ValueError,OverflowError):self.prevision.set(ui('Elige cuándo quieres que te avise.'))
        for m,b in self.atajos.items():
            try:seleccionado=abs(self.plazo()-m)<.0001
            except (ValueError,OverflowError):seleccionado=False
            b.configure(bg='#421327' if seleccionado else TARJETA,fg=VERDE if seleccionado else TEXTO)

    def elegir_plazo(self,minutos):
        self.minutos.delete(0,'end');self.minutos.insert(0,'1' if minutos==60 else str(minutos))
        self.unidad.current(1 if minutos==60 else 0);self.actualizar_plazo()

    def crear(self):
        try:
            texto=self.texto.get('1.0','end-1c')
            if len(texto)>300:raise ErrorRecordatorio('Usa hasta 300 caracteres.')
            lista=agregar(self.leer(),texto,self.plazo())
            self.guardar('recordatorios',lista)
            self.texto.delete('1.0','end');self.pintar_placeholder()
            self.estado.set(ui('Recordatorio creado.'));self.refrescar_datos()
        except ValueError as e:
            self.estado.set(ui(str(e)) if isinstance(e,ErrorRecordatorio) else ui('Elige un plazo entre un segundo y siete días.'))

    def cancelar(self,identidad):
        self.guardar('recordatorios',[r for r in self.leer() if r['id']!=identidad])
        self.estado.set(ui('Recordatorio eliminado.'));self.refrescar_datos()

    def grupo(self,fecha,hoy):
        dia=datetime.datetime.fromtimestamp(fecha).date()
        if dia==hoy:return ui('Hoy')
        if dia==hoy+datetime.timedelta(days=1):return ui('Mañana')
        return dia.strftime('%d / %m / %Y')

    def dibujar_vacio(self,e=None):
        c=self.vacio;c.delete('all');w=max(240,c.winfo_width());h=max(250,c.winfo_height());x=w/2;y=min(150,h*.36)
        c.create_polygon(20,35,w-35,35,w-15,55,w-15,h-22,35,h-22,15,h-42,15,55,
                         fill=TARJETA,outline='#442637')
        c.create_oval(x-63,y-63,x+63,y+63,outline='#442637',dash=(3,6))
        c.create_line(x-80,y,x-68,y,fill=ACENTO,width=2);c.create_line(x+68,y,x+80,y,fill=ACENTO,width=2)
        c.create_polygon(x-32,y+20,x-25,y+10,x-25,y-20,x-15,y-34,x+15,y-34,x+25,y-20,x+25,y+10,x+32,y+20,
                         fill=FONDO,outline=VERDE,width=2)
        c.create_line(x-32,y+20,x+32,y+20,fill=VERDE,width=2)
        c.create_arc(x-8,y+19,x+8,y+35,start=180,extent=180,style='arc',outline=ACENTO,width=2)
        c.create_line(x,y-45,x,y-40,fill=ACENTO,width=2)
        c.create_text(x,y+103,text='Todo bajo control.',fill=TEXTO,font=(FAMILIA,17,'bold'),width=w-52)
        c.create_text(x,y+151,text='No tienes avisos pendientes. Crea el primero y yo me encargo.',
                      fill=SUAVE,font=(FAMILIA,10),width=w-70)

    def refrescar_datos(self):
        ahora=time.time();hoy=datetime.datetime.fromtimestamp(ahora).date()
        filas=sorted(normalizar(self.leer()),key=lambda r:r['vence'])
        self.cantidad.set(ui('1 pendiente') if len(filas)==1 else ui('{0} pendientes').format(len(filas)))
        self.proximo.set(ui('PRÓXIMO · {0}').format(datetime.datetime.fromtimestamp(filas[0]['vence']).strftime('%H:%M')) if filas else '')
        firma=(filas,hoy,idioma_actual())
        if firma!=self._firma:
            self._firma=firma;self._tiempos=[];self.tarjetas={}
            for w in self.lista.interior.winfo_children():w.destroy()
            if filas:
                self.vacio.pack_forget();self.lista.pack(fill='both',expand=True)
            else:
                self.lista.pack_forget();self.vacio.pack(fill='both',expand=True);self.dibujar_vacio()
            anterior=None
            for i,r in enumerate(filas):
                grupo=self.grupo(r['vence'],hoy)
                if grupo!=anterior:
                    self.etiqueta(self.lista.interior,grupo.upper(),SUAVE,9,True).pack(anchor='w',padx=3,pady=(8 if i else 0,8));anterior=grupo
                tarjeta=tk.Frame(self.lista.interior,bg=TARJETA,highlightbackground='#69404c' if i==0 else '#442637',highlightthickness=1)
                tarjeta.pack(fill='x',pady=(0,10));self.tarjetas[r['id']]=tarjeta
                tk.Frame(tarjeta,width=3,bg=ACENTO if i==0 else '#69404c').pack(side='left',fill='y')
                f=tk.Frame(tarjeta,bg=TARJETA,padx=14,pady=12);f.pack(fill='both',expand=True)
                fila=tk.Frame(f,bg=TARJETA);fila.pack(fill='x')
                self.etiqueta(fila,datetime.datetime.fromtimestamp(r['vence']).strftime('%H:%M'),VERDE if i==0 else TEXTO,20,True).pack(side='left')
                BotonCyber(fila,text='Quitar',command=lambda identidad=r['id']:self.cancelar(identidad),
                           estilo='secundario',bg=TARJETA,padx=8,pady=3,font=(FAMILIA,9)).pack(side='right')
                texto=tk.Label(f,text=r['texto'],bg=TARJETA,fg=TEXTO,font=(FAMILIA,12),wraplength=350,anchor='w',justify='left')
                texto._capri_contenido_usuario=True;texto.pack(fill='x',pady=(8,10))
                f.bind('<Configure>',lambda e,l=texto:l.configure(wraplength=max(120,e.width-32)))
                tiempo=tk.StringVar()
                self.etiqueta(f,'',SUAVE,9,textvariable=tiempo).pack(anchor='w')
                self._tiempos.append((r['vence'],tiempo))
            self.lista.conectar()
        for vence,variable in self._tiempos:variable.set(restante(vence,ahora))
        self.actualizar_plazo()

    def refrescar(self):
        if self.cerrado:return
        self.refrescar_datos();self._after=self.raiz.after(1000,self.refrescar)

    def cerrar(self):
        if self.cerrado:return
        self.cerrado=True
        if self._after:self.raiz.after_cancel(self._after);self._after=None
        self.ventana.destroy()

    def destruir(self,e):
        if e.widget is self.ventana:
            self.cerrado=True
            if self._after:self.raiz.after_cancel(self._after);self._after=None
