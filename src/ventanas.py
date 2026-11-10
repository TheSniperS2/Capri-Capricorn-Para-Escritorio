"""Ventanas visibles de Windows, sin inspeccionar contenido ni capturar pantalla."""
import os
import ctypes
from ctypes import wintypes as w
APOYOS_PROPIOS=set()


def hwnd_propio(ventana):
    if os.name!='nt':return None
    u=ctypes.windll.user32
    u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
    return u.GetAncestor(w.HWND(ventana.winfo_toplevel().winfo_id()),2) or ventana.winfo_toplevel().winfo_id()


def recortar_marco(ventana,puntos):
    """Contorno nativo sin hacer transparente el fondo de todos los controles Tk."""
    if os.name!='nt':return False
    puntos=tuple(round(n) for n in puntos)
    if getattr(ventana,'_capri_contorno',None)==puntos:return True
    u=ctypes.windll.user32;g=ctypes.windll.gdi32
    g.CreatePolygonRgn.argtypes=[ctypes.POINTER(w.POINT),ctypes.c_int,ctypes.c_int];g.CreatePolygonRgn.restype=w.HRGN
    g.DeleteObject.argtypes=[w.HGDIOBJ];g.DeleteObject.restype=w.BOOL
    u.SetWindowRgn.argtypes=[w.HWND,w.HRGN,w.BOOL];u.SetWindowRgn.restype=ctypes.c_int
    vertices=(w.POINT*(len(puntos)//2))(*(w.POINT(*puntos[i:i+2]) for i in range(0,len(puntos),2)))
    region=g.CreatePolygonRgn(vertices,len(vertices),2)
    if not region:return False
    if not u.SetWindowRgn(hwnd_propio(ventana),region,False):g.DeleteObject(region);return False
    # Tras SetWindowRgn, Windows es dueño del HRGN y lo libera al reemplazarlo.
    ventana._capri_contorno=puntos;return True


def repintar_ventana(ventana):
    """Actualiza el layout y expone los controles Tk, no solo el HWND exterior."""
    if not ventana.winfo_exists():return
    # Primero resuelve el reflujo: pintar con posiciones antiguas deja copias
    # de etiquetas/campos cuando el marco cambia continuamente de tamaño.
    ventana.update_idletasks()
    def visibles(widget,limites=None):
        if not widget.winfo_viewable():return
        x,y=widget.winfo_rootx(),widget.winfo_rooty();ancho,alto=widget.winfo_width(),widget.winfo_height()
        rect=(x,y,x+ancho,y+alto)
        clip=rect if limites is None else (max(x,limites[0]),max(y,limites[1]),min(x+ancho,limites[2]),min(y+alto,limites[3]))
        if clip[0]>=clip[2] or clip[1]>=clip[3]:return
        yield widget
        for hijo in widget.winfo_children():
            if hijo.winfo_toplevel() is ventana:yield from visibles(hijo,clip)
    for widget in visibles(ventana):
        # También los controles cuya geometría no cambió necesitan renovar
        # su superficie. Invalidar solo el marco HWND no refresca el dibujo Tk.
        widget.event_generate('<Expose>',x=0,y=0,width=widget.winfo_width(),height=widget.winfo_height())
    ventana.update_idletasks()


def preparar_presentacion(ventana):
    """Resuelve layout y eventos nativos sin ejecutar temporizadores ajenos."""
    from _tkinter import WINDOW_EVENTS,DONT_WAIT
    # update() también ejecutaría animación/poll durante la apertura. El
    # repintado posterior resolverá el reflujo generado por Configure/Map.
    if not ventana.winfo_exists():return
    ventana.update_idletasks()
    for _ in range(4096):
        if not ventana.tk.dooneevent(WINDOW_EVENTS|DONT_WAIT):break


def terminar_opaca(ventana):
    if os.name!='nt' or not getattr(ventana,'_capri_opaca',False):return
    if float(ventana.attributes('-alpha'))<1:return
    u=ctypes.windll.user32;hwnd=hwnd_propio(ventana)
    u.GetWindowLongPtrW.argtypes=[w.HWND,ctypes.c_int];u.GetWindowLongPtrW.restype=ctypes.c_ssize_t
    u.SetWindowLongPtrW.argtypes=[w.HWND,ctypes.c_int,ctypes.c_ssize_t];u.SetWindowLongPtrW.restype=ctypes.c_ssize_t
    estilo=u.GetWindowLongPtrW(hwnd,-20)
    if estilo&0x80000:u.SetWindowLongPtrW(hwnd,-20,estilo&~0x80000)


def ocultar_para_preparar(ventana):
    ventana.attributes('-alpha',0)
    if os.name!='nt':return
    u=ctypes.windll.user32;hwnd=hwnd_propio(ventana)
    u.GetWindowLongPtrW.argtypes=[w.HWND,ctypes.c_int];u.GetWindowLongPtrW.restype=ctypes.c_ssize_t
    u.SetWindowLongPtrW.argtypes=[w.HWND,ctypes.c_int,ctypes.c_ssize_t];u.SetWindowLongPtrW.restype=ctypes.c_ssize_t
    u.SetLayeredWindowAttributes.argtypes=[w.HWND,w.COLORREF,w.BYTE,w.DWORD];u.SetLayeredWindowAttributes.restype=w.BOOL
    # Tk conserva su estilo anterior en caché. Asegura el bit nativo al volver
    # a preparar una ventana que ya terminó opaca mediante terminar_opaca.
    u.SetWindowLongPtrW(hwnd,-20,u.GetWindowLongPtrW(hwnd,-20)|0x80000)
    u.SetLayeredWindowAttributes(hwnd,0,0,2)


def registrar_apoyo(ventana):
    if os.name!='nt':return
    ventana.update_idletasks();u=ctypes.windll.user32
    u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
    hwnd=int(u.GetAncestor(w.HWND(ventana.winfo_id()),2) or ventana.winfo_id())
    APOYOS_PROPIOS.add(hwnd)
    def retirar(evento):
        if evento.widget==ventana:APOYOS_PROPIOS.discard(hwnd)
    ventana.bind('<Destroy>',retirar,add='+')
    return hwnd

def primer_plano_propio():
    if os.name!='nt':return False
    u=ctypes.windll.user32;u.GetForegroundWindow.restype=w.HWND
    hwnd=u.GetForegroundWindow();pid=w.DWORD()
    if not hwnd:return False
    u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
    u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    return pid.value==os.getpid()

def traer_al_frente(ventana):
    """Petición explícita del usuario: solo restaura y activa una ventana propia."""
    ventana.deiconify();ventana.attributes('-topmost',True);ventana.lift();ventana.update_idletasks()
    if os.name!='nt':ventana.focus_set();return True
    u=ctypes.windll.user32
    u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
    hwnd=u.GetAncestor(w.HWND(ventana.winfo_id()),2) or ventana.winfo_id()
    pid=w.DWORD();u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
    u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    if pid.value!=os.getpid():return False
    u.ShowWindow.argtypes=[w.HWND,ctypes.c_int];u.SetForegroundWindow.argtypes=[w.HWND]
    u.ShowWindow(hwnd,9)
    return bool(u.SetForegroundWindow(hwnd))

def preparar_no_activar(ventana):
    """Windows no debe activar este aviso ni añadirlo a Alt+Tab."""
    if os.name!='nt':return None
    ventana.update_idletasks();u=ctypes.windll.user32
    u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
    hwnd=u.GetAncestor(w.HWND(ventana.winfo_id()),2) or ventana.winfo_id()
    get=u.GetWindowLongPtrW;set_=u.SetWindowLongPtrW
    get.argtypes=[w.HWND,ctypes.c_int];get.restype=ctypes.c_ssize_t
    set_.argtypes=[w.HWND,ctypes.c_int,ctypes.c_ssize_t];set_.restype=ctypes.c_ssize_t
    set_(hwnd,-20,(get(hwnd,-20)|0x08000000|0x80)&~0x40000)
    return hwnd


def mostrar_no_activar(ventana):
    hwnd=preparar_no_activar(ventana);ventana.deiconify()
    if hwnd and ventana.state()!='withdrawn':
        u=ctypes.windll.user32;u.ShowWindow.argtypes=[w.HWND,ctypes.c_int]
        u.SetWindowPos.argtypes=[w.HWND,w.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,w.UINT]
        u.ShowWindow(hwnd,4)
        u.SetWindowPos(hwnd,w.HWND(-1),0,0,0,0,0x0010|0x0001|0x0002|0x0040)


def area_trabajo():
    if os.name!='nt':return (0,0,1920,1040)
    rect=w.RECT()
    if ctypes.windll.user32.SystemParametersInfoW(0x30,0,ctypes.byref(rect),0):
        return (rect.left,rect.top,rect.right,rect.bottom)
    return (0,0,ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))


def apoyo_propio_permitido(titulo):
    return titulo.startswith(('Capri · Ajustes','Capri · Aspectos','Capri // Aspectos','Capri · Color','Capri · Conversación','Capri · Playlists','Capri · YouTube','Conectar YouTube con Opera'))


def visibles(incluir_propias=False):
    if os.name!='nt':return []
    u=ctypes.windll.user32;salida=[]
    u.IsWindowVisible.argtypes=[w.HWND];u.IsIconic.argtypes=[w.HWND]
    u.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
    u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
    u.GetWindowTextLengthW.argtypes=[w.HWND];u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
    u.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
    callback=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
    def ver(hwnd,param):
        if not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd):return True
        pid=w.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        propia=pid.value==os.getpid()
        if propia and not incluir_propias:return True
        clase=ctypes.create_unicode_buffer(256);u.GetClassNameW(hwnd,clase,256)
        if clase.value in ('Progman','WorkerW','Shell_TrayWnd','Shell_SecondaryTrayWnd'):return True
        oculto=w.DWORD()
        if ctypes.windll.dwmapi.DwmGetWindowAttribute(w.HWND(hwnd),14,ctypes.byref(oculto),4)==0 and oculto.value:return True
        r=w.RECT()
        if not u.GetWindowRect(hwnd,ctypes.byref(r)) or r.right-r.left<180 or r.bottom-r.top<100:return True
        n=u.GetWindowTextLengthW(hwnd);texto=ctypes.create_unicode_buffer(n+1);u.GetWindowTextW(hwnd,texto,n+1)
        if propia and int(hwnd) not in APOYOS_PROPIOS and not apoyo_propio_permitido(texto.value):return True
        if texto.value:salida.append({'id':int(hwnd),'titulo':texto.value,'rect':(r.left,r.top,r.right,r.bottom)})
        return True
    cb=callback(ver);u.EnumWindows.argtypes=[callback,w.LPARAM];u.EnumWindows(cb,0)
    return salida


