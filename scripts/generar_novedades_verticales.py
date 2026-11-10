"""Maqueta las capturas propias en láminas 1080×1920 mediante HTML/CSS.

Chrome/Edge headless solo abre estos documentos locales. No usa el perfil del
usuario. El arte de portada se genera aparte con ImageGen; aquí se compone el
material de presentación y se exporta, sin recrear ni retocar las interfaces.
"""
from pathlib import Path
import argparse
import html
import os
import shutil
import subprocess
import tempfile
import zipfile
from PIL import Image

BASE=Path(__file__).resolve().parents[1]
MEDIOS=BASE/'docs/media/novedades-2026-11'

LAMINAS=[
    ('01-capri','TU ESCRITORIO.<br><em>MÁS CONTIGO.</em>',
     'Música, juegos y pequeños detalles<br>que hacen la diferencia.','cover','',
     'NUEVAS VISTAS. MÁS OPCIONES. MISMA CAPRI.'),
    ('02-playlists','TU PLAYLIST.<br><em>EN TUS PALABRAS.</em>',
     'Si Capri no entiende su nombre,<br>guárdala con uno fácil.','playlists','playlists.png',
     'Guardadas incluso al cerrar Capri.'),
    ('03-juegos','UN SOLO LUGAR.<br><em>TUS JUEGOS.</em>',
     'Navega, vuelve atrás y adapta<br>la ventana a tu espacio.','juegos','lol.png',
     'LoL · Valorant · Fortnite<br>Counter-Strike 2 · Roblox'),
    ('04-confirmaciones','CAMBIA<br><em>CON CLARIDAD.</em>',
     'Qué ganas, qué cambia<br>y qué conviene para tu PC.','confirmaciones','confirmar-cambio.png',
     'Tú decides antes de aplicar.'),
    ('05-monitor','TU PC.<br><em>DE UN VISTAZO.</em>',
     'CPU, RAM, GPU y VRAM<br>encima de donde escribes.','monitor','monitor-pc.png',
     'Actívalo cuando quieras.'),
    ('06-recordatorios','QUE NO<br><em>SE TE PASE.</em>',
     'Tus avisos, en una agenda<br>que puedes tener a mano.','recordatorios','recordatorios.png',
     'Recordatorios fuera de los juegos.'),
    ('07-multimedia','TU MÚSICA.<br>ELLA TAMBIÉN<br><em>LA DISFRUTA.</em>',
     'Capri reacciona mientras escuchas.<br>El reproductor tiene su propio lugar.','multimedia','multimedia.png',
     'Panel independiente. Tú lo colocas.'),
]

