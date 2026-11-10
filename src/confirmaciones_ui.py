"""Revisión visual del cambio y orientación local antes de guardar preferencias."""
import queue
import threading
import time
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui,idioma_actual

TEXTOS=('Confirmar cambio','Cancelar','Confirmar','Actual: {0}','Nuevo: {0}')


class ConfirmarCambio:
    def __init__(self,padre,titulo,texto,aceptar,cancelar=None,actual=None,nuevo=None,evaluar=None,equipo=None):
        self.aceptar_callback=aceptar;self.cancelar_callback=cancelar or (lambda:None)
        self.cerrado=False;self.confirmado=False;self._tarea=None;self.evaluar=evaluar
        self._tarea_tamano=None;self._minimo_contenido=0
        self.analisis_listo=False;self.equipo={};self.informe={};self.etiquetas=[];self.texto_base=texto
        v=self.ventana=tk.Toplevel(padre);v.withdraw();v.title(ui(titulo))
        from ventanas import area_trabajo
        l,t,r,b=area_trabajo();ancho=min(680,r-l-48);alto=min(520,b-t-48)
        v.geometry(f'{ancho}x{alto}');v.minsize(min(600,ancho),200)
        self.marco=VentanaCyber(v,'Confirmar cambio',cerrar=self.cancelar)
        f=tk.Frame(self.marco.cuerpo,bg=FONDO);f.pack(fill='both',expand=True)
        pie=self.pie=tk.Frame(f,bg=FONDO,padx=20,pady=10);pie.pack(side='bottom',fill='x')
        tk.Frame(pie,bg='#512333',height=1).pack(fill='x',pady=(0,10))
        self.boton_cancelar=BotonCyber(pie,text='Cancelar',command=self.cancelar,estilo='secundario',bg=TARJETA,pady=10)
        self.boton_cancelar.pack(side='left')
        self.boton_aceptar=BotonCyber(pie,text='Aplicar cambio',command=self.aceptar,estilo='principal',bg=ACENTO,fg=FONDO,pady=10,state='disabled')
        self.boton_aceptar.pack(side='right')
        interior=self.contenido=tk.Frame(f,bg=FONDO);interior.pack(fill='x',padx=20)
        interior.bind('<Configure>',self.programar_tamano)
        pie.bind('<Configure>',self.programar_tamano)
        cabecera=LienzoUI(interior,height=54,bg=FONDO,highlightthickness=0);cabecera.pack(fill='x',pady=(2,8))
        def dibujar(e):
            c=cabecera;w=e.width;c.delete('all')
            c.create_text(0,23,text=titulo,anchor='w',width=max(220,w-58),fill=TEXTO,font=(FAMILIA,19,'bold'))
            c.create_polygon(w-24,5,w-5,16,w-5,38,w-24,49,w-43,38,w-43,16,fill=TARJETA,outline=ACENTO)
            from monitor_diseno import icono
            icono(c,'cpu',w-24,27,ACENTO)
            c.create_line(0,51,60,51,fill=ACENTO,width=2)
        cabecera.bind('<Configure>',dibujar)
        comparacion=tk.Frame(interior,bg=FONDO);comparacion.pack(fill='x',pady=(0,12))
        comparacion.columnconfigure(0,weight=1,uniform='opciones');comparacion.columnconfigure(2,weight=1,uniform='opciones')
        for col,tipo,valor,tinta in ((0,'AHORA',actual or ui('Sin activar'),SUAVE),(2,'PROPUESTA',nuevo or ui(titulo),ACENTO)):
            tarjeta=tk.Frame(comparacion,bg=TARJETA,padx=13,pady=9,highlightthickness=1,highlightbackground='#683044')
            tarjeta.grid(row=0,column=col,sticky='nsew')
            self._label(tarjeta,tipo,8,tinta).pack(anchor='w',pady=(0,5))
            self._label(tarjeta,valor,11,TEXTO,True,literal=True).pack(fill='x')
        flecha=LienzoUI(comparacion,width=30,height=48,bg=FONDO,highlightthickness=0)
        flecha.grid(row=0,column=1);flecha.create_line(6,24,23,24,fill=ACENTO,width=2)
        flecha.create_line(17,18,23,24,17,30,fill=ACENTO,width=2)
        hero=tk.Frame(interior,bg=TARJETA,padx=15,pady=12,highlightthickness=1,highlightbackground='#683044')
        hero.pack(fill='x',pady=(0,12))
        self._label(hero,'AL CAMBIAR',8,ACENTO,True).pack(anchor='w',pady=(0,7))
        self.resumen=self._label(hero,texto,14,TEXTO,True);self.resumen.pack(fill='x')
        pc=tk.Frame(interior,bg='#1b1620',padx=13,pady=9);pc.pack(fill='x',pady=(0,4))
        fila=tk.Frame(pc,bg=pc.cget('bg'));fila.pack(fill='x',pady=(0,5))
        self.veredicto=self._label(fila,'PARA TU PC',8,SUAVE,True);self.veredicto.pack(side='left',anchor='s')
        self.boton_releer=BotonCyber(fila,text='Volver a evaluar',command=self.iniciar_lectura,
            estilo='secundario',bg=pc.cget('bg'),font=(FAMILIA,8),padx=8,pady=2)
        self.boton_releer.pack(side='right')
        self.consejo=self._label(pc,'Comprobando tu equipo…',11,TEXTO);self.consejo.pack(fill='x')
        v.bind('<Configure>',lambda e:self.programar_tamano() if e.widget is v else None,add='+')
        v.bind('<Destroy>',self._destruir,add='+');v._capri_cerrar_temporal=self.cancelar
        v.protocol('WM_DELETE_WINDOW',self.cancelar)
        self.mostrar_analisis(equipo or {})
        v.deiconify();v.update_idletasks()
        ancho,alto=v.winfo_width(),v.winfo_height()
        x=max(l+16,min(padre.winfo_rootx()+(padre.winfo_width()-ancho)//2,r-ancho-16))
        y=max(t+16,min(padre.winfo_rooty()+(padre.winfo_height()-alto)//2,b-alto-16))
        v.geometry(f'+{x}+{y}');v.lift();self.boton_cancelar.focus_set()
        if equipo is None:self.iniciar_lectura()

    def programar_tamano(self,e=None):
        if not self.cerrado and self._tarea_tamano is None:
            self._tarea_tamano=self.ventana.after_idle(self.ajustar_tamano)

    def ajustar_tamano(self):
        self._tarea_tamano=None
        if self.cerrado:return
        from ventanas import area_trabajo
        l,t,r,b=area_trabajo();max_ancho=max(100,r-l-32);max_alto=max(100,b-t-32)
        v=self.ventana;ancho=min(max_ancho,max(min(600,max_ancho),v.winfo_width()))
        necesario=self.contenido.winfo_reqheight()+self.pie.winfo_reqheight()+68
        # Al acercarse al borde de la pantalla, refluye el texto con más ancho.
        if necesario>max_alto and ancho<max_ancho:
            ancho=min(max_ancho,ancho+100)
        alto=min(max_alto,max(200,necesario))
        if self._minimo_contenido!=alto:
            v.minsize(min(600,max_ancho),alto);self._minimo_contenido=alto
        v.maxsize(max_ancho,max_alto)
        x=max(l+16,min(v.winfo_x(),r-ancho-16));y=max(t+16,min(v.winfo_y(),b-alto-16))
        if (v.winfo_width(),v.winfo_height(),v.winfo_x(),v.winfo_y())!=(ancho,alto,x,y):
            v.geometry(f'{ancho}x{alto}{x:+d}{y:+d}')

    def iniciar_lectura(self):
        if self.cerrado:return
        if self._tarea is not None:self.ventana.after_cancel(self._tarea)
        self.analisis_listo=False;self._cola=cola=queue.Queue();self._plazo=time.monotonic()+3
        self.boton_aceptar.configure(state='disabled');self.boton_releer.configure(state='disabled')
        self.consejo.configure(text=ui('Comprobando tu equipo…'),fg=SUAVE)
        def leer():
            from equipo_pc import leer_equipo
            try:datos=leer_equipo()
            except Exception:datos={}
            cola.put(datos)
        threading.Thread(target=leer,daemon=True,name='Capri-equipo').start()
        self._tarea=self.ventana.after(25,self._recibir)

    def _label(self,padre,texto,tamano,tinta,negrita=False,literal=False):
        familia='Yu Gothic UI' if idioma_actual()=='ja' else FAMILIA
        l=tk.Label(padre,text=texto if literal else ui(texto),bg=padre.cget('bg'),fg=tinta,
                   font=(familia,tamano,'bold') if negrita else (familia,tamano),anchor='nw',justify='left',wraplength=360)
        l._capri_contenido_usuario=literal
        self.etiquetas.append(l);ancho_anterior=[0]
        def ajustar(e):
            if e.width<50:return
            ancho=max(40,e.width-2)
            if ancho!=ancho_anterior[0]:l.configure(wraplength=ancho);ancho_anterior[0]=ancho
            self.programar_tamano()
        l.bind('<Configure>',ajustar,add='+')
        return l

    def _recibir(self):
        self._tarea=None
        if self.cerrado:return
        try:datos=self._cola.get_nowait()
        except queue.Empty:
            if time.monotonic()<self._plazo:
                self._tarea=self.ventana.after(40,self._recibir);return
            datos={}
        self.mostrar_analisis(datos)

    def mostrar_analisis(self,equipo):
        if self.cerrado:return
        self.equipo=equipo
        try:informe=self.evaluar(equipo) if self.evaluar else {}
        except Exception:informe={}
        self.informe=informe;estado=informe.get('estado','desconocido')
        tinta={'recomendado':'#8be0c0','precaucion':'#ffc77a','limitado':'#ff8da6'}.get(estado,SUAVE)
        self.veredicto.configure(text=ui('PARA TU PC'))
        self.resumen.configure(text=informe.get('resumen',self.texto_base if not self.evaluar else ui('No pude comparar estas opciones.')))
        self.consejo.configure(text=informe.get('consejo_breve',ui('No pude comprobar si conviene en tu PC.')),fg=tinta)
        self.analisis_listo=True;self.boton_aceptar.configure(state='normal')
        self.boton_releer.configure(state='normal')
        self.programar_tamano()

    def _destruir(self,e):
        if e.widget is not self.ventana:return
        self.cerrado=True
        if self._tarea is not None:self.ventana.after_cancel(self._tarea);self._tarea=None
        if self._tarea_tamano is not None:self.ventana.after_cancel(self._tarea_tamano);self._tarea_tamano=None

    def finalizar(self,confirmado):
        if self.cerrado:return
        self.cerrado=True;self.confirmado=confirmado
        if self._tarea is not None:self.ventana.after_cancel(self._tarea);self._tarea=None
        if self._tarea_tamano is not None:self.ventana.after_cancel(self._tarea_tamano);self._tarea_tamano=None
        if self.ventana.grab_current() is self.ventana:self.ventana.grab_release()
        self.ventana.destroy()
        (self.aceptar_callback if confirmado else self.cancelar_callback)()

    def aceptar(self):self.finalizar(True)
    def cancelar(self):self.finalizar(False)
