"""Una sola Capri por sesión; abrirla de nuevo solicita mostrar la existente."""
import os

class InstanciaCapri:
    def __init__(self,nombre='Local\\CapriDesktopCompanion1'):
        self.mutex=None;self.evento=None;self.primera=True;self.k=None
        if os.name!='nt':return
        import ctypes
        from ctypes import wintypes as w
        self.k=k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.CreateEventW.argtypes=[ctypes.c_void_p,w.BOOL,w.BOOL,w.LPCWSTR];k.CreateEventW.restype=w.HANDLE
        k.CreateMutexW.argtypes=[ctypes.c_void_p,w.BOOL,w.LPCWSTR];k.CreateMutexW.restype=w.HANDLE
        k.SetEvent.argtypes=[w.HANDLE];k.SetEvent.restype=w.BOOL
        k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];k.WaitForSingleObject.restype=w.DWORD
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
        # Crear primero el evento conserva peticiones incluso durante el arranque.
        self.evento=k.CreateEventW(None,False,False,nombre+'.Mostrar')
        if not self.evento:raise ctypes.WinError(ctypes.get_last_error())
        self.mutex=k.CreateMutexW(None,False,nombre)
        error=ctypes.get_last_error()
        if not self.mutex:
            self.cerrar();raise ctypes.WinError(error)
        self.primera=error!=183
    def solicitar_mostrar(self):return bool(self.evento and self.k.SetEvent(self.evento))
    def recibir(self):return bool(self.evento and self.k.WaitForSingleObject(self.evento,0)==0)
    def cerrar(self):
        for atributo in ('mutex','evento'):
            h=getattr(self,atributo)
            if h:self.k.CloseHandle(h);setattr(self,atributo,None)
    def __enter__(self):return self
    def __exit__(self,*a):self.cerrar()
