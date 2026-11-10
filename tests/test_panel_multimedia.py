import base64
import io
import os
import subprocess
import threading
import time
import unittest
from unittest.mock import Mock,patch
from PIL import Image
from test_capri import PruebasTk
import test_companera_control as fixtures
from reproduccion_pc import normalizar_sesion,elegir,ReproduccionPC,OrdenReproduccion,SCRIPT
from multimedia_diseno import tiempos,portada


def sesion(fuente='Spotify.exe',titulo='Night City',estado='Playing'):
    return normalizar_sesion(dict(fuente=fuente,titulo=titulo,artista='Samurai',estado=estado,posicion=35,duracion=180,
                                 controles=dict(pausa=True,reanudar=True,siguiente=True,anterior=False)))


class Sesiones(unittest.TestCase):
    def test_esquinas_transparentes_sin_alfa_parcial_en_todas_las_escalas(self):
        from multimedia_diseno import dibujar_multimedia,preparar_tarjeta_ventana,ANCHO,ALTO
        from avatar import LienzoRaster
        original=Image.new('RGBA',(ANCHO*2,ALTO*2))
        dibujar_multimedia(LienzoRaster(original,2),sesion())
        for escala in (.75,1,1.25,1.5,1.6):
            im=preparar_tarjeta_ventana(original,(round(ANCHO*escala),round(ALTO*escala)))
            self.assertLessEqual(set(im.getchannel('A').getdata()),{0,255})
            w,h=im.size
            self.assertEqual([im.getpixel(p)[3] for p in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))],[0,0,0,0])
            self.assertEqual(im.getpixel((w//2,h//2))[3],255)

    def test_marco_opaco_continuo_sin_huecos_por_el_remuestreo_en_las_esquinas(self):
        from PIL import ImageDraw
        from multimedia_diseno import dibujar_multimedia,preparar_tarjeta_ventana,MARCO_MULTIMEDIA,ANCHO,ALTO
        from avatar import LienzoRaster
        original=Image.new('RGBA',(ANCHO*2,ALTO*2));dibujar_multimedia(LienzoRaster(original,2),sesion())
        for s in (.75,1,1.25,1.5):
            tamano=(round(ANCHO*s),round(ALTO*s));im=preparar_tarjeta_ventana(original,tamano)
            mascara=Image.new('L',tamano)
            puntos=[(round(MARCO_MULTIMEDIA[i]*tamano[0]/ANCHO),round(MARCO_MULTIMEDIA[i+1]*tamano[1]/ALTO)) for i in range(0,len(MARCO_MULTIMEDIA),2)]
            ImageDraw.Draw(mascara).polygon(puntos,fill=255)
            self.assertEqual(im.getchannel('A').tobytes(),mascara.tobytes())

    def test_bucle_de_escucha_se_prepara_fuera_de_la_interfaz_y_se_reutiliza(self):
        from musica_visual import AnimacionEscucha,FOTOGRAMAS_ESCUCHA,FPS_ESCUCHA
        hilos=[];entrado=threading.Event();continuar=threading.Event()
        def renderizar(tamano,senal,fase):
            hilos.append(threading.current_thread().ident)
            if fase==0:entrado.set();continuar.wait(2)
            return Image.new('RGBA',tamano,(fase,senal,0,255))
        bucle=AnimacionEscucha(renderizar)
        try:
            bucle.preparar((16,16));self.assertTrue(entrado.wait(1))
            self.assertIsNone(bucle.fase())
            continuar.set();limite=time.monotonic()+2
            while not bucle.cuadros and time.monotonic()<limite:time.sleep(.005)
            self.assertEqual(len(bucle.cuadros),FOTOGRAMAS_ESCUCHA)
            self.assertTrue(all(h!=threading.current_thread().ident for h in hilos))
            cuadros=bucle.cuadros;bucle.preparar((16,16))
            self.assertIs(bucle.cuadros,cuadros)
            self.assertEqual(bucle.fase(bucle.inicio+1.5/FPS_ESCUCHA),1)
            self.assertEqual(len(hilos),FOTOGRAMAS_ESCUCHA)
        finally:continuar.set();bucle.cancelar()
        self.assertFalse(bucle.cuadros)

    def test_cabeceo_deforma_el_personaje_sin_mover_bordes_ni_abrir_huecos(self):
        from musica_visual import _escena_escucha,_mover_escucha,FOTOGRAMAS_ESCUCHA
        escena=_escena_escucha((320,210))
        a=_mover_escucha(escena,0);b=_mover_escucha(escena,18)
        self.assertNotEqual(a.crop((100,60,250,150)).tobytes(),b.crop((100,60,250,150)).tobytes())
        self.assertEqual(a.crop((0,0,320,1)).tobytes(),b.crop((0,0,320,1)).tobytes())
        self.assertEqual(a.getchannel('A').getextrema(),(255,255))
        self.assertEqual(a.tobytes(),_mover_escucha(escena,FOTOGRAMAS_ESCUCHA).tobytes())

    @unittest.skipUnless(os.name=='nt','Puente PowerShell de Windows')
    def test_puente_controla_antes_de_leer_imagenes_y_tolera_metadatos_de_spotify(self):
        # Solo objetos falsos: no consulta ni controla reproductores del equipo.
        falso=r'''
function Esperar($op,[Type]$t) {return $op}
$script:estado='Playing';$script:controlado=$false
$sesion=New-Object PSObject -Property @{SourceAppUserModelId='Spotify.exe'}
$sesion|Add-Member ScriptMethod GetPlaybackInfo {return @{PlaybackStatus=$script:estado;Controls=@{IsPauseEnabled=$true;IsPlayEnabled=$true}}}
$sesion|Add-Member ScriptMethod TryGetMediaPropertiesAsync {
 if(-not $script:controlado){throw 'El control debe preceder a los metadatos'}
 return @{Title='Titulo actualizado';Artist='Artista actualizado';Thumbnail=$null}
}
$sesion|Add-Member ScriptMethod GetTimelineProperties {throw 'Sin tiempo'}
$sesion|Add-Member ScriptMethod TryPauseAsync {$script:controlado=$true;$script:estado='Paused';return $true}
$gestor=New-Object PSObject
$gestor|Add-Member ScriptMethod GetSessions {return @($sesion)}
'''
        # Se conserva el protocolo y toda la ruta real de selección/control del ayudante.
        codigo=falso+SCRIPT[SCRIPT.index('$artes=@{}'):]
        orden='{"accion":"pausa","fuente":"Spotify.exe","titulo":"Titulo anterior","artista":"Artista anterior"}\n'
        import json
        r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(codigo.encode('utf-16-le')).decode()],
                         input=orden,capture_output=True,text=True,encoding='utf8',timeout=15)
        self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(r.stdout);self.assertTrue(d['ok'],d)
        self.assertEqual(d['sesiones'][0]['estado'],'Paused')
        self.assertEqual(d['sesiones'][0]['titulo'],'Titulo actualizado')

    def test_play_pausa_responde_antes_de_la_confirmacion_y_no_modifica_la_lectura(self):
        modelo=ReproduccionPC();modelo.activo.set();d=sesion();d['_fecha']=time.monotonic()
        self.assertTrue(modelo.solicitar('pausa',d))
        self.assertEqual(modelo.presentar(d)['estado'],'Paused')
        self.assertTrue(modelo.presentar(d)['_pendiente'])
        self.assertEqual(d['estado'],'Playing')
        modelo.pendiente['hasta']=0
        self.assertEqual(modelo.presentar(d)['estado'],'Playing')

    def test_automatico_conserva_la_primera_fuente_aunque_windows_reordene(self):
        orden=OrdenReproduccion();spotify=sesion();video=sesion('opera.exe','Video')
        orden.actualizar([spotify],100)
        datos=orden.actualizar([video,spotify],102)
        self.assertEqual(elegir(datos,'auto','opera.exe')['fuente'],'Spotify.exe')
        spotify=sesion(titulo='Otra pista')
        datos=orden.actualizar([video,spotify],104)
        self.assertEqual(elegir(datos)['fuente'],'Spotify.exe')
        spotify['estado']='Paused'
        datos=orden.actualizar([spotify,video],106)
        self.assertEqual(elegir(datos,'auto','Spotify.exe')['fuente'],'opera.exe')
        spotify['estado']='Playing'
        datos=orden.actualizar([spotify,video],108)
        self.assertEqual(elegir(datos)['fuente'],'opera.exe')

    def test_lectura_ausente_no_vacia_panel_ni_cambia_prioridad_y_caduca(self):
        orden=OrdenReproduccion();spotify=sesion();video=sesion('opera.exe','Video')
        orden.actualizar([spotify],100)
        datos=orden.actualizar([video],102)
        retenida=elegir(datos)
        self.assertEqual(retenida['fuente'],'Spotify.exe')
        self.assertFalse(retenida['_confirmada'])
        self.assertEqual(tiempos(retenida,102),(37,180))
        modelo=ReproduccionPC();modelo.activo.set()
        self.assertFalse(modelo.solicitar('pausa',retenida))
        datos=orden.actualizar([video,spotify],104)
        self.assertTrue(elegir(datos)['_confirmada'])
        self.assertEqual(elegir(datos)['fuente'],'Spotify.exe')
        datos=orden.actualizar([video],106)
        datos=orden.actualizar([video],108)
        self.assertEqual(elegir(datos)['fuente'],'opera.exe')
        self.assertEqual(len(datos),1)
        self.assertEqual(orden.actualizar([],112),[])

    def test_sesion_sin_metadatos_o_fuente_desconocida_no_es_controlable(self):
        self.assertIsNone(normalizar_sesion({'fuente':'notepad.exe','titulo':'algo'}))
        self.assertIsNone(normalizar_sesion({'fuente':'Spotify.exe','titulo':''}))
        d=sesion();d.update(posicion=float('nan'),duracion=-10,controles={'siguiente':'true'})
        limpio=normalizar_sesion(d);self.assertEqual(limpio['posicion'],0);self.assertEqual(limpio['duracion'],0)
        self.assertFalse(limpio['controles']['siguiente'])

    def test_elige_reproduccion_y_permite_distinguir_dos_pestanas_del_mismo_navegador(self):
        a=sesion(estado='Paused');b=sesion('opera.exe','Vídeo A');c=sesion('opera.exe','Vídeo B')
        self.assertIs(elegir([a,b,c]),b)
        self.assertIs(elegir([a,b,c],'spotify'),a)
        self.assertIs(elegir([a,b,c],'navegador',('opera.exe','Vídeo B','Samurai')),c)
        self.assertIsNone(elegir([b,c],'spotify'))

    def test_progreso_solo_avanza_al_reproducir_y_no_inventa_duracion(self):
        d=sesion();d['_fecha']=100
        self.assertEqual(tiempos(d,105),(40,180))
        d['estado']='Paused';self.assertEqual(tiempos(d,105),(35,180))
        d['duracion']=0;self.assertEqual(tiempos(d,105),(0,0))
        self.assertIsNone(portada({'caratula':'no-es-base64'}))

    def test_buscar_posicion_exige_capacidad_y_tiempo_valido(self):
        modelo=ReproduccionPC();modelo.activo.set();d=sesion()
        self.assertFalse(modelo.solicitar('posicion',d,20))
        d['controles']['posicion']=True
        for valor in (-1,181,float('nan'),True,'10'):
            self.assertFalse(modelo.solicitar('posicion',d,valor))
        self.assertTrue(modelo.solicitar('posicion',d,20))
        self.assertEqual(modelo.ordenes.get_nowait()[2],20)

    def test_muestreo_no_reproduce_nada_y_una_orden_fallida_no_se_reintenta(self):
        recibido=threading.Event();fallido=threading.Event();cliente=Mock()
        def pedir(accion='estado',dato=None):
            if accion!='estado':fallido.set();raise OSError('Sin respuesta')
            recibido.set();return {'ok':True,'sesiones':[sesion()]}
        cliente.pedir.side_effect=pedir
        modelo=ReproduccionPC(lambda:cliente)
        try:
            modelo.activar(True);self.assertTrue(recibido.wait(2))
            limite=time.monotonic()+2
            while not modelo.fecha and time.monotonic()<limite:time.sleep(.01)
            self.assertTrue(modelo.fecha)
            for _ in range(10):modelo.activar(True)
            self.assertTrue(modelo.solicitar('siguiente',sesion()))
            self.assertTrue(fallido.wait(2))
        finally:
            modelo.cerrar();modelo.hilo.join(2)
        self.assertEqual(sum(c.args and c.args[0]=='siguiente' for c in cliente.pedir.call_args_list),1)
        self.assertFalse(any(c.args and c.args[0]=='reanudar' for c in cliente.pedir.call_args_list))


class Interfaz(PruebasTk):
    capri=fixtures.ModoPersonaje.capri

    def test_escucha_conserva_interferencia_y_respeta_el_interruptor(self):
        from PIL import ImageTk
        with self.capri() as (a,_),patch.object(a.panel_multimedia.backend,'activar'),patch('multimedia_ui.time.monotonic',return_value=100):
            a.cfg['panel_multimedia']=True;a.cfg['animaciones']=True;a.cfg['efecto_glitch']=True
            m=a.panel_multimedia;m.backend.sesiones=[sesion()];m.backend.fecha=100
            a.avatar.glitch_activo=False;normal=ImageTk.getimage(m.imagen_visor())
            a.avatar.glitch_activo=True;cortada=ImageTk.getimage(m.imagen_visor())
            self.assertEqual(normal.size,cortada.size)
            self.assertNotEqual(normal.tobytes(),cortada.tobytes())
            a.cfg['efecto_glitch']=False;sin_efecto=m.imagen_visor()
            a.avatar.glitch_activo=False
            self.assertIs(m.imagen_visor(),sin_efecto)

    def test_pose_del_visor_solo_durante_reproduccion_y_retorna_al_arte_normal(self):
        with self.capri() as (a,_),patch.object(a.panel_multimedia.backend,'activar'):
            a.cfg['panel_multimedia']=True;m=a.panel_multimedia
            m.backend.sesiones=[sesion()];m.backend.fecha=time.monotonic()
            self.assertIsNotNone(m.imagen_visor())
            self.assertEqual(a.vista_animacion().size,a.avatar.vista_maestra.size)
            self.assertIsNot(a.vista_animacion(),a.avatar.vista_maestra)
            for estado in ('Paused','Stopped','Unknown'):
                m.backend.sesiones[0]['estado']=estado
                self.assertIsNone(m.imagen_visor())
                self.assertIs(a.vista_animacion(),a.avatar.vista_maestra)
            m.backend.sesiones=[]
            self.assertIsNone(m.imagen_visor())
            m.backend.sesiones=[sesion()];a.cfg['reaccion_musica']=False
            self.assertIsNone(m.imagen_visor())

    def test_personaje_siempre_delante_del_panel_en_pausa_y_reproduccion(self):
        with self.capri(ajustes={'modo_visual':'personaje','panel_multimedia':True,'voz':False}) as (a,_),patch.object(a.panel_multimedia.backend,'activar'):
            a.root.deiconify();m=a.panel_multimedia;m.sincronizar();a.root.update_idletasks()
            for estado in ('Paused','Playing','Paused'):
                m.backend.sesiones=[sesion(estado=estado)];m.backend.fecha=time.monotonic()
                # Windows eleva el reproductor al pulsarlo: Capri debe seguir delante.
                m.ventana.lift();a.root.update_idletasks()
                foco=a.root.focus_get()
                m.sincronizar();a.root.update_idletasks()
                self.assertTrue(a.root.tk.call('wm','stackorder',a.root,'isabove',m.ventana))
                self.assertEqual(a.root.focus_get(),foco)

    def test_teletransporte_conserva_reproductor_posicion_y_controles(self):
        from types import SimpleNamespace
        with self.capri(ajustes={'modo_visual':'personaje','panel_multimedia':True,'voz':False}) as (a,_),patch.object(a.panel_multimedia.backend,'activar') as activar,patch.object(a.panel_multimedia.backend,'solicitar') as enviar:
            a.root.deiconify();m=a.panel_multimedia
            m.backend.sesiones=[sesion()];m.backend.fecha=time.monotonic()
            m.sincronizar();a.root.update_idletasks()
            ventana=m.ventana;posicion=(ventana.winfo_x(),ventana.winfo_y())
            activar.reset_mock()
            p=a.companera
            salto={'inicio':time.monotonic(),'x':p.x,'y':p.y,'destino':(200,300),'id':0,'izquierda':200,'lado':None}
            a.iniciar_transito('salto',salto=salto)
            for progreso in (0,.3,.7):
                a.transito['inicio']=time.monotonic()-a.transito['duracion']*progreso
                a.dibujar_transito();m.sincronizar();a.root.update_idletasks()
                self.assertTrue(m.visible)
                self.assertIs(m.ventana,ventana)
                self.assertEqual(ventana.state(),'normal')
                self.assertTrue(a.root.tk.call('wm','stackorder',a.root,'isabove',ventana))
                self.assertEqual((ventana.winfo_x(),ventana.winfo_y()),posicion)
            m.clic(SimpleNamespace(x=222,y=174))
            self.assertEqual(enviar.call_args.args[0],'pausa')
            self.assertFalse(any(c.args==(False,) for c in activar.call_args_list))
            a.finalizar_transito();m.sincronizar()
            self.assertEqual(ventana.state(),'normal')
            self.assertEqual((ventana.winfo_x(),ventana.winfo_y()),posicion)

    def test_arranca_con_personaje_y_reproductor_guardados(self):
        with self.capri(ajustes={'modo_visual':'personaje','panel_multimedia':True,'voz':False}) as (a,_),patch.object(a.panel_multimedia.backend,'activar'):
            self.assertTrue(a.es_personaje())
            self.assertIsNotNone(a.panel_multimedia)
            a.root.deiconify();a.panel_multimedia.sincronizar();a.animar();a.root.update_idletasks()
            self.assertEqual((a.root.winfo_width(),a.root.winfo_height()),(210,240))
            self.assertEqual(a.panel_multimedia.ventana.state(),'normal')

    def test_reproductor_flotante_controles_y_monitor_independientes(self):
        with self.capri() as (a,_),patch.object(a.panel_multimedia.backend,'activar'),patch.object(a.panel_multimedia.backend,'solicitar') as enviar,patch.object(a.monitor_pc.monitor,'activar'):
            a.root.deiconify();a.root.update_idletasks()
            m=a.panel_multimedia;backend=m.backend
            datos=sesion();buffer=io.BytesIO();Image.new('RGB',(80,80),'#1ddf94').save(buffer,format='PNG')
            datos['caratula']=base64.b64encode(buffer.getvalue()).decode()
            backend.sesiones=[datos,sesion('opera.exe','Vídeo de prueba')];backend.fecha=time.monotonic()
            a.guardar('panel_multimedia',True);a.root.update_idletasks()
            self.assertTrue(m.visible);self.assertIsNotNone(m.tarjeta_foto)
            self.assertIsNot(m.ventana.winfo_toplevel(),a.root)
            self.assertEqual(a.root.winfo_height(),338)
            a.guardar('monitor_pc',True);a.root.update_idletasks()
            self.assertEqual(a.root.winfo_height(),382)
            self.assertEqual(m.ventana.winfo_width(),440)
            from types import SimpleNamespace
            m.clic(SimpleNamespace(x=330,y=20));m.dibujar()
            self.assertEqual(m.sesion['fuente'],'Spotify.exe')
            a.guardar('multimedia_fuente','navegador');m.dibujar()
            self.assertEqual(m.sesion['fuente'],'opera.exe')
            m.clic(SimpleNamespace(x=262,y=174));self.assertEqual(enviar.call_args.args[0],'siguiente')
            self.assertEqual(enviar.call_args.args[1]['fuente'],'opera.exe')
            m.sesion['controles']['posicion']=True
            m.clic(SimpleNamespace(x=220,y=147));self.assertEqual(enviar.call_args.args[0],'posicion')
            self.assertAlmostEqual(enviar.call_args.args[2],90)
            backend.fecha-=10;m.dibujar();enviar.reset_mock();m.clic(SimpleNamespace(x=222,y=174));enviar.assert_not_called()
            a.guardar('panel_multimedia',False);self.assertFalse(m.visible)
            self.assertTrue(a.entrada_compacta.unida)

    def test_personaje_se_sienta_y_la_reaccion_se_detiene_en_pausa(self):
        with self.capri() as (a,_),patch.object(a.panel_multimedia.backend,'activar'),patch('intro.Transformacion') as transformar:
            transformar.return_value.fotos=[]
            a.root.deiconify();a.root.update_idletasks();a.cfg['panel_multimedia']=True
            m=a.panel_multimedia;backend=m.backend
            backend.sesiones=[sesion()];backend.fecha=time.monotonic()
            a.iniciar_intro();self.assertEqual(a.bienvenida.destino_tamano,(360,338))
            a.finalizar_intro();self.assertTrue(m.visible)
            self.assertTrue(m.disfrutando())
            foto=m.imagen_visor();self.assertIsNotNone(foto)
            backend.sesiones[0]['estado']='Paused'
            self.assertFalse(m.disfrutando())
            self.assertIsNone(m.imagen_visor())
            self.assertIs(a.vista_animacion(),a.avatar.vista_maestra)
            a.guardar('modo_visual','personaje')
            self.assertEqual(transformar.call_args.args[2].size,(210,240))
            a.finalizar_transito();a.root.update_idletasks()
            self.assertEqual((a.root.winfo_width(),a.root.winfo_height()),(210,240))
            self.assertEqual(m.ventana.state(),'normal')
            m.ventana.geometry('+350+400');a.root.update_idletasks()
            p=a.companera;p.x=400;p.y=400-p.alto*.64
            self.assertTrue(m.apoyar_personaje())
            self.assertEqual(p.soporte,m.apoyo_id)
            self.assertEqual(p.estado,'sentada')
            backend.sesiones[0]['estado']='Playing'
            with patch('multimedia_ui.vista_escucha',side_effect=AssertionError('Sin audifonos en personaje')):
                a.animar();self.assertIs(p.imagen,m.foto_personaje)
            antes=(m.ventana.winfo_x(),m.ventana.winfo_y())
            p.x+=100
            self.assertEqual((m.ventana.winfo_x(),m.ventana.winfo_y()),antes)
            m.ventana.geometry('+450+430');a.root.update_idletasks();m.actualizar_apoyo()
            self.assertAlmostEqual(p.y,432-p.alto*.64)
            p.x=10;p.y=10;p.soporte=None
            self.assertFalse(m.apoyar_personaje())
            self.assertIsNone(p.soporte)
            a.guardar('modo_visual','pantalla');a.finalizar_transito();a.root.update_idletasks()
            self.assertEqual(m.ventana.state(),'normal')
            self.assertEqual(a.root.winfo_height(),338)