CSS='''
@font-face{font-family:Chakra;src:url('../../../../assets/fonts/ChakraPetch-Regular.ttf')}
@font-face{font-family:Chakra;src:url('../../../../assets/fonts/ChakraPetch-Bold.ttf');font-weight:700}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1920px;overflow:hidden}
body{font-family:Chakra,sans-serif;background:#090711;color:#f6f4ff}
.poster{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(ellipse at 94% 35%,#23112e,transparent 65%),linear-gradient(155deg,#090b14,#0b0710 70%);--accent:#ef8ad3}
.poster:after{content:'';position:absolute;inset:28px;border:1px solid #5b315d;clip-path:polygon(24px 0,100% 0,100% calc(100% - 28px),calc(100% - 28px) 100%,0 100%,0 24px);pointer-events:none}
.ghost{position:absolute;bottom:0;right:-80px;width:950px;opacity:.12;filter:saturate(.6)}
.header{position:absolute;left:78px;right:100px;top:96px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #533455;padding-bottom:24px;font-size:23px;letter-spacing:3px;font-weight:700}
.brand{font-size:37px;letter-spacing:3px}.edition{font-size:20px;color:#c3a6c5;letter-spacing:2px}
.copy{position:absolute;top:215px;left:78px;right:100px}
h1{font-size:82px;line-height:1.05;letter-spacing:-2px;margin:0 0 34px;font-weight:700}
em{font-style:normal;color:var(--accent)}.copy p{font-size:34px;line-height:1.4;color:#c9bfd4;margin:0}
.screen{position:absolute;left:78px;width:902px;padding:12px;background:#10090d;border:1px solid #895786;box-shadow:0 26px 70px #0008;clip-path:polygon(18px 0,calc(100% - 18px) 0,100% 18px,100% calc(100% - 18px),calc(100% - 18px) 100%,18px 100%,0 calc(100% - 18px),0 18px)}
.screen img{display:block;width:100%;height:auto}.screen:before{content:'';position:absolute;top:0;left:24px;width:160px;height:3px;background:var(--accent)}
.note{position:absolute;left:78px;right:100px;top:1585px;font-size:32px;line-height:1.4;color:#e3d8eb}
.quote{position:absolute;left:78px;right:100px;padding:28px 32px;background:#211128;border-left:4px solid var(--accent);font-size:41px;line-height:1.25}
.quote small{display:block;font-size:20px;letter-spacing:3px;color:var(--accent);margin-bottom:14px}
.footer{position:absolute;left:78px;right:100px;bottom:160px;border-top:1px solid #58355c;padding-top:20px;display:flex;justify-content:space-between;color:#b6a3bf;font-size:22px;letter-spacing:2px}
.cover{--accent:#8ff2cc;background:#0b0616}.cover .hero{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cover .copy{top:220px}.cover h1{font-size:96px;letter-spacing:-3px}.cover .copy p{font-size:31px}.cover .note{top:1570px;background:#10091ce8;padding:26px 28px;border-left:4px solid var(--accent);font-size:25px;letter-spacing:2px;font-weight:700}
.playlists .screen{top:600px}.playlists .quote{top:1330px}.playlists .note{top:1585px}
.juegos{--accent:#93edcc}.juegos .screen{top:590px}.juegos .note{top:1495px;font-size:32px}
.confirmaciones{--accent:#b5a5ff}.confirmaciones .screen{top:620px}.benefits{position:absolute;left:96px;top:1395px;right:100px;font-size:29px;color:#cbbfd6;display:flex;gap:25px}.benefits span{border-top:2px solid var(--accent);padding-top:14px;flex:1}
.monitor .screen{top:605px;left:161px;width:728px;padding:16px}.monitor .note{top:1535px;font-size:38px}
.recordatorios{--accent:#93edcc}.recordatorios .screen{top:600px}.recordatorios .quote{top:1335px;font-size:37px}.recordatorios .note{top:1595px}
.multimedia .copy{top:210px}.multimedia h1{font-size:76px;margin-bottom:25px}.multimedia .copy p{font-size:30px}
.music-art{position:absolute;left:78px;top:660px;width:902px;height:570px;object-fit:cover;border:1px solid #895786;clip-path:polygon(18px 0,100% 0,100% calc(100% - 18px),calc(100% - 18px) 100%,0 100%,0 18px)}
.multimedia .screen{top:1210px}.multimedia .note{top:1640px;font-size:29px}
'''


