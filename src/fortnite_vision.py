"""Lectura local del lobby con OCR de Windows y entradas normales de ratón.

No lee credenciales, memoria del juego ni servicios privados. Las capturas son
temporales, se procesan en este equipo y se eliminan incluso si falla el OCR.
"""
import base64
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from fortnite import ErrorFortnite,Pantalla,Texto

OCR=r'''
$ErrorActionPreference='Stop'
[Console]::InputEncoding=New-Object Text.UTF8Encoding($false)
[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'} | Select-Object -First 1)
function Await($operation,$type) {
 $task=$asTask.MakeGenericMethod($type).Invoke($null,@($operation))
 if(-not $task.Wait(4500)){throw 'OCR timeout'}
 return $task.Result
}
$file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync([Console]::In.ReadLine())) ([Windows.Storage.StorageFile])
$stream=Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
try {
 $decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
 $bitmap=Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
 try {
  $engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
  if($null -eq $engine){throw 'No OCR language'}
  $result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  $lines=@(foreach($line in $result.Lines){
   $left=1e9;$top=1e9;$right=0;$bottom=0
   foreach($word in $line.Words){$r=$word.BoundingRect;$left=[Math]::Min($left,$r.X);$top=[Math]::Min($top,$r.Y);$right=[Math]::Max($right,$r.X+$r.Width);$bottom=[Math]::Max($bottom,$r.Y+$r.Height)}
   if($line.Words.Count){@{text=$line.Text;rect=@($left,$top,($right-$left),($bottom-$top))}}
  })
  ConvertTo-Json -InputObject $lines -Depth 4 -Compress
 } finally {$bitmap.Dispose()}
} finally {$stream.Dispose()}
'''


def leer_imagen(ruta):
    codigo=base64.b64encode(OCR.encode('utf-16-le')).decode('ascii')
    try:
        r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',codigo],
            input=str(Path(ruta).resolve())+'\n',capture_output=True,encoding='utf-8',errors='replace',
            timeout=9,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if r.returncode:raise ErrorFortnite('No pude usar el reconocimiento de texto de Windows para leer Fortnite.')
        datos=json.loads(r.stdout.lstrip('\ufeff'))
        return tuple(Texto(d['text'],tuple(d['rect'])) for d in datos)
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        raise ErrorFortnite('No pude leer los controles de Fortnite con el reconocimiento de Windows.') from e




