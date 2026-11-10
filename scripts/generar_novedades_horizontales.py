"""Recompone las novedades para el README en 1920×1080, sin tocar las verticales."""
from pathlib import Path
import argparse
import html
import subprocess
import tempfile
import zipfile
from PIL import Image
from generar_novedades_verticales import MEDIOS,LAMINAS,documento


CSS='''
@font-face{font-family:Chakra;src:url('../../../../assets/fonts/ChakraPetch-Regular.ttf')}
@font-face{font-family:Chakra;src:url('../../../../assets/fonts/ChakraPetch-Bold.ttf');font-weight:700}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden}
body{font-family:Chakra,sans-serif;background:#090711;color:#f6f4ff}
.poster{position:relative;width:1920px;height:1080px;overflow:hidden;background:radial-gradient(ellipse at 85% 25%,#26142f,transparent 65%),linear-gradient(155deg,#090b14,#0b0710 70%);--accent:#ef8ad3}
.poster:after{content:'';position:absolute;inset:28px;border:1px solid #5b315d;clip-path:polygon(24px 0,100% 0,100% calc(100% - 28px),calc(100% - 28px) 100%,0 100%,0 24px);pointer-events:none}
.ghost{position:absolute;bottom:-430px;right:10px;width:1100px;opacity:.1;filter:saturate(.6)}
.header{position:absolute;left:90px;right:90px;top:64px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #533455;padding-bottom:22px;font-weight:700;letter-spacing:3px}
.brand{font-size:37px}.edition{font-size:21px;color:#c3a6c5;letter-spacing:2px}
.copy{position:absolute;top:240px;left:90px;width:755px}
h1{font-size:74px;line-height:1.08;letter-spacing:-2px;margin:0 0 36px;font-weight:700}
em{font-style:normal;color:var(--accent)}.copy p{font-size:31px;line-height:1.4;color:#c9bfd4;margin:0}
.screen{position:absolute;left:930px;top:176px;width:900px;padding:12px;display:flex;align-items:center;justify-content:center;background:#10090d;border:1px solid #895786;box-shadow:0 26px 70px #0008;clip-path:polygon(18px 0,calc(100% - 18px) 0,100% 18px,100% calc(100% - 18px),calc(100% - 18px) 100%,18px 100%,0 calc(100% - 18px),0 18px)}
.screen img{display:block;width:auto;height:auto;max-width:100%;max-height:738px}.screen:before{content:'';position:absolute;top:0;left:24px;width:160px;height:3px;background:var(--accent)}
.note{position:absolute;left:90px;width:755px;top:860px;font-size:29px;line-height:1.4;color:#e3d8eb}
.quote{position:absolute;left:90px;top:645px;width:755px;padding:26px 30px;background:#211128;border-left:4px solid var(--accent);font-size:36px;line-height:1.25}
.quote small{display:block;font-size:20px;letter-spacing:3px;color:var(--accent);margin-bottom:12px}
.footer{position:absolute;left:90px;right:90px;bottom:52px;border-top:1px solid #58355c;padding-top:20px;display:flex;justify-content:space-between;color:#b6a3bf;font-size:22px;letter-spacing:2px}
.cover{--accent:#8ff2cc;background:radial-gradient(ellipse at 90% 85%,#1f1633,#0b0616 75%)}
.cover .hero{position:absolute;left:880px;top:-360px;width:1060px;height:1883px;object-fit:contain;mask-image:linear-gradient(to right,transparent,#000 10%)}
.cover .copy{top:250px;width:930px}.cover h1{font-size:92px;letter-spacing:-3px}.cover .copy p{font-size:34px}.cover .note{top:790px;width:830px;background:#10091ce8;padding:25px 26px;border-left:4px solid var(--accent);font-size:25px;letter-spacing:2px;font-weight:700}
.playlists .screen{top:210px}.playlists .screen img,.confirmaciones .screen img{width:100%;max-height:none}
.juegos{--accent:#93edcc}.juegos .screen{top:170px}.juegos .note{top:690px;font-size:32px}
.confirmaciones{--accent:#b5a5ff}.confirmaciones .screen{top:210px}
.benefits{position:absolute;left:90px;top:650px;width:755px;font-size:26px;color:#cbbfd6;display:flex;gap:24px}.benefits span{border-top:2px solid var(--accent);padding-top:15px;flex:1}
.monitor .screen{left:1050px;top:175px;width:650px;padding:16px}.monitor .screen img{width:100%;max-height:none}.monitor .note{top:690px;font-size:38px}
.recordatorios{--accent:#93edcc}.recordatorios .screen{top:170px}
.multimedia .copy{top:205px}.multimedia h1{font-size:72px;margin-bottom:30px}.multimedia .copy p{font-size:29px}
.music-art{position:absolute;left:990px;top:160px;width:800px;height:445px;object-fit:cover;border:1px solid #895786;clip-path:polygon(18px 0,100% 0,100% calc(100% - 18px),calc(100% - 18px) 100%,0 100%,0 18px)}
.multimedia .screen{left:990px;top:585px;width:800px}.multimedia .screen img{width:100%;max-height:none}.multimedia .note{top:750px;font-size:29px}
'''


