"""Ocultar Capri conservando voz y controles; recuperar solo el avatar."""
from tema_ui import tk

class VisibilidadCapri:
    def __init__(self,root,antes_ocultar=None,al_mostrar=None):
        self.root=root;self.oculta=False;self._cambiando=False
        self.antes_ocultar=antes_ocultar or (lambda:None);self.al_mostrar=al_mostrar or (lambda:None)
        root.bind_all('<Map>',self._mapear,add='+')

    def ventanas(self):
        def recorrer(widget):
            for hijo in widget.winfo_children():
                if isinstance(hijo,tk.Toplevel):yield hijo
                yield from recorrer(hijo)
        return [self.root,*recorrer(self.root)]

    def ocultar(self):
        if self.oculta:return
        self._cerrar_temporales()
        self.antes_ocultar();self.oculta=True;self._cambiando=True
        captura=self.root.grab_current()
        if captura:captura.grab_release()
        for v in self.ventanas():
            try:
                if v.state() in ('normal','zoomed'):
                    v.withdraw()
            except tk.TclError:pass
        # Mantener el mismo marco/HWND: cambiar overrideredirect para iconificar
        # reconstruía la ventana raíz mientras sus paneles seguían existiendo.
        self.root.withdraw()
        self.root.after_idle(self._fin_cambio)

    def _fin_cambio(self):self._cambiando=False

    def mostrar(self):
        self._cerrar_temporales()
        if self.oculta:
            self.oculta=False;self._cambiando=True
            try:
                self.root.deiconify()
            finally:self._cambiando=False
        else:self.root.deiconify()
        self.al_mostrar()

    def _cerrar_temporales(self):
        # Los desplegables no son paneles: no deben sobrevivir a una recuperación
        # de ventanas ni conservar la captura de ratón detrás de otra ventana.
        for v in self.ventanas():
            cerrar=getattr(v,'_capri_cerrar_temporal',None)
            if cerrar:
                try:cerrar()
                except tk.TclError:pass

    def alternar(self):
        from ventanas import primer_plano_propio
        if self.oculta or not primer_plano_propio():self.mostrar()
        else:self.ocultar()

    def _mapear(self,e):
        if not self.oculta or self._cambiando:return
        if e.widget==self.root:
            if self.root.state()!='withdrawn':self.mostrar()
        elif isinstance(e.widget,tk.Toplevel):
            try:e.widget.withdraw()
            except tk.TclError:pass
