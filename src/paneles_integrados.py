"""Contenido de juegos reutilizable en Ajustes y en sus ventanas independientes."""
from types import SimpleNamespace
from tema_ui import tk
from ajustes_ui import VentanaCyber,FONDO


class ContenidoJuego(tk.Frame):
    def __init__(self,padre,panel):
        super().__init__(padre,bg=FONDO)
        self.panel=panel;self._temporizadores=set();self._rueda=None;self._comando_rueda=None
        self._tag='CapriJuego'+str(id(self));self.pack(fill='both',expand=True)

    def after(self,ms,func=None,*args):
        if func is None:return self._root().after(ms)
        identificador=None
        def ejecutar():
            self._temporizadores.discard(identificador)
            if self.winfo_exists() and not self.panel.cerrado:func(*args)
        identificador=self._root().after(ms,ejecutar)
        self._temporizadores.add(identificador);return identificador

    def after_cancel(self,identificador):
        self._temporizadores.discard(identificador);self._root().after_cancel(identificador)

    def bind(self,secuencia=None,func=None,add=None):
        if secuencia=='<MouseWheel>':
            self._rueda=func;return None
        return super().bind(secuencia,func,add)

    def deiconify(self):
        self.winfo_toplevel().deiconify()
        if self._rueda and not self._comando_rueda:
            def desplazar(e):self._rueda(e);return 'break'
            self._comando_rueda=self._root().bind_class(self._tag,'<MouseWheel>',desplazar)
            def conectar(w):
                w.bindtags((self._tag,)+tuple(t for t in w.bindtags() if t!=self._tag))
                for hijo in w.winfo_children():
                    if not isinstance(hijo,tk.Toplevel):conectar(hijo)
            conectar(self)

    def withdraw(self):self.winfo_toplevel().withdraw()
    def lift(self,*args):self.winfo_toplevel().lift()
    def attributes(self,*args):return self.winfo_toplevel().attributes(*args)
    def state(self):return self.winfo_toplevel().state()
    def geometry(self,*args):return self.winfo_toplevel().geometry(*args)

    def destroy(self):
        if not self.winfo_exists():return
        self.panel.cerrado=True
        stop=getattr(self.panel,'_stop',None)
        if stop is not None:stop.set()
        for identificador in tuple(self._temporizadores):self.after_cancel(identificador)
        if self._comando_rueda:
            self._root().unbind_class(self._tag,'<MouseWheel>')
            self._root().deletecommand(self._comando_rueda);self._comando_rueda=None
        super().destroy()


def preparar_panel(padre,titulo,panel,tamano,minimo,ocultar=None,contenedor=None):
    if contenedor is not None:
        w=ContenidoJuego(contenedor,panel)
        return w,SimpleNamespace(cuerpo=w)
    w=tk.Toplevel(padre);w.withdraw();w.title('Capri · '+titulo)
    ancho=min(tamano[0],w.winfo_screenwidth()-64);alto=min(tamano[1],w.winfo_screenheight()-80)
    w.geometry(f'{ancho}x{alto}');w.minsize(*minimo)
    marco=VentanaCyber(w,titulo.upper(),panel.cerrar,minimizar=ocultar)
    w.protocol('WM_DELETE_WINDOW',panel.cerrar)
    return w,marco