def galeria(destino,extension):
    tarjetas=''.join(f'<a href="{slug}.{extension}"><img loading="lazy" src="{slug}.{extension}" alt="{html.unescape(titulo.replace("<br>"," ").replace("<em>","").replace("</em>",""))}"></a>' for slug,titulo,*_ in LAMINAS)
    (destino/'VER-IMAGENES.html').write_text(f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capri · Novedades horizontales</title><style>body{{margin:0;background:#0b0812;color:#f3ebf7;font:18px system-ui;padding:32px}}p{{line-height:1.6;color:#c8bad2}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:24px;max-width:1800px}}img{{display:block;width:100%;height:auto}}@media(max-width:500px){{main{{grid-template-columns:1fr}}}}</style><h1>Capri · Novedades para el README</h1><p>Siete imágenes horizontales 1920 × 1080. Abre una para verla completa.</p><main>{tarjetas}</main></html>''',encoding='utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida',type=Path,default=Path.home()/'Pictures/Capri/Novedades-2026-11-09-Horizontal')
    p.add_argument('--sin-render',action='store_true');args=p.parse_args()
    carpeta=MEDIOS/'horizontal';carpeta.mkdir(parents=True,exist_ok=True)
    (carpeta/'estilo.css').write_text(CSS,encoding='utf8')
    for n,datos in enumerate(LAMINAS,1):(carpeta/(datos[0]+'.html')).write_text(documento(n,datos),encoding='utf8')
    if args.sin_render:return
    navegador=next((s for s in (Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')) if s.is_file()),None)
    if not navegador:p.error('Se necesita Chrome o Edge para exportar los documentos locales.')
    args.salida.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='capri-horizontal-') as perfil:
        for slug,*_ in LAMINAS:
            png=args.salida/(slug+'.png')
            comando=[str(navegador),'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--no-default-browser-check','--disable-extensions','--disable-background-networking','--disable-sync','--force-device-scale-factor=1','--run-all-compositor-stages-before-draw','--virtual-time-budget=1500','--window-size=1920,1080','--user-data-dir='+perfil,'--screenshot='+str(png),(carpeta/(slug+'.html')).as_uri()]
            subprocess.run(comando,check=True,timeout=45,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            with Image.open(png) as im:
                if im.size!=(1920,1080):raise ValueError(f'Tamaño incorrecto: {slug}: {im.size}')
                im.convert('RGB').save(carpeta/(slug+'.webp'),'WEBP',quality=90,method=6)
            print(slug,flush=True)
    galeria(args.salida,'png');galeria(carpeta,'webp')
    with zipfile.ZipFile(args.salida/'Capri-Novedades-Horizontales.zip','w',zipfile.ZIP_DEFLATED) as z:
        for slug,*_ in LAMINAS:z.write(args.salida/(slug+'.png'),slug+'.png')
        z.write(args.salida/'VER-IMAGENES.html','VER-IMAGENES.html')
    print('Imágenes horizontales listas:',args.salida)


if __name__=='__main__':main()
