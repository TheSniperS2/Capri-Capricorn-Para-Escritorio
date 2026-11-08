"""Agenda personal de Capri; no pertenece a ninguna integración de juegos."""
import datetime
from tema_ui import tk
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from desplazamiento_ui import Desplazable
from fuentes import FAMILIA
from idiomas import ui
from recordatorios import agregar,normalizar,ErrorRecordatorio

TEXTOS=('Recordatorios','Que Capri te avise.','Qué quieres recordar','Dentro de cuántos minutos','Crear recordatorio',
        'Tus próximos avisos','No tienes recordatorios pendientes.','Cancelar','Recordatorio creado.',
        'Elige un plazo entre un segundo y siete días.','Puedes guardar hasta 100 recordatorios.',
        'Escribe qué quieres recordar.','Los avisos esperan si Capri está hablando. Se conservan al cerrar; vuelven a estar disponibles al abrir Capri.',
        'Puedes decir: «Capri, recuérdame en 20 minutos hacer una pausa».','Recordatorio: {0}',
        'Te lo recordaré en {0} minutos.','Cancelé tus recordatorios.')

class PanelRecordatorios:
    def __init__(self,padre,leer,guardar,ocultar=None):
        self.leer=leer;self.guardar=guardar;self.cerrado=False;self._after=None;self._firma=None
        self.ventana=w=tk.Toplevel(padre);w.withdraw();w.title('Capri · Recordatorios');w.geometry('740x650');w.minsize(640,530)
        marco=VentanaCyber(w,'RECORDATORIOS',self.cerrar,minimizar=ocultar);w.protocol('WM_DELETE_WINDOW',self.cerrar)
        p=tk.Frame(marco.cuerpo,bg=FONDO,padx=20);p.pack(fill='both',expand=True)
        self.etiqueta(p,'Que Capri te avise.',TEXTO,21).pack(anchor='w',pady=(4,12))
        self.etiqueta(p,'Qué quieres recordar',SUAVE,10).pack(anchor='w')
        self.texto=self.entrada(p);self.texto.pack(fill='x',ipady=9,pady=(5,12))
        fila=tk.Frame(p,bg=FONDO);fila.pack(fill='x',pady=(0,8))
        self.etiqueta(fila,'Dentro de cuántos minutos',SUAVE,10).pack(side='left',padx=(0,12))
        self.minutos=self.entrada(fila,width=6);self.minutos.insert(0,'20');self.minutos.pack(side='left',ipady=8,padx=(0,12))
        BotonCyber(fila,text='Crear recordatorio',command=self.crear,estilo='principal',bg=ACENTO,fg=FONDO).pack(side='right')
        self.estado=tk.StringVar();self.etiqueta(p,'',SUAVE,10,textvariable=self.estado).pack(anchor='w',pady=(0,8))
        self.etiqueta(p,'Tus próximos avisos',TEXTO,12).pack(anchor='w',pady=(10,8))
        self.lista=Desplazable(p,bg=FONDO);self.lista.pack(fill='both',expand=True)
        pie=tk.Frame(p,bg=FONDO);pie.pack(side='bottom',fill='x',before=self.lista,pady=(12,8))
        for t,tamano in (('Puedes decir: «Capri, recuérdame en 20 minutos hacer una pausa».',10),
                         ('Los avisos esperan si Capri está hablando. Se conservan al cerrar; vuelven a estar disponibles al abrir Capri.',9)):
            l=self.etiqueta(pie,t,SUAVE,tamano,wraplength=650);l.pack(fill='x',pady=(0,5))
            l.bind('<Configure>',lambda e,l=l:l.configure(wraplength=max(200,e.width)))
        self.refrescar();w.deiconify()
    @staticmethod
    def etiqueta(p,t,color,tamano,**kw):return tk.Label(p,text=ui(t),bg=p.cget('bg'),fg=color,font=(FAMILIA,tamano),anchor='w',justify='left',**kw)
    @staticmethod
    def entrada(p,**kw):return tk.Entry(p,bg=TARJETA,fg=TEXTO,insertbackground=ACENTO,relief='flat',font=(FAMILIA,11),**kw)
    def crear(self):
        try:
            self.guardar('recordatorios',agregar(self.leer(),self.texto.get(),float(self.minutos.get().replace(',','.'))))
            self.texto.delete(0,'end');self.estado.set(ui('Recordatorio creado.'))
        except ValueError as e:self.estado.set(ui(str(e)) if isinstance(e,ErrorRecordatorio) else ui('Elige un plazo entre un segundo y siete días.'))
    def cancelar(self,identidad):self.guardar('recordatorios',[r for r in self.leer() if r['id']!=identidad])
    def refrescar(self):
        if self.cerrado:return
        filas=sorted(normalizar(self.leer()),key=lambda r:r['vence'])
        if filas!=self._firma:
            self._firma=filas
            for w in self.lista.interior.winfo_children():w.destroy()
            for r in filas:
                f=tk.Frame(self.lista.interior,bg=TARJETA,padx=14,pady=12);f.pack(fill='x',pady=(0,8))
                BotonCyber(f,text='Cancelar',command=lambda i=r['id']:self.cancelar(i),estilo='secundario',bg=TARJETA).pack(side='right',padx=(12,0))
                t=tk.Frame(f,bg=TARJETA);t.pack(side='left',fill='both',expand=True)
                self.etiqueta(t,datetime.datetime.fromtimestamp(r['vence']).strftime('%d/%m · %H:%M'),ACENTO,10).pack(anchor='w')
                l=self.etiqueta(t,r['texto'],TEXTO,11,wraplength=450);l.pack(fill='x',pady=(5,0))
                t.bind('<Configure>',lambda e,l=l:l.configure(wraplength=max(120,e.width)))
            if not filas:self.etiqueta(self.lista.interior,'No tienes recordatorios pendientes.',SUAVE,11).pack(anchor='w',pady=18)
            self.lista.conectar()
        self._after=self.ventana.after(500,self.refrescar)
    def cerrar(self):
        self.cerrado=True
        if self._after:self.ventana.after_cancel(self._after)
        self.ventana.destroy()
