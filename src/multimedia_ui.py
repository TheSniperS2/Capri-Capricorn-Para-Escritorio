"""Reproductor flotante; Capri se sienta sobre él en modo personaje."""
import math
import time
from PIL import ImageTk,Image,ImageOps
from tema_ui import tk,LienzoUI,actual,color
from reproduccion_pc import ReproduccionPC,elegir
from multimedia_diseno import dibujar_multimedia,portada,tiempos,ALTO,ANCHO
from musica_visual import vista_escucha,balancear,AnimacionEscucha
from idiomas import idioma_actual


class PanelMultimedia:
    def __init__(self,app):
        self.app=app;self.root=app.root;self.backend=getattr(app,'reproduccion_multimedia',None) or ReproduccionPC()
        self.ventana=None;self.marco=None;self.visible=False;self.cerrado=False;self.fuente=None;self.sesion=None
        self.tarjeta=None;self.tarjeta_foto=None;self.firma_tarjeta=None;self.poses={};self.visores={};self.escenas={}
        self.drag=None;self.apoyo_id=None;self.tarea=self.root.after(350,self.actualizar)
        self.animacion_escucha=AnimacionEscucha()
        if app.cfg.get('panel_multimedia') and app.cfg.get('animaciones',True) and not app.es_personaje():
            self.animacion_escucha.preparar((round(320*app.escala_avatar),round(210*app.escala_avatar)),app.cfg.get('efecto_glitch',True))

    def datos(self):
        if not self.backend.fecha or time.monotonic()-self.backend.fecha>8:return None
        s=elegir(self.backend.sesiones,self.app.cfg.get('multimedia_fuente','auto'),self.fuente)
        return self.backend.presentar({**s,'_fecha':s.get('_fecha',self.backend.fecha)}) if s else None

    def disfrutando(self):
        d=self.datos()
        return bool(d and d['estado']=='Playing' and self.app.cfg.get('reaccion_musica',True)
                    and not self.app.hablando and not self.app.escuchando)

    def crear(self):
        v=self.ventana=tk.Toplevel(self.root);v.withdraw();v.title('Capri · Música');v.overrideredirect(True)
        v.configure(bg='#010203');v.attributes('-topmost',True)
        try:v.wm_attributes('-transparentcolor','#010203')
        except tk.TclError:pass
        self.canvas=LienzoUI(v,bg='#010203',highlightthickness=0);self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<ButtonPress-1>',self.inicio_arrastre);self.canvas.bind('<B1-Motion>',self.arrastrar)
        self.canvas.bind('<ButtonRelease-1>',self.fin_arrastre);self.canvas.bind('<Button-3>',self.app.menu)
        self.canvas.bind('<Motion>',self.cursor)
        self.colocar_ventana()
        from ventanas import registrar_apoyo
        self.apoyo_id=registrar_apoyo(v)

    def colocar_ventana(self):
        s=self.app.escala_avatar;w=round(ANCHO*s);h=round(ALTO*s)
        pos=self.app.cfg.get('posicion_multimedia')
        if not (isinstance(pos,list) and len(pos)==2 and all(type(v) is int for v in pos)):
            pos=[self.root.winfo_x()-w-18,self.root.winfo_y()+40]
        x=max(0,min(pos[0],self.root.winfo_screenwidth()-w));y=max(0,min(pos[1],self.root.winfo_screenheight()-h-40))
        self.ventana.geometry(f'{w}x{h}+{x}+{y}');self.canvas.configure(width=w,height=h)
        self.escala_ventana=s

    def actualizar(self):
        if self.cerrado:return
        self.sincronizar();self.tarea=self.root.after(40,self.actualizar)

    def sincronizar(self):
        if self.cerrado:return
        a=self.app;permitido=a.cfg.get('panel_multimedia',False) and not a.cerrado and not a.saliendo
        if not permitido:self.animacion_escucha.cancelar()
        oculta=getattr(getattr(a,'visibilidad',None),'oculta',False)
        visible=permitido and not oculta and not a.intro_activa and self.root.state()=='normal'
        self.backend.activar(permitido and not oculta)
        cambio=visible!=self.visible;self.visible=visible
        if visible:
            if self.ventana is None:self.crear()
            if getattr(self,'escala_ventana',None)!=a.escala_avatar:self.colocar_ventana()
            if self.ventana.state()!='normal':self.ventana.deiconify()
            self.dibujar()
            self.ordenar_capas()
        elif self.ventana:self.ventana.withdraw()

    def ordenar_capas(self):
        if not self.visible or not self.ventana or self.ventana.state()!='normal' or self.root.state()!='normal':return
        # Bajar solo el reproductor respecto a Capri conserva el foco y las demás ventanas.
        if self.root.tk.call('wm','stackorder',self.ventana,'isabove',self.root):
            self.ventana.lower(self.root)

    def _tarjeta(self,s):
        d=self.datos();self.sesion=d
        pos,_=tiempos(d or {})
        identidad=tuple(d.get(k) for k in ('fuente','titulo','artista','estado')) if d else None
        firma=(self.backend.fecha,int(pos),s,actual(),idioma_actual(),self.backend.ocupado,self.backend.error,self.fuente,identidad,bool(d and d.get('_pendiente')))
        if firma==self.firma_tarjeta:return
        from avatar import LienzoRaster
        self.firma_tarjeta=firma
        pref=self.app.cfg.get('multimedia_fuente','auto')
        cantidad=sum(pref=='auto' or (v['proveedor']=='Spotify')==(pref=='spotify') for v in self.backend.sesiones)
        if pref=='auto' and any(v['estado']=='Playing' for v in self.backend.sesiones):cantidad=1
        im=Image.new('RGBA',(ANCHO*2,ALTO*2))
        dibujar_multimedia(LienzoRaster(im,2),d,ocupado=self.backend.ocupado,error=self.backend.error,cantidad=cantidad)
        arte=portada(d or {})
        if arte:im.alpha_composite(arte.resize((120,120),Image.Resampling.LANCZOS),(710,38))
        self.tarjeta=im.resize((round(ANCHO*s),round(ALTO*s)),Image.Resampling.LANCZOS)
        self.tarjeta_foto=ImageTk.PhotoImage(self.tarjeta)

    def _pose(self,s,fase=0):
        boca=bool(self.app.hablando and self.app.boca_activa)
        espejo=self.app.companera.direccion<0
        clave=(s,actual(),boca,espejo,fase)
        if clave not in self.poses:
            p=self.app.companera;p.redimensionar(s)
            im=p.lienzos[6 if boca else 3].copy()
            im=balancear(im,fase/12,True)
            if espejo:im=ImageOps.mirror(im)
            self.poses[clave]=(im,ImageTk.PhotoImage(im))
            if len(self.poses)>60:
                ultimo=self.poses[clave];self.poses.clear();self.poses[clave]=ultimo
        return self.poses[clave]

    def apoyo(self):
        if not self.visible or not self.ventana or self.ventana.state()!='normal' or not self.apoyo_id:return None
        v=self.ventana
        return {'id':self.apoyo_id,'titulo':'Capri · Música','rect':(v.winfo_x(),v.winfo_y()+2,v.winfo_x()+v.winfo_width(),v.winfo_y()+v.winfo_height())}

    def actualizar_apoyo(self):
        p=self.app.companera;v=self.apoyo()
        if not v:return
        ahora=time.monotonic();p.refrescar(ahora)
        p.ventanas=[v]+[otra for otra in p.ventanas if otra['id']!=v['id']]
        if p.soporte==v['id']:
            # El panel y Capri son ventanas distintas, pero su asiento sigue el borde sin saltos.
            p.x=v['rect'][0]+getattr(p,'soporte_dx',0);p.y=v['rect'][1]-p.alto*.64
            p.quieta_hasta=ahora+15
        elif (self.disfrutando() and self.app.cfg.get('pasear_personaje',True) and not p.libre
              and v['rect'][1]>=p.alto*.64 and not p.salto and not self.app.drag and ahora>=p.proxima_accion):
            p.preparar_salto(v,ahora);p.proxima_accion=ahora+15

    def apoyar_personaje(self):
        v=self.apoyo();p=self.app.companera
        if not v:return False
        x,y,der,_=v['rect'];cx=p.x+p.ancho/2
        if y<p.alto*.64 or not x+10<cx<der-10 or abs(p.y+p.alto*.64-y)>55*p.escala:return False
        p.x=max(x-p.ancho*.35,min(der-p.ancho*.65,p.x));p.y=y-p.alto*.64
        p.salto=None;p.ancla=None;p.soporte=v['id'];p.soporte_dx=p.x-x;p.soporte_lado='libre'
        p.estado='sentada';p.libre=False;p.velocidad_caida=0.;p.quieta_hasta=time.monotonic()+15
        self.actualizar_apoyo();self.ordenar_capas();return True

    def dibujar_reaccion(self,c):
        p=self.app.companera
        if not self.visible or p.soporte!=self.apoyo_id or p.estado!='sentada' or not self.disfrutando():return
        activo=self.app.cfg.get('animaciones',True);ahora=time.monotonic()
        _,foto=self._pose(self.app.escala_avatar,int(ahora*8)%12 if activo else 0)
        self.foto_personaje=foto;p.imagen=foto;c.itemconfigure('personaje',image=foto)
        if activo:
            for i in range(2):
                u=(ahora*.35+i/2)%1
                c.create_text((172+i*15)*p.escala,(75-u*45)*p.escala,text='♪',fill=color('#ff9eaf'),font=('Chakra Petch',round(12*p.escala)),traducir=False)

    def _escena(self,c):
        s=self.app.escala_avatar;self._tarjeta(s);top=0
        escena=self.escenas.get(str(c))
        # El bucle principal puede haber utilizado el lienzo para una transición.
        if not escena or not c.type(escena['tarjeta']):
            c.delete('all');escena={'tarjeta':c.create_image(0,round(top*s),image=self.tarjeta_foto,anchor='nw')}
            escena['barras']=[c.create_rectangle(0,0,1,1,fill=color('#ff9eaf'),outline='') for _ in range(8)]
            self.escenas[str(c)]=escena
        if escena.get('foto_tarjeta')!=str(self.tarjeta_foto):
            c.itemconfigure(escena['tarjeta'],image=self.tarjeta_foto);escena['foto_tarjeta']=str(self.tarjeta_foto)
            escena['objeto_tarjeta']=self.tarjeta_foto
        activo=self.disfrutando() and self.app.cfg.get('animaciones',True)
        ahora=time.monotonic()
        for i,item in enumerate(escena['barras']):
            alto=(4+12*(.5+.5*math.sin(ahora*4+i*.8))) if activo else 2
            c.coords(item,(276+i*7)*s,(top+68-alto)*s,(280+i*7)*s,(top+68)*s)
            c.itemconfigure(item,fill=color('#ff9eaf'))
    def dibujar(self):self._escena(self.canvas)

    def imagen_visor(self):
        if not self.app.cfg.get('panel_multimedia') or not self.disfrutando():return None
        a=self.app;ahora=time.monotonic();animaciones=bool(a.cfg.get('animaciones',True))
        efectos=animaciones and bool(a.cfg.get('efecto_glitch',True))
        tamano=(round(320*a.escala_avatar),round(210*a.escala_avatar))
        if animaciones:self.animacion_escucha.preparar(tamano,efectos)
        else:self.animacion_escucha.cancelar()
        fase=self.animacion_escucha.fase(ahora) if animaciones else None
        interferencia=int(ahora*28)%6 if efectos and a.avatar.glitch_activo else None
        clave=(a.escala_avatar,fase,animaciones,efectos,interferencia)
        if clave not in self.visores:
            im=self.animacion_escucha.cuadros[fase] if fase is not None else vista_escucha(tamano)
            if im is None:return None
            if interferencia is not None:
                from avatar import interferencia as cortar_senal
                im=cortar_senal(im,interferencia)
            self.visores[clave]=ImageTk.PhotoImage(im)
            if len(self.visores)>32:self.visores.pop(next(iter(self.visores)))
        return self.visores[clave]

    def _cambiar_fuente(self):
        pref=self.app.cfg.get('multimedia_fuente','auto')
        if pref=='auto' and any(s['estado']=='Playing' for s in self.backend.sesiones):return
        opciones=[s for s in self.backend.sesiones if pref=='auto' or (s['proveedor']=='Spotify')==(pref=='spotify')]
        if len(opciones)>1:
            elegido=next((i for i,v in enumerate(opciones) if self.sesion and tuple(v[k] for k in ('fuente','titulo','artista'))==tuple(self.sesion[k] for k in ('fuente','titulo','artista'))),-1)
            v=opciones[(elegido+1)%len(opciones)];self.fuente=tuple(v[k] for k in ('fuente','titulo','artista'));self.firma_tarjeta=None

    def clic(self,e):
        s=self.app.escala_avatar;x=e.x/s;y=e.y/s
        if y<0:return False
        if x>412 and y<30:self.app.guardar('panel_multimedia',False);return True
        if (x>270 and y<32) or (x<55 and 158<y<193):self._cambiar_fuente();return True
        if 24<=x<=416 and 140<=y<=154:
            if self.sesion and self.sesion.get('duracion',0)>0:self.backend.solicitar('posicion',self.sesion,(x-24)/392*self.sesion['duracion'])
            return True
        if 155<=y<=193:
            accion='anterior' if 166<=x<=196 else 'siguiente' if 248<=x<=278 else ('pausa' if self.sesion and self.sesion.get('estado')=='Playing' else 'reanudar') if 202<=x<=242 else None
            if accion:
                if self.sesion:self.backend.solicitar(accion,self.sesion)
                self.firma_tarjeta=None;return True
        return False

    def inicio_arrastre(self,e):
        self.root.after_idle(self.ordenar_capas)
        if self.clic(e):self.drag=None;return
        self.drag=(e.x_root,e.y_root,self.ventana.winfo_x(),self.ventana.winfo_y())

    def arrastrar(self,e):
        if self.drag:
            x,y,wx,wy=self.drag
            nx=max(0,min(wx+e.x_root-x,self.root.winfo_screenwidth()-self.ventana.winfo_width()))
            ny=max(0,min(wy+e.y_root-y,self.root.winfo_screenheight()-self.ventana.winfo_height()))
            self.ventana.geometry(f'+{nx}+{ny}')
            self.ordenar_capas()

    def fin_arrastre(self,e):
        if self.drag:self.app.guardar('posicion_multimedia',[self.ventana.winfo_x(),self.ventana.winfo_y()])
        self.drag=None

    def cursor(self,e):
        x=e.x/self.app.escala_avatar;y=e.y/self.app.escala_avatar
        seek=140<=y<=154 and self.sesion and self.sesion.get('controles',{}).get('posicion')
        self.canvas.configure(cursor='hand2' if y<32 and x>270 or 158<y<193 or seek else 'fleur')

    def ocultar(self):
        self.backend.activar(False);self.visible=False
        if self.ventana:self.ventana.withdraw()

    def cerrar(self):
        if self.cerrado:return
        self.animacion_escucha.cancelar()
        self.ocultar();self.cerrado=True;self.backend.cerrar()
        if self.tarea:self.root.after_cancel(self.tarea);self.tarea=None
        if self.ventana:self.ventana.destroy();self.ventana=None
