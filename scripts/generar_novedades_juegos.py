"""Exporta la selección de novedades en 9:16 y 16:9, con maquetas distintas.

Solo abre HTML local en un perfil temporal de Chrome/Edge. El arte corregido y
las capturas ya están incluidos; exportar no consulta cuentas ni genera imágenes.
"""
from pathlib import Path
import argparse
import html
import subprocess
import tempfile
import zipfile
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
MEDIOS = BASE / 'docs/media/novedades-2026-11/seleccion-juegos'

LAMINAS = [
    dict(slug='01-capri', tipo='cover', seccion='NUEVA ACTUALIZACIÓN',
         titulo='NUEVOS JUEGOS.<br><em>MISMA CAPRI.</em>',
         descripcion='Más formas de jugar, escuchar música<br>y compartir tu escritorio.',
         nota='VALORANT · FORTNITE · ROBLOX · CS2 · LOL',
         detalle='Conoce lo que llegó desde la presentación anterior.'),
    dict(slug='02-valorant', tipo='valorant', seccion='VALORANT',
         titulo='TU AGENTE.<br>TU PLAN B.<br><em>Y TU PLAN C.</em>',
         descripcion='Tres preferencias. Si una está ocupada,<br>Capri sigue con la siguiente.',
         captura='valorant.png', nota='Respeta los agentes señalados por tu equipo.',
         orden='Capri, busca partida en Valorant.',
         detalle='Confirmación opcional · Integración en pruebas'),
    dict(slug='03-skins', tipo='skins', seccion='FORTNITE + VALORANT // SKINS',
         titulo='TU SKIN.<br><em>SU OPINIÓN.</em>',
         descripcion='Tiene sus favoritas.<br>Y otras que no la convencen tanto.',
         captura='skins.png', nota='Su gusto por cada skin se mantiene al volver a verla.',
         orden='¿Qué te parece esta skin?', detalle='Reacciones en pruebas · Ejemplo del probador'),
    dict(slug='04-fortnite', tipo='fortnite', seccion='FORTNITE // LOBBY',
         titulo='¿UN DÚO<br><em>SIN CONSTRUIR?</em>',
         descripcion='Elige modo y tamaño de equipo.<br>Capri aplica tus opciones antes de buscar.',
         captura='fortnite.png', nota='También puedes aplicar las opciones sin entrar en cola.',
         orden='Capri, busca partida en Fortnite.', detalle='Battle Royale · Cero construcción · Solo a Squad'),
    dict(slug='05-roblox', tipo='roblox', seccion='ROBLOX',
         titulo='VOLVAMOS<br><em>A ESE JUEGO.</em>',
         descripcion='Tus favoritos, a una frase.<br>Su personalidad se adapta a la experiencia.',
         captura='roblox.png', nota='También opina sobre las piezas de tu avatar.',
         orden='Capri, abre Mansión de neón en Roblox.',
         detalle='Descripción y categoría públicas · Favoritos de ejemplo'),
    dict(slug='06-counter-strike', tipo='counter-strike', seccion='COUNTER-STRIKE 2',
         titulo='TUS MAPAS.<br><em>A TU MANERA.</em>',
         descripcion='Guarda tu selección y aplícala<br>antes de buscar en Competitivo.',
         captura='counter-strike.png', nota='Leer mapas · Aplicar sin buscar · Cancelar la cola',
         orden='Capri, aplica mis mapas en CS2.',
         detalle='Integración en pruebas · Aceptas tú la partida'),
    dict(slug='07-lol', tipo='lol', seccion='LEAGUE OF LEGENDS',
         titulo='TU LÍNEA.<br><em>TUS PRIORIDADES.</em>',
         descripcion='Tres picks y tres baneos por línea.<br>Preparados para tu turno de selección.',
         captura='lol.png', nota='Aceptación automática y confirmación de picks opcionales.',
         orden='Capri, busca partida en LoL.', detalle='Preferencias guardadas en tu equipo'),
    dict(slug='08-musica', tipo='musica', seccion='MODO MÚSICA',
         titulo='DALE PLAY.<br><em>MÍRALA DISFRUTAR.</em>',
         descripcion='Se mueve con la música en el visor.<br>El reproductor va donde tú quieras.',
         nota='Spotify o navegador. Capri y el panel se mueven por separado.',
         detalle='Arte del visor y sesión musical de demostración'),
    dict(slug='09-playlists', tipo='playlists', seccion='SPOTIFY // PLAYLISTS',
         titulo='¿NOMBRE IMPOSIBLE?<br><em>DÍSELO A TU MANERA.</em>',
         descripcion='Guarda el enlace con un nombre fácil.<br>Capri lo recuerda aunque la cierres.',
         captura='../../capturas/playlists.png', nota='Tu biblioteca, con búsqueda, edición y portadas.',
         orden='Capri, pon mi playlist Para jugar.', detalle='También admite una portada capturada por ti'),
    dict(slug='10-conversacion', tipo='conversacion', seccion='ESCUCHA DESPUÉS DE UNA PREGUNTA',
         titulo='ELLA PREGUNTA.<br><em>TÚ CONTINÚAS.</em>',
         descripcion='Responde sin repetir «Capri»<br>cada vez que ella te pregunta algo.',
         captura='escucha.png', nota='Es opcional. Tú eliges cómo quieres hablar con ella.',
         detalle='15 segundos para responder después de que termine su voz'),
    dict(slug='11-escritorio', tipo='escritorio', seccion='TU ESCRITORIO',
         titulo='TU PC A LA VISTA.<br><em>TUS AVISOS A TIEMPO.</em>',
         descripcion='Recursos junto al visor.<br>Recordatorios para lo que no quieres olvidar.',
         nota='Monitor opcional y agenda de avisos guardados.',
         orden='Capri, recuérdame en 25 minutos tomar agua.',
         detalle='Capri debe estar abierta para entregar los avisos'),
]

