"""Captura controles reales con datos temporales, sin juegos, cuentas ni red.

Complementa capturar_novedades.py. No pulsa acciones de juego ni reproduce voz.
Las imágenes de los favoritos son el icono de Capri, no miniaturas de Roblox.
"""
from pathlib import Path
from unittest.mock import patch
import ctypes
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BASE / 'src'), str(BASE / 'tests')]
from test_companera_control import ModoPersonaje
from tema_ui import tk, activar
from fuentes import cargar
from PIL import Image, ImageGrab

SALIDA = BASE / 'docs/media/novedades-2026-11/seleccion-juegos/capturas'


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    prueba = ModoPersonaje()
    prueba.setUp()
    try:
        with prueba.capri({'intro_inicio': False, 'animaciones': False}) as (c, carpeta), \
             patch('lol_ui.PanelLoL._consultar'), \
             patch('valorant_ui.PanelValorant._consultar'), \
             patch('roblox_ui.PanelRoblox.cargar_info'), \
             patch('playlists_ui.consultar_playlist', return_value=''), \
             patch('roblox_vision.en_primer_plano', return_value=False):
            cargar(BASE)
            activar('#f786d4')
            fondo = tk.Toplevel(c.root)
            fondo.overrideredirect(True)
            fondo.configure(bg='#10090d')
            fondo.geometry('1300x1020+20+20')

            def foto(ventana, nombre, tamano):
                ventana.geometry(f'{tamano[0]}x{tamano[1]}+50+45')
                ventana.deiconify()
                ventana.lift()
                fondo.lower(ventana)
                c.root.update()
                listo = tk.BooleanVar(master=c.root)
                c.root.after(120, lambda: listo.set(True))
                c.root.wait_variable(listo)
                ventana.lift()
                ctypes.windll.dwmapi.DwmFlush()
                x, y = ventana.winfo_rootx(), ventana.winfo_rooty()
                assert x >= 0 and y >= 0
                assert x + ventana.winfo_width() <= ventana.winfo_screenwidth()
                assert y + ventana.winfo_height() <= ventana.winfo_screenheight()
                ImageGrab.grab(bbox=(x, y, x + ventana.winfo_width(),
                                     y + ventana.winfo_height())).save(SALIDA / f'{nombre}.png')
                print(nombre, flush=True)

            from valorant import cargar_catalogo
            agentes = cargar_catalogo()['agents']
            ids = [next(a['id'] for a in agentes if a['name'] == n)
                   for n in ('Jett', 'Reyna', 'Sage')]
            c.guardar('valorant', {'preferencias': ids, 'auto_pick': False})
            c.abrir_valorant()
            foto(c.ajustes, 'valorant', (1000, 950))

            c.guardar('fortnite', {'modo': 'cero', 'equipo': 'duo'})
            c.abrir_fortnite()
            foto(c.ajustes, 'fortnite', (900, 900))

            c.guardar('cs2', {'mapas': ['Mirage', 'Inferno']})
            c.abrir_cs2()
            foto(c.ajustes, 'counter-strike', (1000, 830))

            from lol_seleccion import normalizar
            cfg = normalizar({})
            cfg['roles']['TOP']['pick'] = [266, 103, 61]
            cfg['roles']['TOP']['ban'] = [799, 157, 25]
            c.guardar('lol_seleccion', cfg)
            c.abrir_lol()
            foto(c.ajustes, 'lol', (1000, 950))

            from roblox import agregar_favorito
            cfg = agregar_favorito({}, 'Islas del cielo', '222222222')
            cfg = agregar_favorito(cfg, 'Mansión de neón', '111111111')
            c.guardar('roblox', cfg)
            for f in cfg['favoritos']:
                terror = f['nombre'].startswith('Mansión')
                c.roblox.informacion[f['id']] = dict(
                    lugar=f['url'].rsplit('/', 1)[-1], universo=f['id'],
                    nombre=f['nombre'], creador='Creador de ejemplo',
                    descripcion=('Explora una mansión misteriosa con tus amigos. '
                                 'Encuentra las llaves y descubre una salida.' if terror else
                                 'Explora islas flotantes y supera sus desafíos.'),
                    genero='Survival' if terror else 'Adventure',
                    subgenero='Escape' if terror else 'Exploration',
                    perfil='terror' if terror else 'aventura')
            c.abrir_roblox()
            p = c.roblox_panel
            p.pintar_info()
            with Image.open(BASE / 'assets/capri-icono-v2.png') as im:
                info = c.roblox.informacion[cfg['seleccion']]
                p.foto_juego = p.guardar_foto(info['universo'], im)
                p.icono.configure(image=p.foto_juego, text='', width=112)
            foto(c.ajustes, 'roblox', (1080, 800))
            c.ajustes.withdraw()

            # Son los widgets del probador existente, sin analizar el juego.
            from ajustes_ui import VentanaCyber
            from skins_ui import AjustesSkins
            w = tk.Toplevel(c.root)
            w.withdraw()
            w.geometry('680x790')
            w.minsize(620, 700)
            marco = VentanaCyber(w, 'SKINS')
            interior = tk.Frame(marco.cuerpo, bg='#10090d')
            interior.pack(fill='both', expand=True, padx=24, pady=16)
            skins = AjustesSkins(interior, {}, lambda *_: None, lambda *_: None,
                                 lambda *_: None, c.skins, juego='fortnite')
            indice = next(i for i, s in enumerate(skins.opciones)
                          if s['nombres']['en'] == 'Goku Black')
            skins.selector.current(indice)
            skins.previsualizar()
            from skins_dialogos import frases
            skins.texto.set(frases(skins.opciones[indice], 'es')[0])
            marco.mostrar_completa()
            foto(w, 'skins', (680, 790))
            w.destroy()

            # Controles nativos de escucha, separados para mostrar solo la opción.
            from escucha_activa import crear_opciones
            w = tk.Toplevel(c.root)
            w.withdraw()
            w.geometry('700x360')
            w.minsize(620, 330)
            marco = VentanaCyber(w, 'MICRÓFONO')
            interior = tk.Frame(marco.cuerpo, bg='#10090d')
            interior.pack(fill='both', expand=True, padx=24, pady=12)
            crear_opciones(interior, {'modo_escucha': 'preguntas'}, lambda *_: None)
            marco.mostrar_completa()
            foto(w, 'escucha', (700, 360))
            w.destroy()
    finally:
        prueba.tearDown()


if __name__ == '__main__':
    main()
