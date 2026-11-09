"""Confirmaciones de configuración: sin guardar ni cargar nada hasta aceptar."""
from tema_ui import tk
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui

TEXTOS=('Confirmar cambio','Cancelar','Confirmar','Actual: {0}','Nuevo: {0}')


class ConfirmarCambio:
    def __init__(self,padre,titulo,texto,aceptar,cancelar=None,actual=None,nuevo=None):
        self.aceptar_callback=aceptar;self.cancelar_callback=cancelar or (lambda:None)
        self.cerrado=False;self.confirmado=False
        v=self.ventana=tk.Toplevel(padre);v.withdraw();v.title(ui(titulo));v.transient(padre)
        v.geometry('620x480');v.minsize(560,440)
        self.marco=VentanaCyber(v,'Confirmar cambio',cerrar=self.cancelar)
        f=tk.Frame(self.marco.cuerpo,bg=FONDO,padx=20,pady=10);f.pack(fill='both',expand=True)
        tk.Label(f,text=ui(titulo),bg=FONDO,fg=TEXTO,font=(FAMILIA,18,'bold'),anchor='w').pack(fill='x',pady=(0,12))
        self.etiquetas=[]
        if actual is not None:
            tarjeta=tk.Frame(f,bg=TARJETA,padx=14,pady=10);tarjeta.pack(fill='x',pady=(0,12))
            for patron,valor in (('Actual: {0}',actual),('Nuevo: {0}',nuevo)):
                l=tk.Label(tarjeta,text=ui(patron).format(valor),bg=TARJETA,fg=TEXTO,font=(FAMILIA,10),anchor='w',justify='left')
                l.pack(fill='x',pady=2);self.etiquetas.append(l)
        pie=tk.Frame(f,bg=FONDO);pie.pack(side='bottom',fill='x',pady=(14,0))
        self.boton_cancelar=BotonCyber(pie,text='Cancelar',command=self.cancelar,estilo='secundario',bg=TARJETA)
        self.boton_cancelar.pack(side='left')
        self.boton_aceptar=BotonCyber(pie,text='Confirmar',command=self.aceptar,estilo='principal',bg=ACENTO,fg=FONDO)
        self.boton_aceptar.pack(side='right')
        detalle=tk.Label(f,text=texto,bg=FONDO,fg=SUAVE,font=(FAMILIA,11),anchor='nw',justify='left')
        detalle.pack(fill='both',expand=True);self.etiquetas.append(detalle)
        def adaptar(e):
            for l in self.etiquetas:l.configure(wraplength=max(180,e.width-32))
        f.bind('<Configure>',adaptar)
        v.bind('<Destroy>',lambda e:setattr(self,'cerrado',True) if e.widget is v else None,add='+')
        v._capri_cerrar_temporal=self.cancelar
        v.protocol('WM_DELETE_WINDOW',self.cancelar)
        from idiomas import localizar_widgets
        localizar_widgets(v,True);v.deiconify();v.lift();v.grab_set()
        self.boton_cancelar.focus_set()

    def finalizar(self,confirmado):
        if self.cerrado:return
        self.cerrado=True;self.confirmado=confirmado
        if self.ventana.grab_current() is self.ventana:self.ventana.grab_release()
        self.ventana.destroy()
        (self.aceptar_callback if confirmado else self.cancelar_callback)()

    def aceptar(self):self.finalizar(True)
    def cancelar(self):self.finalizar(False)
