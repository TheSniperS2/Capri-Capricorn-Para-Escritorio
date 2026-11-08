"""Lectura opcional del centro del cliente Roblox. No activa ventanas ni envía entradas."""
import ctypes
from ctypes import wintypes as w
import os
from pathlib import Path
import tempfile
import re,time

NOMBRES={'robloxplayerbeta.exe','robloxplayer.exe'}

def ventana():
    if os.name!='nt':return None
    u=ctypes.windll.user32;k=ctypes.windll.kernel32
    u.GetForegroundWindow.restype=w.HWND;h=u.GetForegroundWindow()
    u.IsIconic.argtypes=[w.HWND]
    if not h or u.IsIconic(h):return None
    pid=w.DWORD();u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)];u.GetWindowThreadProcessId(h,ctypes.byref(pid))
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    p=k.OpenProcess(0x1000,False,pid.value)
    if not p:return None
    try:
        ruta=ctypes.create_unicode_buffer(32768);n=w.DWORD(len(ruta))
        k.QueryFullProcessImageNameW.argtypes=[w.HANDLE,w.DWORD,w.LPWSTR,ctypes.POINTER(w.DWORD)]
        if not k.QueryFullProcessImageNameW(p,0,ruta,ctypes.byref(n)) or Path(ruta.value).name.casefold() not in NOMBRES:return None
    finally:
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(p)
    r=w.RECT();u.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
    if not u.GetWindowRect(h,ctypes.byref(r)):return None
    return h,(r.left,r.top,r.right,r.bottom)

def en_primer_plano():
    try:return ventana() is not None
    except OSError:return False

def lugar_actual(carpeta=None,ahora=None):
    """Solo extrae el ID del último ingreso del registro reciente del cliente local."""
    if not en_primer_plano():return None
    carpeta=Path(carpeta) if carpeta is not None else Path(os.environ.get('LOCALAPPDATA',''))/'Roblox/logs'
    ahora=time.time() if ahora is None else ahora
    try:
        archivos=sorted(carpeta.glob('*_Player_*.log'),key=lambda p:p.stat().st_mtime,reverse=True)
        if not archivos or ahora-archivos[0].stat().st_mtime>28800:return None
        with archivos[0].open('rb') as f:
            f.seek(max(0,f.seek(0,2)-131072));trozo=f.read(131072).decode('utf8',errors='ignore')
        patron=r'(?:Joining game[^\r\n]{0,120}?\bplace\s+|\bplaceId["\s:=]+)([1-9]\d{0,18})(?!\d)'
        ids=re.findall(patron,trozo,flags=re.I)
        return ids[-1] if ids else None
    except OSError:return None

def leer_centro():
    v=ventana()
    if not v:return None
    h,rect=v;l,t,r,b=rect;ancho=r-l;alto=b-t
    if ancho<640 or alto<360:return None
    from PIL import ImageGrab
    from fortnite_vision import leer_imagen
    from fortnite import ErrorFortnite
    # Excluir esquinas, chat lateral y barras habituales. Nunca se usa una captura de todo el escritorio.
    caja=(l+round(ancho*.20),t+round(alto*.12),l+round(ancho*.80),t+round(alto*.72))
    imagen=ImageGrab.grab(bbox=caja,all_screens=True)
    if ventana()!=v:return None
    with tempfile.TemporaryDirectory(prefix='capri-roblox-') as tmp:
        ruta=Path(tmp)/'centro.png';imagen.save(ruta)
        try:textos=leer_imagen(ruta)
        except ErrorFortnite as e:raise OSError('No pude leer el centro de Roblox.') from e
    if ventana()!=v:return None
    return [x.texto for x in textos]