def controlar(accion,ventana):
    if os.name!='nt':raise OSError('Este control necesita Windows.')
    u=ctypes.windll.user32;hwnd=w.HWND(ventana['id'])
    if not u.IsWindow(hwnd):raise OSError('Esa ventana ya no está abierta.')
    if accion=='ventana_cerrar':
        u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
        if not u.PostMessageW(hwnd,0x10,0,0):raise OSError('Windows no permitió cerrar la ventana.')
        return 'Envié la solicitud de cierre a «'+ventana['titulo']+'». La aplicación puede pedir guardar cambios.'
    u.ShowWindow.argtypes=[w.HWND,ctypes.c_int]
    u.ShowWindow(hwnd,6 if accion=='ventana_minimizar' else 3)
    return ('Minimicé' if accion=='ventana_minimizar' else 'Maximicé')+' «'+ventana['titulo']+'».'


def activa():
    if os.name!='nt':return None
    u=ctypes.windll.user32;u.GetForegroundWindow.restype=w.HWND
    hwnd=int(u.GetForegroundWindow() or 0)
    ventana=next((v for v in visibles() if v['id']==hwnd),None)
    if ventana:
        pid=w.DWORD();u.GetWindowThreadProcessId(w.HWND(hwnd),ctypes.byref(pid));ventana['pid']=pid.value
    return ventana


def minimizar_travesura(ventana):
    actual=activa()
    if not actual or actual['id']!=ventana['id']:return False
    controlar('ventana_minimizar',actual)
    u=ctypes.windll.user32;u.IsIconic.argtypes=[w.HWND]
    return bool(u.IsIconic(w.HWND(ventana['id'])))


def restaurar_travesura(ventana,activar=True):
    if os.name!='nt':return
    u=ctypes.windll.user32;u.IsWindow.argtypes=[w.HWND];u.IsIconic.argtypes=[w.HWND]
    hwnd=w.HWND(ventana['id'])
    if u.IsWindow(hwnd) and u.IsIconic(hwnd):
        pid=w.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if ventana.get('pid') is not None and pid.value!=ventana['pid']:return
        u.ShowWindow.argtypes=[w.HWND,ctypes.c_int];u.ShowWindow(hwnd,9 if activar else 4)