def documento(n,datos):
    slug,titulo,descripcion,tipo,captura,nota=datos
    arte='<img class="hero" src="../arte-capri.webp" alt="Ilustración promocional de Capri">' if tipo=='cover' else '<img class="ghost" src="../arte-capri.webp" alt="">'
    pantalla=f'<div class="screen"><img src="../capturas/{captura}" alt="Interfaz real con datos de demostración"></div>' if captura else ''
    extra=''
    if tipo=='playlists':extra='<div class="quote"><small>ASÍ SE LA PIDES</small>Capri, pon mi playlist<br>Para jugar.</div>'
    if tipo=='recordatorios':extra='<div class="quote"><small>PRUEBA ESTA FRASE</small>Capri, recuérdame en<br>25 minutos tomar agua.</div>'
    if tipo=='confirmaciones':extra='<div class="benefits"><span>Beneficio<br>del cambio</span><span>Rapidez<br>y consumo</span><span>Consejo<br>para tu equipo</span></div>'
    if tipo=='multimedia':extra='<img class="music-art" src="../../../../assets/capri-escuchando-musica-v3.png" alt="Arte del modo pantalla mientras disfruta música">'
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{slug} · Capri</title><link rel="stylesheet" href="estilo.css"></head>
<body><main class="poster {tipo}">{arte}<header class="header"><span class="brand">CAPRI</span><span class="edition">ACTUALIZACIÓN // NOV 2026</span></header>
<div class="copy"><h1>{titulo}</h1><p>{descripcion}</p></div>{extra}{pantalla}<div class="note">{nota}</div><footer class="footer"><span>CAPRICORN DESKTOP</span><span>{n:02} / 07</span></footer></main></body></html>'''


def galeria(destino,extension):
    tarjetas=''.join(f'<a href="{html.escape(slug)}.{extension}"><img loading="lazy" src="{html.escape(slug)}.{extension}" alt="{html.unescape(titulo.replace("<br>"," ").replace("<em>","").replace("</em>",""))}"></a>' for slug,titulo,*_ in LAMINAS)
    (destino/'VER-IMAGENES.html').write_text(f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capri · Novedades verticales</title><style>body{{margin:0;background:#0b0812;color:#f3ebf7;font:18px system-ui;padding:32px}}h1{{font-size:34px}}p{{max-width:760px;line-height:1.6;color:#c8bad2}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;max-width:1500px}}img{{display:block;width:100%;height:auto}}a{{color:#f38ad7}}</style><h1>Capri · Novedades</h1><p>Siete láminas verticales 1080 × 1920. Abre una imagen para verla a tamaño completo. Capturas propias con datos de demostración y arte de presentación generado con ImageGen.</p><main>{tarjetas}</main></html>''',encoding='utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--arte',type=Path,help='PNG seleccionado de ImageGen; se conserva el original.')
    p.add_argument('--salida',type=Path,default=Path.home()/'Pictures/Capri/Novedades-2026-11-09-Vertical')
    p.add_argument('--sin-render',action='store_true');args=p.parse_args()
    vertical=MEDIOS/'vertical';vertical.mkdir(parents=True,exist_ok=True)
    if args.arte:
        with Image.open(args.arte) as im:im.save(MEDIOS/'arte-capri.webp','WEBP',quality=92,method=6)
    if not (MEDIOS/'arte-capri.webp').is_file():p.error('Falta el arte de presentación seleccionado.')
    (vertical/'estilo.css').write_text(CSS,encoding='utf8')
    for n,datos in enumerate(LAMINAS,1):(vertical/(datos[0]+'.html')).write_text(documento(n,datos),encoding='utf8')
    if args.sin_render:return
    navegador=next((s for s in (Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')) if s.is_file()),None)
    if not navegador:p.error('Se necesita Chrome o Edge para exportar los documentos locales.')
    args.salida.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='capri-poster-') as perfil:
        for slug,*_ in LAMINAS:
            png=args.salida/(slug+'.png')
            comando=[str(navegador),'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--no-default-browser-check','--disable-extensions','--disable-background-networking','--disable-sync','--force-device-scale-factor=1','--run-all-compositor-stages-before-draw','--virtual-time-budget=1500','--window-size=1080,1920','--user-data-dir='+perfil,'--screenshot='+str(png),(vertical/(slug+'.html')).as_uri()]
            subprocess.run(comando,check=True,timeout=45,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            with Image.open(png) as im:
                if im.size!=(1080,1920):raise ValueError(f'Tamaño incorrecto: {slug}: {im.size}')
                im.convert('RGB').save(vertical/(slug+'.webp'),'WEBP',quality=90,method=6)
            print(slug,flush=True)
    galeria(args.salida,'png');galeria(vertical,'webp')
    with zipfile.ZipFile(args.salida/'Capri-Novedades-Verticales.zip','w',zipfile.ZIP_DEFLATED) as z:
        for slug,*_ in LAMINAS:z.write(args.salida/(slug+'.png'),slug+'.png')
        z.write(args.salida/'VER-IMAGENES.html','VER-IMAGENES.html')
    print('Imágenes listas:',args.salida)


if __name__=='__main__':main()