def botones_equipo(imagen,textos):
    """Cuatro cuadrados de siluetas junto a la etiqueta observada del equipo."""
    ancho,alto=imagen.size
    anclas=[t for t in textos if t.texto.casefold() in ('tamaño del equipo','team size','tamanho da equipe')
            and t.rect[0]>ancho*.55]
    if len(anclas)!=1:return ()
    a=anclas[0];l,y,w,h=a.rect;pix=imagen.convert('RGB').load()
    for fila in range(int(y+h+.013*alto),min(alto,int(y+h+.035*alto)),2):
        bandas=[];inicio=int(l+w+10);x=inicio
        while x<ancho*.96:
            color=pix[x,fila];izq=x;x+=1
            while x<ancho*.96 and pix[x,fila]==color:x+=1
            lado=x-izq
            if not ancho*.025<=lado<=ancho*.055:continue
            arriba=abajo=fila
            while arriba>0 and fila-arriba<lado*1.4 and pix[izq+2,arriba-1]==color:arriba-=1
            while abajo<alto-1 and abajo-fila<lado*1.4 and pix[izq+2,abajo+1]==color:abajo+=1
            altura=abajo-arriba+1
            if not .83*lado<=altura<=1.2*lado:continue
            # Una silueta blanca dentro del cuadrado, sobre fondo saturado.
            blancos=sum(1 for xx in range(izq+lado//5,izq+lado*4//5,2)
                for yy in range(arriba+altura//5,arriba+altura*4//5,2) if min(pix[xx,yy])>220)
            if not lado*altura*.003<blancos<lado*altura*.10:continue
            bandas.append((izq,arriba,lado,altura))
        if len(bandas)!=4:continue
        largos=[b[2] for b in bandas]
        if max(largos)>min(largos)*1.2:continue
        huecos=[bandas[i+1][0]-(bandas[i][0]+bandas[i][2]) for i in range(3)]
        if not all(3<h<min(largos)*.65 for h in huecos):continue
        return tuple(Texto(k,r) for k,r in zip(('solo','duo','trio','squad'),bandas))
    return ()


class VistaFortnite:
    NOMBRES={'fortniteclient-win64-shipping.exe'}
    def __init__(self):
        if os.name!='nt':raise ErrorFortnite('El control de Fortnite necesita Windows.')
        import win32gui,win32api,win32process,win32con,pywintypes
        self.g=win32gui;self.a=win32api;self.p=win32process;self.c=win32con
        self.error=pywintypes.error

    def _es_fortnite(self,hwnd):
        try:
            pid=self.p.GetWindowThreadProcessId(hwnd)[1]
            h=self.a.OpenProcess(0x1000,False,pid)
            try:
                k=ctypes.windll.kernel32;k.QueryFullProcessImageNameW.argtypes=[w.HANDLE,w.DWORD,w.LPWSTR,ctypes.POINTER(w.DWORD)]
                ruta=ctypes.create_unicode_buffer(32768);n=w.DWORD(len(ruta))
                return bool(k.QueryFullProcessImageNameW(w.HANDLE(int(h)),0,ruta,ctypes.byref(n)) and Path(ruta.value).name.casefold() in self.NOMBRES)
            finally:h.Close()
        except (OSError,self.error):return False

    def _ventana(self):
        ventanas=[]
        self.g.EnumWindows(lambda h,_:ventanas.append(h) if self.g.IsWindowVisible(h) and self._es_fortnite(h) else None,None)
        if len(ventanas)!=1:raise ErrorFortnite('Abre Fortnite y deja el lobby preparado para conectar con Capri.')
        return ventanas[0]

    def _rect(self,h):
        l,t,r,b=self.g.GetClientRect(h);x,y=self.g.ClientToScreen(h,(l,t));d,f=self.g.ClientToScreen(h,(r,b))
        return (x,y,d,f)

    def _validar(self,h,rect=None):
        try:
            if not self.g.IsWindow(h) or not self._es_fortnite(h) or self.g.GetForegroundWindow()!=h or self.g.IsIconic(h):
                raise ErrorFortnite('Fortnite perdió el foco. Vuelve al lobby y pide la acción otra vez.')
            if rect is not None and self._rect(h)!=rect:raise ErrorFortnite('La ventana de Fortnite cambió de tamaño o posición. Vuelve a intentarlo.')
        except self.error as e:raise ErrorFortnite('La ventana de Fortnite dejó de estar disponible.') from e

    def _mostrar_restaurada(self,h):
        # La restauración pertenece al hilo del juego y puede tardar. No bloquear
        # el hilo de la orden esperando a que ShowWindow atienda sus mensajes.
        mostrar=ctypes.windll.user32.ShowWindowAsync
        mostrar.argtypes=[w.HWND,ctypes.c_int];mostrar.restype=w.BOOL
        if not mostrar(w.HWND(h),self.c.SW_RESTORE):
            raise ErrorFortnite('Windows no pudo restaurar Fortnite. Abre el juego y vuelve a pedir la acción.')

    def _activar(self,h):
        """Restaurar una sola vez y esperar confirmación real, sin teclas falsas."""
        try:
            if not self.g.IsWindow(h) or not self._es_fortnite(h):
                raise ErrorFortnite('La ventana de Fortnite dejó de estar disponible.')
            minimizada=bool(self.g.IsIconic(h));cambiada=minimizada or self.g.GetForegroundWindow()!=h
            if minimizada:
                self._mostrar_restaurada(h);limite=time.monotonic()+6
                while self.g.IsIconic(h):
                    if not self.g.IsWindow(h):raise ErrorFortnite('Fortnite se cerró al intentar restaurarlo.')
                    if time.monotonic()>=limite:raise ErrorFortnite('Fortnite sigue minimizado. No pude restaurar su ventana.')
                    time.sleep(.05)
            if self.g.GetForegroundWindow()!=h:
                try:self.g.SetForegroundWindow(h)
                except (OSError,self.error):
                    # Windows puede informar un error aunque el cambio esté
                    # terminando. Solo la consulta posterior confirma el foco.
                    pass
                limite=time.monotonic()+2
                while self.g.GetForegroundWindow()!=h:
                    if not self.g.IsWindow(h) or time.monotonic()>=limite:
                        raise ErrorFortnite('Windows no permitió activar Fortnite. Abre el lobby y vuelve a pedirlo.')
                    time.sleep(.05)
            self._validar(h)
            return cambiada
        except (OSError,self.error) as e:raise ErrorFortnite('No pude recuperar la ventana de Fortnite.') from e

    def _imagen(self,h,esperar=False):
        from PIL import ImageGrab,ImageStat
        limite=time.monotonic()+(4 if esperar else 0)
        while True:
            self._validar(h);rect=self._rect(h)
            if rect[2]-rect[0]>=640 and rect[3]-rect[1]>=360:
                inicio=time.monotonic();imagen=ImageGrab.grab(bbox=rect,all_screens=True)
                self._validar(h)
                if self._rect(h)==rect and max(ImageStat.Stat(imagen).stddev)>=3:return imagen,rect,inicio
            if time.monotonic()>=limite:
                raise ErrorFortnite('Fortnite todavía no muestra una imagen del lobby que pueda leer. Vuelve a pedir la acción cuando termine de abrirse.')
            time.sleep(.1)

    def capturar(self,activar=False):
        h=self._ventana()
        recuperada=self._activar(h) if activar else False
        imagen,rect,inicio=self._imagen(h,esperar=recuperada)
        with tempfile.TemporaryDirectory(prefix='capri-fortnite-') as temporal:
            ruta=Path(temporal)/'lobby.png';imagen.save(ruta);textos=leer_imagen(ruta)
        self._validar(h,rect)
        return Pantalla(h,rect,textos,inicio,botones_equipo(imagen,textos))



    def pulsar(self,p,t):
        self._validar(p.ventana,p.rect)
        if t not in (*p.textos,*p.equipos) or time.monotonic()-p.momento>5:raise ErrorFortnite('La lectura de Fortnite quedó desactualizada. Vuelve a pedir la acción.')
        l,a,an,al=t.rect;x=p.rect[0]+int(l+an/2);y=p.rect[1]+int(a+al/2)
        if not(p.rect[0]<=x<p.rect[2] and p.rect[1]<=y<p.rect[3]):raise ErrorFortnite('El control no está dentro de Fortnite.')
        self.a.SetCursorPos((x,y));self._validar(p.ventana,p.rect)
        if self.g.GetAncestor(self.g.WindowFromPoint((x,y)),2)!=p.ventana:
            raise ErrorFortnite('Otra ventana tapa ese control de Fortnite. Despéjalo y vuelve a intentarlo.')
        self.a.mouse_event(self.c.MOUSEEVENTF_LEFTDOWN,0,0);self.a.mouse_event(self.c.MOUSEEVENTF_LEFTUP,0,0)

    def volver(self,p):
        self._validar(p.ventana,p.rect)
        self.a.keybd_event(self.c.VK_ESCAPE,0,0,0);self.a.keybd_event(self.c.VK_ESCAPE,0,self.c.KEYEVENTF_KEYUP,0)
