"""Capturas propias con datos de demostración; no controla juegos ni cuentas."""
from pathlib import Path
from unittest.mock import patch
import ctypes
import shutil
import sys
import time

BASE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(BASE/'src'),str(BASE/'tests')]
from test_companera_control import ModoPersonaje
from tema_ui import tk,activar
from fuentes import cargar
from PIL import ImageGrab

SALIDA=BASE/'docs/media/novedades-2026-11/capturas'


def main():
    SALIDA.mkdir(parents=True,exist_ok=True)
    prueba=ModoPersonaje();prueba.setUp()
    try:
        with prueba.capri({'intro_inicio':False,'animaciones':False}) as (c,carpeta), \
             patch('lol_ui.PanelLoL._consultar'),patch('valorant_ui.PanelValorant._consultar'), \
             patch('playlists_ui.consultar_playlist',return_value=''):
            cargar(BASE);activar('#f786d4')
            fondo=tk.Toplevel(c.root);fondo.overrideredirect(True)
            fondo.configure(bg='#10090d');fondo.geometry('1260x1010+20+20')

            def foto(v,nombre):
                v.geometry('+60+60');v.deiconify();v.lift();fondo.lower(v);c.root.update()
                listo=tk.BooleanVar(master=c.root);c.root.after(100,lambda:listo.set(True));c.root.wait_variable(listo)
                v.lift()
                ctypes.windll.dwmapi.DwmFlush()
                x,y=v.winfo_rootx(),v.winfo_rooty()
                ImageGrab.grab(bbox=(x,y,x+v.winfo_width(),y+v.winfo_height())).save(SALIDA/(nombre+'.png'))

            c.configurar();c.panel_ajustes.mostrar('Juegos');foto(c.ajustes,'ajustes-juegos')
            from lol_seleccion import normalizar
            cfg=normalizar({});cfg['roles']['TOP']['pick']=[266,103,61];cfg['roles']['TOP']['ban']=[799,157,25]
            c.cfg['lol_seleccion']=cfg;c.abrir_lol();foto(c.ajustes,'lol')
            c.abrir_valorant();foto(c.ajustes,'valorant');c.ajustes.withdraw()

            from playlists import vincular,actualizar_titulo
            from playlists_metadata import archivo_portada
            for alias,uri,titulo in (
                ('Para jugar','spotify:playlist:1111111111111111111111','Sesión de juego'),
                ('Noche synth','spotify:playlist:2222222222222222222222','Noche synth')):
                vincular(alias,uri,carpeta);actualizar_titulo(uri,titulo,carpeta)
                p=archivo_portada(uri,carpeta);p.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(BASE/'assets/capri-icono-v2.png',p)
            c.vincular_playlist();d=c.playlist_dialogo
            d.nombre.set('Para concentrarme');foto(d.ventana,'playlists');d.ventana.withdraw()

            from cambios_modelos import GIB,informe_modelo
            from confirmaciones_ui import ConfirmarCambio
            modelos={'Modelo ligero':{'size':1.5*GIB,'details':{'parameter_size':'2B'}},
                     'Modelo completo':{'size':5*GIB,'details':{'parameter_size':'8B'}}}
            equipo=dict(cpu='Equipo de demostración',hilos=8,ram_total=32*GIB,ram_libre=20*GIB,gpus=[])
            confirmar=ConfirmarCambio(c.root,'Cambiar modelo de IA','',lambda:None,
                actual='Modelo ligero',nuevo='Modelo completo',equipo=equipo,
                evaluar=lambda e:informe_modelo('Modelo ligero','Modelo completo',modelos,e))
            foto(confirmar.ventana,'confirmar-cambio');confirmar.cancelar()

            from recordatorios import agregar
            avisos=agregar([],'Tomar agua',25)
            avisos=agregar(avisos,'Hacer una pausa',55)
            avisos=agregar(avisos,'Revisar mi proyecto',120)
            c.cfg['recordatorios']=avisos;c.abrir_recordatorios()
            foto(c.recordatorios_panel.ventana,'recordatorios');c.recordatorios_panel.ventana.withdraw()

            c.cfg['modo_visual']='pantalla';c.intro_activa=False
            with patch.object(c.monitor_pc.monitor,'activar'):
                c.root.deiconify();c.visibilidad.oculta=False
                c.cfg['monitor_pc']=True;c.cfg['escala_avatar']=1.6
                c.monitor_pc.monitor.datos=dict(cpu=18,ram=42,gpu=26,vram=2*GIB,fecha=time.monotonic())
                c.aplicar_escala();c.animar();c.monitor_pc.sincronizar();foto(c.root,'monitor-pc')
            assert c.monitor_pc.visible
            c.cfg['monitor_pc']=False;c.monitor_pc.sincronizar();c.root.withdraw()

            from test_panel_multimedia import sesion
            m=c.panel_multimedia
            with patch.object(m.backend,'activar'):
                c.cfg['panel_multimedia']=True;c.cfg['escala_avatar']=1.6;c.aplicar_escala()
                c.root.geometry('+1100+650');c.root.deiconify()
                m.backend.sesiones=[sesion(titulo='Night City',estado='Playing')]
                m.backend.fecha=time.monotonic();c.cfg['posicion_multimedia']=[60,60]
                m.sincronizar();foto(m.ventana,'multimedia')
            print('Capturas de demostración guardadas:',SALIDA)
    finally:prueba.tearDown()


if __name__=='__main__':main()
