"""Componentes locales para orientar cambios; sin procesos externos ni envíos."""
import ctypes as c
from ctypes import wintypes as w
import os
import uuid


class GUID(c.Structure):
    _fields_=[('a',c.c_uint32),('b',c.c_uint16),('d',c.c_uint16),('e',c.c_ubyte*8)]


class DescripcionGPU(c.Structure):
    _fields_=[('nombre',w.WCHAR*128),('vendor',w.UINT),('device',w.UINT),
              ('subsystem',w.UINT),('revision',w.UINT),('dedicada',c.c_size_t),
              ('sistema',c.c_size_t),('compartida',c.c_size_t),
              ('luid_bajo',w.DWORD),('luid_alto',w.LONG),('flags',w.UINT)]


def _metodo(objeto,indice,retorno,*argumentos):
    tabla=c.cast(objeto,c.POINTER(c.POINTER(c.c_void_p))).contents
    return c.WINFUNCTYPE(retorno,c.c_void_p,*argumentos)(tabla[indice])


def graficas():
    """DXGI usa SIZE_T: no trunca a 4 GB como Win32_VideoController.AdapterRAM."""
    if os.name!='nt':return []
    fabrica=c.c_void_p();salida=[]
    try:
        dxgi=c.WinDLL('dxgi')
        crear=dxgi.CreateDXGIFactory1;crear.argtypes=[c.POINTER(GUID),c.POINTER(c.c_void_p)];crear.restype=c.c_long
        guid=GUID.from_buffer_copy(uuid.UUID('770aae78-f26f-4dba-a829-253c83d1b387').bytes_le)
        if crear(c.byref(guid),c.byref(fabrica))<0:return []
        enumerar=_metodo(fabrica,12,c.c_long,w.UINT,c.POINTER(c.c_void_p))
        for i in range(16):
            adaptador=c.c_void_p()
            if enumerar(fabrica,i,c.byref(adaptador))<0:break
            try:
                detalle=DescripcionGPU()
                if _metodo(adaptador,10,c.c_long,c.POINTER(DescripcionGPU))(adaptador,c.byref(detalle))>=0 and not detalle.flags&2:
                    salida.append({'nombre':detalle.nombre.strip(),'dedicada':int(detalle.dedicada)})
            finally:_metodo(adaptador,2,w.ULONG)(adaptador)
    except (OSError,AttributeError,ValueError):pass
    finally:
        if fabrica.value:_metodo(fabrica,2,w.ULONG)(fabrica)
    return salida


def leer_equipo():
    datos={'cpu':'','hilos':os.cpu_count(),'ram_total':None,'ram_libre':None,'gpus':[]}
    if os.name!='nt':return datos
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as clave:
            datos['cpu']=' '.join(winreg.QueryValueEx(clave,'ProcessorNameString')[0].split())
    except OSError:pass
    try:
        from monitor_pc import Memoria
        memoria=Memoria();memoria.length=c.sizeof(memoria)
        kernel=c.WinDLL('kernel32');kernel.GlobalMemoryStatusEx.argtypes=[c.POINTER(Memoria)]
        if kernel.GlobalMemoryStatusEx(c.byref(memoria)):
            datos.update(ram_total=int(memoria.total),ram_libre=int(memoria.available))
    except (OSError,AttributeError):pass
    datos['gpus']=graficas()
    return datos
