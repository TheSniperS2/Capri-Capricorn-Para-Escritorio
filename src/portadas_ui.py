"""Portadas desde Spotify visible: selección del usuario, sin tokens ni cookies."""
import ctypes
from ctypes import wintypes as w
import os
from PIL import ImageGrab,ImageTk
from tema_ui import tk,LienzoUI
from ajustes_ui import VentanaCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui


def recortar_portada(imagen,inicio,fin):
    x1,x2=sorted((max(0,min(imagen.width,round(inicio[0]))),max(0,min(imagen.width,round(fin[0])))))
    y1,y2=sorted((max(0,min(imagen.height,round(inicio[1]))),max(0,min(imagen.height,round(fin[1])))))
    if x2-x1<16 or y2-y1<16:raise ValueError('Selecciona la portada completa.')
    return imagen.crop((x1,y1,x2,y2))


class CapturaPortada:
    def __init__(self,padre,uri,al_guardar,al_cancelar=None):
        self.root=padre._root();self.padre=padre;self.uri=uri;self.al_guardar=al_guardar
        self.al_cancelar=al_cancelar or (lambda:None);self.cerrado=False;self._tarea=None
        self.ocultas=[];self.hud=None;self.overlay=None
        grab=padre.grab_current();self.grab_anterior=grab;self.foco_anterior=padre.focus_get()
        if grab is not None:grab.grab_release()
        def ventanas(v):
            yield v
            for hijo in v.winfo_children():
                if isinstance(hijo,tk.Toplevel):yield from ventanas(hijo)
        # Guarda también los hijos antes de ocultar a sus dueños: Windows puede
        # desmapear automáticamente los diálogos transitorios al retirar al padre.
        self.ocultas=[(v,v.attributes('-alpha')) for v in ventanas(self.root) if v.winfo_viewable()]
        for v,alpha in reversed(self.ocultas):v.attributes('-alpha',0);v.withdraw()
        try:os.startfile(uri)
        except OSError:pass
        self.hud=h=tk.Toplevel(self.root);h.title(ui('Portada de Spotify'));h.geometry('430x210')
        h.minsize(430,210)
        marco=VentanaCyber(h,'SPOTIFY',cerrar=self.cancelar);f=marco.cuerpo
        tk.Label(f,text=ui('También sirve para playlists privadas.'),bg=FONDO,fg=TEXTO,
            font=(FAMILIA,12,'bold'),wraplength=370,justify='left').pack(anchor='w',padx=16,pady=(8,6))
        tk.Label(f,text=ui('Abre la playlist en Spotify. Cuando veas su portada, pulsa Capturar.'),bg=FONDO,fg=SUAVE,
            font=(FAMILIA,10),wraplength=370,justify='left').pack(anchor='w',padx=16)
        botones=tk.Frame(f,bg=FONDO);botones.pack(fill='x',padx=16,pady=12)
        BotonCyber(botones,text='Cancelar',command=self.cancelar,estilo='secundario',bg=TARJETA).pack(side='left')
        BotonCyber(botones,text='Capturar',command=self.capturar,estilo='principal',bg=ACENTO,fg=FONDO).pack(side='right')
        h.update_idletasks();alto=max(210,f.winfo_reqheight()+68);h.minsize(430,alto)
        from ventanas import area_trabajo
        l,t,r,b=area_trabajo();h.geometry(f'430x{alto}+{max(l,r-454)}+{max(t,b-alto-24)}')
        h.bind('<Destroy>',lambda e:self.cancelar() if e.widget is h and not self.cerrado else None,add='+')

    def capturar(self):
        self.hud.withdraw();self._tarea=self.root.after(150,self.seleccionar)

    def seleccionar(self):
        self._tarea=None
        if self.cerrado:return
        try:self.imagen=ImageGrab.grab(all_screens=True)
        except OSError:self.cancelar();return
        x=y=0
        if os.name=='nt':
            x=ctypes.windll.user32.GetSystemMetrics(76);y=ctypes.windll.user32.GetSystemMetrics(77)
        self.overlay=v=tk.Toplevel(self.root);v.overrideredirect(True);v.attributes('-topmost',True)
        ancho,alto=self.imagen.size;v.geometry(f'{ancho}x{alto}+0+0')
        self.canvas=c=LienzoUI(v,bg='#09060e',highlightthickness=0,cursor='crosshair');c.pack(fill='both',expand=True)
        self.foto=ImageTk.PhotoImage(self.imagen);c.create_image(0,0,anchor='nw',image=self.foto)
        c.create_rectangle(20,20,min(ancho-20,640),70,fill=FONDO,outline=ACENTO)
        c.create_text(38,45,text='Selecciona la portada · Esc para cancelar',anchor='w',fill=TEXTO,font=(FAMILIA,13,'bold'))
        self.inicio=None;self.rectangulo=None
        def pulsar(e):
            self.inicio=(e.x,e.y)
            if self.rectangulo:c.delete(self.rectangulo)
            self.rectangulo=c.create_rectangle(e.x,e.y,e.x,e.y,outline='#ffffff',width=2)
        def mover(e):
            if self.inicio:c.coords(self.rectangulo,*self.inicio,e.x,e.y)
        def soltar(e):
            if not self.inicio:return
            sx=self.imagen.width/max(1,c.winfo_width());sy=self.imagen.height/max(1,c.winfo_height())
            try:recorte=recortar_portada(self.imagen,(self.inicio[0]*sx,self.inicio[1]*sy),(e.x*sx,e.y*sy))
            except ValueError:return
            self.finalizar(recorte)
        c.bind('<ButtonPress-1>',pulsar);c.bind('<B1-Motion>',mover);c.bind('<ButtonRelease-1>',soltar)
        v.bind('<Escape>',lambda e:self.cancelar())
        v.update_idletasks()
        if os.name=='nt':
            u=ctypes.windll.user32;u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
            u.SetWindowPos.argtypes=[w.HWND,w.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,w.UINT]
            hwnd=u.GetAncestor(v.winfo_id(),2) or v.winfo_id()
            u.SetWindowPos(hwnd,None,x,y,ancho,alto,0x4|0x10)
        v.grab_set();v.focus_force()

    def finalizar(self,imagen=None):
        if self.cerrado:return
        self.cerrado=True
        if self._tarea is not None:self.root.after_cancel(self._tarea);self._tarea=None
        for v in (self.overlay,self.hud):
            try:
                if v and v.winfo_exists():v.grab_release();v.destroy()
            except tk.TclError:pass
        self.imagen=None;self.foto=None
        for v,alpha in self.ocultas:
            try:
                if v.winfo_exists():v.attributes('-alpha',alpha);v.deiconify()
            except tk.TclError:pass
        try:
            from ventanas import terminar_opaca,repintar_ventana
            for v,alpha in self.ocultas:
                if v.winfo_exists() and getattr(v,'_capri_opaca',False):terminar_opaca(v);repintar_ventana(v)
            if self.grab_anterior and self.grab_anterior.winfo_exists():
                self.grab_anterior.grab_set()
            if self.padre.winfo_exists():
                from ventanas import traer_al_frente
                traer_al_frente(self.padre)
            if self.foco_anterior and self.foco_anterior.winfo_exists():self.foco_anterior.focus_set()
        except tk.TclError:pass
        if imagen is not None:self.al_guardar(imagen)
        else:self.al_cancelar()

    def cancelar(self):self.finalizar()
