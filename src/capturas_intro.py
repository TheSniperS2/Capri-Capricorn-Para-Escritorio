"""Detecta Recortes durante las animaciones; no captura imágenes ni guarda teclas."""
import os
import ctypes
from ctypes import wintypes as w
from pathlib import PureWindowsPath

_procesos={}

def proceso_de_recortes(pid):
    if not pid:return False
    if pid in _procesos:return _procesos[pid]
    k=ctypes.windll.kernel32
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    handle=k.OpenProcess(0x1000,False,pid)
    if not handle:return False
    try:
        ruta=ctypes.create_unicode_buffer(32768);longitud=w.DWORD(len(ruta))
        k.QueryFullProcessImageNameW.argtypes=[w.HANDLE,w.DWORD,w.LPWSTR,ctypes.POINTER(w.DWORD)]
        if not k.QueryFullProcessImageNameW(handle,0,ruta,ctypes.byref(longitud)):return False
        resultado=PureWindowsPath(ruta.value).name.casefold() in {
            'screenclippinghost.exe','snippingtool.exe','screensketch.exe'}
        if len(_procesos)>=8:_procesos.pop(next(iter(_procesos)))
        _procesos[pid]=resultado
        return resultado
    finally:
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(handle)


def captura_solicitada():
    """Sólo observa Impr Pant / Win+Shift+S y el ejecutable en primer plano."""
    if os.name!='nt':return False
    try:
        u=ctypes.windll.user32
        u.GetAsyncKeyState.argtypes=[ctypes.c_int];u.GetAsyncKeyState.restype=ctypes.c_short
        pulsada=lambda tecla:bool(u.GetAsyncKeyState(tecla)&0x8000)
        if pulsada(0x2c) or ((pulsada(0x5b) or pulsada(0x5c)) and pulsada(0x10) and pulsada(0x53)):
            return True
        u.GetForegroundWindow.restype=w.HWND;hwnd=u.GetForegroundWindow()
        if not hwnd:return False
        pid=w.DWORD();u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
        u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        return proceso_de_recortes(pid.value)
    except (AttributeError,OSError,ValueError):return False