CSS = r'''
@font-face{font-family:Chakra;src:url('../../../../../assets/fonts/ChakraPetch-Regular.ttf')}
@font-face{font-family:Chakra;src:url('../../../../../assets/fonts/ChakraPetch-Bold.ttf');font-weight:700}
*{box-sizing:border-box}html,body{margin:0;overflow:hidden;background:#090b14;color:#f8f3ff;font-family:Chakra,sans-serif}
.poster{position:relative;overflow:hidden;isolation:isolate;--accent:#f18bd3;background:radial-gradient(ellipse at 100% 40%,#25102f,transparent 62%),linear-gradient(135deg,#090d18,#100817)}
.poster:before{content:'';position:absolute;inset:0;z-index:-1;opacity:.21;background:repeating-linear-gradient(0deg,transparent 0 4px,#61406222 4px 5px)}
.poster:after{content:'';position:absolute;inset:28px;pointer-events:none;border:1px solid #654261;clip-path:polygon(28px 0,100% 0,100% calc(100% - 30px),calc(100% - 30px) 100%,0 100%,0 28px)}
.header,.footer{position:absolute;display:flex;justify-content:space-between;align-items:center;letter-spacing:2px}
.header{border-bottom:1px solid #6b3f68;padding-bottom:22px}.brand{font-size:37px;font-weight:700}.edition{font-size:20px;color:#bcaac7}
.footer{border-top:1px solid #6b3f68;padding-top:18px;color:#bcaac7;font-size:20px}.footer b{color:var(--accent);font-weight:400}
.copy{position:absolute}.eyebrow{font-size:22px;letter-spacing:3px;color:var(--accent);font-weight:700;margin-bottom:24px;line-height:1.25}
h1{margin:0 0 28px;font-weight:700;line-height:1.02;letter-spacing:-2px}em{font-style:normal;color:var(--accent)}.description{margin:0;font-size:32px;line-height:1.4;color:#c8bfd5}
.serial{position:absolute;right:40px;top:155px;font-size:240px;line-height:1;font-weight:700;color:#b697d408;z-index:-1}
.stage{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px}
figure{margin:0;max-width:100%;min-height:0;display:flex;align-items:center;justify-content:center;flex-direction:column;padding:10px;background:#130b13;border:1px solid #795074;box-shadow:0 20px 60px #0008}
figure img{display:block;max-width:100%;object-fit:contain;min-height:0}figcaption{flex:none;color:#bcaac7;font-size:16px;letter-spacing:2px;padding:12px 0 2px;text-align:center}
.feature-note{position:absolute;border-left:3px solid var(--accent);padding-left:24px;font-size:33px;line-height:1.35;color:#e9dff0}
.command{position:absolute;background:#25132d;border:1px solid #694361;padding:22px 26px;font-size:32px;line-height:1.3;color:#f8effc}
.command small{display:block;font-size:17px;letter-spacing:2px;color:var(--accent);margin-bottom:8px}
.detail{position:absolute;color:#baabc6;font-size:21px;line-height:1.4}
.valorant{--accent:#ff8c9c}.fortnite,.lol{--accent:#9bf0ce}.roblox{--accent:#7fe2e9}.counter-strike{--accent:#f5d78f}.conversacion{--accent:#9bf0ce}
.hero{position:absolute;object-fit:contain;z-index:-1;mask-image:linear-gradient(to right,transparent,#000 1.5%,#000 98.5%,transparent),linear-gradient(to bottom,transparent,#000 4%,#000 88%,transparent);mask-composite:intersect}.cover{background:#0b0616}.cover:before{display:none}.cover .copy{text-shadow:0 3px 20px #06040f}.cover .description{color:#dbd1e4}.cover .feature-note{background:#10091ee8;padding:24px;border-left:3px solid var(--accent);font-weight:700;letter-spacing:2px}
.music-art{width:100%;object-fit:contain;border:1px solid #795074;box-shadow:0 20px 60px #0008}.musica .stage figure{width:100%}
.dialogue{width:100%;background:#160d20;border:1px solid #6f4a70;padding:26px 30px;display:grid;gap:26px}
.dialogue .label{font-size:18px;letter-spacing:2px;color:#bcaac7;margin-bottom:6px}.dialogue blockquote{margin:0;font-size:38px;line-height:1.25}.dialogue b{display:block;font-size:19px;letter-spacing:3px;color:var(--accent);margin-bottom:10px}
.escritorio .stage{display:block}.escritorio figure{position:absolute}.escritorio .pc img{width:100%}.escritorio .agenda img{width:100%}
.vertical,.vertical .poster{width:1080px;height:1920px}.vertical .header{left:78px;right:100px;top:90px}.vertical .footer{left:78px;right:100px;bottom:65px}
.vertical .copy{left:78px;right:100px;top:218px}.vertical h1{font-size:79px}.vertical .description{font-size:32px}
.vertical .stage{left:78px;top:620px;width:902px;height:850px}.vertical figure img{max-height:790px}.vertical .stage>figure{max-height:850px}
.vertical .feature-note{left:78px;right:100px;top:1515px;font-size:32px}.vertical .command{left:78px;right:100px;top:1625px;font-size:31px}.vertical .detail{left:78px;right:100px;top:1770px;font-size:20px}
.vertical .valorant h1{font-size:76px}.vertical .valorant .description{font-size:30px}.vertical .valorant .stage{top:675px;height:800px}.vertical .valorant figure img{max-height:740px}
.vertical .cover .copy{top:220px}.vertical .cover h1{font-size:83px}.vertical .cover .eyebrow{margin-bottom:22px}.vertical .cover .hero{left:125px;top:430px;width:830px;height:1475px}
.vertical .cover .feature-note{top:1600px;font-size:24px}.vertical .cover .detail{top:1715px;font-size:24px}
.vertical .skins .stage{top:580px;height:900px}.vertical .skins figure img{max-height:840px}
.vertical .playlists h1,.vertical .escritorio h1{font-size:67px}.vertical .playlists .stage{top:625px;height:830px}
.vertical .musica h1{font-size:73px}.vertical .musica .stage{top:600px;height:900px;justify-content:flex-start;gap:24px}.vertical .music-art{max-height:485px}.vertical .musica figure img{max-height:340px}.vertical .musica .feature-note{top:1540px}.vertical .musica .detail{top:1660px;font-size:24px}
.vertical .conversacion .stage{top:605px;height:870px;justify-content:flex-start;gap:34px}.vertical .conversacion figure{width:100%}.vertical .conversacion figure img{max-height:460px}.vertical .conversacion .feature-note{top:1510px}.vertical .conversacion .detail{top:1640px;font-size:27px}
.vertical .escritorio .stage{top:615px;height:860px}.vertical .escritorio .pc{left:0;top:0;width:550px}.vertical .escritorio .agenda{right:0;bottom:0;width:485px}.vertical .escritorio figure img{max-height:720px}
.horizontal,.horizontal .poster{width:1920px;height:1080px}.horizontal .header{left:85px;right:85px;top:54px}.horizontal .footer{left:85px;right:85px;bottom:46px}
.horizontal .copy{left:85px;top:220px;width:770px}.horizontal h1{font-size:73px}.horizontal .description{font-size:30px}.horizontal .eyebrow{font-size:21px;margin-bottom:28px}
.horizontal .stage{left:920px;top:170px;width:915px;height:740px}.horizontal figure img{max-height:680px}.horizontal .stage>figure{max-height:740px}
.horizontal .feature-note{left:85px;top:650px;width:760px;font-size:29px}.horizontal .command{left:85px;top:790px;width:760px;font-size:29px}.horizontal .detail{left:920px;top:930px;width:915px;font-size:20px;text-align:center}
.horizontal .cover .copy{top:275px;width:890px}.horizontal .cover h1{font-size:84px}.horizontal .cover .description{font-size:33px}.horizontal .cover .hero{left:950px;top:120px;width:890px;height:1020px}
.horizontal .cover .feature-note{top:780px;width:820px;font-size:23px}.horizontal .cover .detail{top:890px;left:85px;width:820px;text-align:left;font-size:23px}
.horizontal .valorant .copy{top:190px}.horizontal .valorant h1{font-size:72px}.horizontal .valorant .feature-note{top:670px}
.horizontal .playlists h1,.horizontal .escritorio h1{font-size:64px}.horizontal .playlists .stage{height:740px}
.horizontal .skins .stage{left:1060px;width:650px}.horizontal .skins figure img{max-height:680px}
.horizontal .musica .stage{top:165px;height:760px;justify-content:flex-start;gap:20px}.horizontal .music-art{height:425px}.horizontal .musica figure img{max-height:260px}.horizontal .musica .feature-note{top:700px}.horizontal .musica .detail{top:930px}
.horizontal .conversacion .stage{top:200px;height:700px;justify-content:flex-start;gap:30px}.horizontal .dialogue blockquote{font-size:34px}.horizontal .conversacion figure img{max-height:340px}.horizontal .conversacion .feature-note{top:700px}
.horizontal .escritorio .pc{top:0;left:0;width:520px}.horizontal .escritorio .agenda{bottom:0;right:0;width:420px}.horizontal .escritorio figure img{max-height:650px}
'''


