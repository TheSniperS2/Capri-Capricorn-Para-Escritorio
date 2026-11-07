"""Telemetría de Windows sin procesos externos ni dependencias adicionales."""
import ctypes as c
from ctypes import wintypes as w
import math
import re
import threading
import time


def uso_cpu(anterior, actual):
    if anterior is None:return None
    idle, kernel, user = (b-a for a,b in zip(anterior,actual))
    total=kernel+user
    return max(0.,min(100.,100*(total-idle)/total)) if total>0 else None


def uso_gpu(valores):
    # Cada proceso contribuye al mismo motor físico; no sumar motores distintos.
    motores={}
    for nombre,valor in valores:
        clave=re.search(r'luid_.+?_phys_\d+_eng_\d+',nombre)
        if clave and math.isfinite(valor):
            motores[clave[0]]=motores.get(clave[0],0)+max(0,valor)
    return min(100.,max(motores.values())) if motores else None


class Memoria(c.Structure):
    _fields_=[('length',w.DWORD),('load',w.DWORD)]+[(n,c.c_ulonglong) for n in
        ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]


class Valor(c.Structure):
    _fields_=[('status',w.DWORD),('value',c.c_double)]


class Elemento(c.Structure):
    _fields_=[('name',w.LPWSTR),('value',Valor)]


class LecturaWindows:
    def __init__(self):
        self.kernel=c.WinDLL('kernel32',use_last_error=True)
        self.kernel.GetSystemTimes.argtypes=[c.POINTER(w.FILETIME)]*3
        self.kernel.GlobalMemoryStatusEx.argtypes=[c.POINTER(Memoria)]
        self.anterior=None;self.query=w.HANDLE();self.contadores={}
        self.pdh=c.WinDLL('pdh')
        self.pdh.PdhOpenQueryW.argtypes=[w.LPCWSTR,c.c_size_t,c.POINTER(w.HANDLE)]
        self.pdh.PdhAddEnglishCounterW.argtypes=[w.HANDLE,w.LPCWSTR,c.c_size_t,c.POINTER(w.HANDLE)]
        self.pdh.PdhCollectQueryData.argtypes=[w.HANDLE]
        self.pdh.PdhCloseQuery.argtypes=[w.HANDLE]
        self.pdh.PdhGetFormattedCounterArrayW.argtypes=[w.HANDLE,w.DWORD,c.POINTER(w.DWORD),c.POINTER(w.DWORD),c.c_void_p]
        if self.pdh.PdhOpenQueryW(None,0,c.byref(self.query))==0:
            for clave,ruta in [('gpu',r'\GPU Engine(*)\Utilization Percentage'),
                               ('vram',r'\GPU Adapter Memory(*)\Dedicated Usage'),
                               ('shared',r'\GPU Adapter Memory(*)\Shared Usage')]:
                handle=w.HANDLE()
                if self.pdh.PdhAddEnglishCounterW(self.query,ruta,0,c.byref(handle))==0:self.contadores[clave]=handle

    def valores(self,clave):
        handle=self.contadores.get(clave)
        if not handle:return []
        size=w.DWORD();count=w.DWORD()
        self.pdh.PdhGetFormattedCounterArrayW(handle,0x200,c.byref(size),c.byref(count),None)
        if not size.value or size.value>16*1024*1024:return []
        buf=c.create_string_buffer(size.value)
        if self.pdh.PdhGetFormattedCounterArrayW(handle,0x200,c.byref(size),c.byref(count),buf)!=0:return []
        items=c.cast(buf,c.POINTER(Elemento))
        return [(items[i].name,items[i].value.value) for i in range(count.value)
                if items[i].value.status in (0,1) and math.isfinite(items[i].value.value)]

    def leer(self):
        datos={};times=[w.FILETIME() for _ in range(3)]
        if self.kernel.GetSystemTimes(*(c.byref(t) for t in times)):
            actual=tuple((t.dwHighDateTime<<32)|t.dwLowDateTime for t in times)
            datos['cpu']=uso_cpu(self.anterior,actual);self.anterior=actual
        memoria=Memoria();memoria.length=c.sizeof(memoria)
        if self.kernel.GlobalMemoryStatusEx(c.byref(memoria)):
            datos.update(ram=100*(memoria.total-memoria.available)/memoria.total,
                         ram_used=memoria.total-memoria.available,ram_total=memoria.total)
        if self.query and self.contadores:
            self.pdh.PdhCollectQueryData(self.query)
            datos['gpu']=uso_gpu(self.valores('gpu'))
            for clave in ('vram','shared'):
                valores=self.valores(clave)
                datos[clave]=sum(max(0,v) for _,v in valores) if valores else None
        return datos

    def cerrar(self):
        if self.query:self.pdh.PdhCloseQuery(self.query);self.query=w.HANDLE()


class MonitorPC:
    """El trabajador nunca toca Tk. Solo publica una instantánea reemplazable."""
    def __init__(self):
        self.datos={};self.activo=threading.Event();self.fin=threading.Event()
        self.hilo=None

    def activar(self,valor):
        if valor:
            self.activo.set()
            if self.hilo is None:
                self.hilo=threading.Thread(target=self._trabajar,daemon=True,name='Capri-monitor')
                self.hilo.start()
        else:self.activo.clear()

    def _trabajar(self):
        lector=None
        try:
            lector=LecturaWindows()
            calentando=True
            while not self.fin.is_set():
                if not self.activo.is_set():
                    lector.anterior=None
                    calentando=True
                    self.fin.wait(.25);continue
                try:self.datos={**lector.leer(),'fecha':time.monotonic()}
                except (OSError,ValueError):self.datos={}
                self.fin.wait(.25 if calentando else 2)
                calentando=False
        except (OSError,AttributeError):self.datos={}
        finally:
            if lector:lector.cerrar()

    def cerrar(self):self.activo.clear();self.fin.set()
