"""OCR local reutilizable para fichas. Un proceso oculto, sin red ni historial."""
import base64,json,os,queue,subprocess,threading
from pathlib import Path
from fortnite import ErrorFortnite,Texto

CODIGO=r'''
$ErrorActionPreference='Stop'
[Console]::InputEncoding=[Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'} | Select-Object -First 1)
function Await($operation,$type) {
 $task=$asTask.MakeGenericMethod($type).Invoke($null,@($operation))
 if(-not $task.Wait(4000)){throw 'OCR timeout'}
 return $task.Result
}
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if($null -eq $engine){throw 'No OCR language'}
while($null -ne ($ruta=[Console]::In.ReadLine())) {
 $stream=$null;$bitmap=$null
 try {
  $file=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($ruta)) ([Windows.Storage.StorageFile])
  $stream=Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap=Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  $lines=@(foreach($line in $result.Lines){
   $left=1e9;$top=1e9;$right=0;$bottom=0
   foreach($word in $line.Words){$r=$word.BoundingRect;$left=[Math]::Min($left,$r.X);$top=[Math]::Min($top,$r.Y);$right=[Math]::Max($right,$r.X+$r.Width);$bottom=[Math]::Max($bottom,$r.Y+$r.Height)}
   if($line.Words.Count){@{text=$line.Text;rect=@($left,$top,($right-$left),($bottom-$top))}}
  })
  $words=@(foreach($line in $result.Lines){foreach($word in $line.Words){$r=$word.BoundingRect;@{text=$word.Text;rect=@($r.X,$r.Y,$r.Width,$r.Height)}}})
  $salida=@{ok=$true;lineas=$lines;palabras=$words}
 } catch {$salida=@{ok=$false}}
 finally {if($bitmap){$bitmap.Dispose()};if($stream){$stream.Dispose()}}
 [Console]::Out.WriteLine((ConvertTo-Json -InputObject $salida -Depth 5 -Compress));[Console]::Out.Flush()
}
'''

class OcrSkins:
    def __init__(self):self.lock=threading.RLock();self.proceso=None;self.cola=None;self.cerrado=False
    def iniciar(self):
        if self.proceso and self.proceso.poll() is None:return
        codigo=base64.b64encode(CODIGO.encode('utf-16-le')).decode('ascii')
        self.proceso=subprocess.Popen(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',codigo],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf8',bufsize=1,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.cola=cola=queue.Queue();proceso=self.proceso
        def recibir():
            try:
                for linea in proceso.stdout:cola.put(linea)
            finally:cola.put(None)
        threading.Thread(target=recibir,daemon=True,name='Capri-OCR-fichas').start()
    def leer(self,ruta,palabras=False):
        with self.lock:
            if self.cerrado:raise ErrorFortnite('La lectura de skins se cerró.')
            try:
                self.iniciar();self.proceso.stdin.write(str(Path(ruta).resolve())+'\n');self.proceso.stdin.flush()
                linea=self.cola.get(timeout=7)
                if linea is None:raise OSError('OCR cerrado')
                d=json.loads(linea.lstrip('\ufeff'))
                if d.get('ok') is not True or not isinstance(d.get('lineas'),list):raise ValueError('OCR no disponible')
                lineas=d['lineas']+(d.get('palabras',[]) if palabras else [])
                unicos={}
                for t in lineas:
                    if isinstance(t,dict) and isinstance(t.get('text'),str) and isinstance(t.get('rect'),list) and len(t['rect'])==4:
                        unicos[t['text'],tuple(t['rect'])]=Texto(t['text'],tuple(t['rect']))
                return tuple(unicos.values())
            except (OSError,ValueError,queue.Empty) as e:
                self.detener();raise ErrorFortnite('No pude leer la ficha con el reconocimiento local de Windows.') from e
    def detener(self):
        p=self.proceso;self.proceso=None
        if p:
            if p.poll() is None:
                p.terminate()
                try:p.wait(timeout=.5)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=1)
            for f in (p.stdin,p.stdout):
                if f:
                    try:f.close()
                    except OSError:pass
    def cerrar(self):
        with self.lock:self.cerrado=True;self.detener()