def captura(nombre, clase=''):
    ruta = f'../capturas/{nombre}'
    return (f'<figure class="{clase}"><img src="{ruta}" alt="Controles reales de Capri con datos de ejemplo">'
            '<figcaption>CAPRI // VISTA DE DEMOSTRACIÓN</figcaption></figure>')


def documento(indice, datos, formato):
    tipo = datos['tipo']
    arte = '<img class="hero" src="../arte-capri-corregido.webp" alt="Capri con su cabello completo">' if tipo == 'cover' else ''
    contenido = captura(datos['captura']) if datos.get('captura') else ''
    if tipo == 'musica':
        contenido = ('<img class="music-art" src="../../../../../assets/capri-escuchando-musica-v3.png" alt="Arte del modo música">'
                     + captura('../../capturas/multimedia.png'))
    if tipo == 'conversacion':
        contenido = ('<div class="dialogue"><div class="label">CONVERSACIÓN DE EJEMPLO</div>'
                     '<blockquote><b>CAPRI /</b>¿Ponemos algo de música?</blockquote>'
                     '<blockquote><b>TÚ /</b>Mi playlist Para jugar.</blockquote></div>' + contenido)
    if tipo == 'escritorio':
        contenido = captura('../../capturas/monitor-pc.png', 'pc') + captura('../../capturas/recordatorios.png', 'agenda')
    orden = ('<div class="command"><small>PRUEBA ESTA FRASE</small>' + html.escape(datos['orden']) + '</div>') if datos.get('orden') else ''
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{html.escape(datos['seccion'])} · Capri</title><link rel="stylesheet" href="estilo.css"></head>
<body class="{formato}"><main class="poster {tipo}">{arte}<div class="serial">{indice:02}</div>
<header class="header"><span class="brand">CAPRI</span><span class="edition">NOVEDADES // 09.11.26</span></header>
<div class="copy"><div class="eyebrow">{html.escape(datos['seccion'])}</div><h1>{datos['titulo']}</h1><p class="description">{datos['descripcion']}</p></div>
<div class="stage">{contenido}</div><div class="feature-note">{html.escape(datos['nota'])}</div>{orden}
<div class="detail">{html.escape(datos['detalle'])}</div><footer class="footer"><span>CAPRICORN DESKTOP</span><b>{indice:02} / {len(LAMINAS):02}</b></footer></main></body></html>'''


def galeria(carpeta, extension, formato):
    tarjetas = ''.join(f'<a href="{d["slug"]}.{extension}"><img src="{d["slug"]}.{extension}" loading="lazy" alt="{html.escape(d["seccion"])}"></a>' for d in LAMINAS)
    medida = '1080 × 1920 · TikTok' if formato == 'vertical' else '1920 × 1080 · README'
    (carpeta / 'VER-IMAGENES.html').write_text(f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capri · Edición juegos</title><style>body{{margin:0;padding:30px;background:#090b14;color:#f6efff;font:18px system-ui}}p{{color:#c5b7d3;line-height:1.5}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;max-width:1800px}}img{{display:block;width:100%}}</style><h1>Capri · Edición juegos</h1><p>{len(LAMINAS)} imágenes · {medida}. Arte promocional y capturas reales con datos de demostración. Abre una para verla completa.</p><main>{tarjetas}</main></html>''', encoding='utf8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--formato', choices=('vertical', 'horizontal', 'ambos'), default='ambos')
    p.add_argument('--salida', type=Path, default=Path.home() / 'Pictures/Capri/Novedades-2026-11-09-Edicion-Juegos')
    p.add_argument('--sin-render', action='store_true')
    args = p.parse_args()
    formatos = ('vertical', 'horizontal') if args.formato == 'ambos' else (args.formato,)
    navegador = next((s for s in (Path('C:/Program Files/Google/Chrome/Application/chrome.exe'), Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')) if s.is_file()), None)
    if not args.sin_render and not navegador:
        p.error('Se necesita Chrome o Edge para exportar el HTML local.')
    for formato in formatos:
        carpeta = MEDIOS / formato
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'estilo.css').write_text(CSS, encoding='utf8')
        for n, d in enumerate(LAMINAS, 1):
            (carpeta / (d['slug'] + '.html')).write_text(documento(n, d, formato), encoding='utf8')
        if args.sin_render:
            continue
        ancho, alto = (1080, 1920) if formato == 'vertical' else (1920, 1080)
        destino = args.salida / formato.capitalize()
        destino.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='capri-edicion-juegos-') as perfil:
            for d in LAMINAS:
                png = destino / (d['slug'] + '.png')
                comando = [str(navegador), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--disable-background-networking', '--disable-sync', '--force-device-scale-factor=1', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=1500', f'--window-size={ancho},{alto}', '--user-data-dir=' + perfil, '--screenshot=' + str(png), (carpeta / (d['slug'] + '.html')).as_uri()]
                subprocess.run(comando, check=True, timeout=45, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                with Image.open(png) as im:
                    if im.size != (ancho, alto):
                        raise ValueError(f'Tamaño incorrecto: {png.name}: {im.size}')
                    im.convert('RGB').save(carpeta / (d['slug'] + '.webp'), 'WEBP', quality=91, method=6)
                print(formato, d['slug'], flush=True)
        galeria(destino, 'png', formato)
        galeria(carpeta, 'webp', formato)
        with zipfile.ZipFile(destino / f'Capri-Edicion-Juegos-{formato.capitalize()}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for d in LAMINAS:
                z.write(destino / (d['slug'] + '.png'), d['slug'] + '.png')
            z.write(destino / 'VER-IMAGENES.html', 'VER-IMAGENES.html')
        print('Entrega:', destino, flush=True)


if __name__ == '__main__':
    main()
