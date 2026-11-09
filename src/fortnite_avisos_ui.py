"""Avisos opcionales y estado verificable de las fuentes públicas."""
from datetime import datetime,timezone,timedelta
import time,webbrowser
from tema_ui import tk
from ajustes_ui import BotonCyber,InterruptorCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui
from fortnite_avisos import normalizar

TEXTOS=('Avisos de Fortnite','Tienda y misiones con pavos para fundadores.',
        'Tu próxima visita a Fortnite','Avisar cuando cambie la tienda','Tengo una cuenta de fundador de STW',
        'Avisar si hay misiones con pavos','Los pavos de estas alertas requieren una cuenta de fundador y acceso a la misión. Las demás cuentas reciben rayos X.',
        'Capri consulta datos públicos mientras está abierta. Los avisos esperan a que termines de hablar.',
        'Comprobar ahora','Consultando las fuentes…','Todavía no se han consultado los datos.',
        'No pude verificar los datos actuales. Volveré a intentarlo.',
        'Tienda actualizada · {0}','Rotación STW · {0} · {1} pavos',
        'No hay misiones con pavos en esta rotación verificada.',
        '{0} · nivel {1} · {2} pavos · {3}', 'Disponible hasta {0}',
        'Próximo reinicio previsto: {0} (hora local).',
        'Las fuentes son comunitarias; Capri espera una rotación confirmada. No accede a tu cuenta Epic.',
        'Fuente de la tienda: Fortnite-API','Fuente de misiones: V-Bucks Daily',
        'La tienda de Fortnite acaba de cambiar. Ya puedes revisar la nueva rotación.',
        'Hay misiones de Salvar el Mundo con {0} pavos en total para fundadores. Revisa las zonas y los niveles en Ajustes, Avisos de Fortnite; tienes hasta {1}.')


class AjustesAvisosFortnite:
    def __init__(self,padre,config,guardar,monitor):
        self.f=padre;self.raiz=padre._root();self.config=normalizar(config);self.guardar=guardar;self.monitor=monitor;self._after=None;self.variables={}
        self.etiqueta(padre,'Tu próxima visita a Fortnite',TEXTO,21).pack(anchor='w',pady=(2,14))
        for clave,titulo in (('tienda','Avisar cuando cambie la tienda'),('fundador','Tengo una cuenta de fundador de STW'),('pavos','Avisar si hay misiones con pavos')):
            v=tk.BooleanVar(value=self.config[clave]);self.variables[clave]=v
            b=InterruptorCyber(padre,text=titulo,variable=v,command=lambda k=clave,v=v:self.cambiar(k,v.get()),bg=FONDO,fg=TEXTO)
            b.pack(anchor='w',pady=(0,12))
        for t in ('Los pavos de estas alertas requieren una cuenta de fundador y acceso a la misión. Las demás cuentas reciben rayos X.',
                  'Capri consulta datos públicos mientras está abierta. Los avisos esperan a que termines de hablar.'):
            self.etiqueta(padre,t,SUAVE,10).pack(fill='x',pady=(0,10))
        self.boton=BotonCyber(padre,text='Comprobar ahora',command=monitor.actualizar,bg=ACENTO,fg=FONDO,estilo='principal');self.boton.pack(anchor='w',pady=(4,14))
        tarjeta=tk.Frame(padre,bg=TARJETA,padx=14,pady=12);tarjeta.pack(fill='x')
        self.estado=tk.StringVar();self.etiqueta(tarjeta,'',TEXTO,11,textvariable=self.estado).pack(fill='x')
        self.reinicio=tk.StringVar();self.etiqueta(padre,'',ACENTO,10,textvariable=self.reinicio).pack(fill='x',pady=(12,8))
        self.etiqueta(padre,'Las fuentes son comunitarias; Capri espera una rotación confirmada. No accede a tu cuenta Epic.',SUAVE,9).pack(fill='x',pady=(0,8))
        for t,url in (('Fuente de la tienda: Fortnite-API','https://fortnite-api.com/'),('Fuente de misiones: V-Bucks Daily','https://vbucksdaily.com/')):
            l=self.etiqueta(padre,t,ACENTO,9,cursor='hand2');l.pack(anchor='w',pady=3);l.bind('<Button-1>',lambda e,u=url:webbrowser.open(u))
        padre.bind('<Destroy>',self.destruir,add='+');self.refrescar()

    @staticmethod
    def etiqueta(p,t,color,tamano,**kw):
        l=tk.Label(p,text=ui(t),bg=p.cget('bg'),fg=color,font=(FAMILIA,tamano),wraplength=450,justify='left',anchor='w',**kw)
        l.bind('<Configure>',lambda e:l.configure(wraplength=max(180,e.width)));return l

    def cambiar(self,k,v):
        self.config[k]=v;self.config=normalizar(self.config);self.guardar('fortnite_avisos',self.config)

    def refrescar(self):
        if not self.f.winfo_exists():return
        d=self.monitor.copia();ahora=time.time();lineas=[]
        if d['consultando']:lineas.append(ui('Consultando las fuentes…'))
        if d['errores']:lineas.append(ui('No pude verificar los datos actuales. Volveré a intentarlo.'))
        for tipo in ('tienda','pavos'):
            dato=d['datos'].get(tipo)
            if not dato or dato['vence']<=ahora:continue
            if tipo=='tienda':lineas.append(ui('Tienda actualizada · {0}').format(dato['rotacion']))
            else:
                lineas.append(ui('Rotación STW · {0} · {1} pavos').format(dato['rotacion'],dato['total']))
                for m in dato['misiones']:lineas.append(ui('{0} · nivel {1} · {2} pavos · {3}').format(m['zona'],m['nivel'],m['pavos'],m['tipo']))
                if not dato['total']:lineas.append(ui('No hay misiones con pavos en esta rotación verificada.'))
                lineas.append(ui('Disponible hasta {0}').format(datetime.fromtimestamp(dato['vence']).astimezone().strftime('%d/%m %H:%M')))
        self.estado.set('\n\n'.join(lineas) or ui('Todavía no se han consultado los datos.'))
        ahora_utc=datetime.now(timezone.utc);manana=(ahora_utc+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
        self.reinicio.set(ui('Próximo reinicio previsto: {0} (hora local).').format(manana.astimezone().strftime('%d/%m %H:%M')))
        self._after=self.raiz.after(1000,self.refrescar)

    def destruir(self,e):
        if e.widget is self.f and self._after:
            self.raiz.after_cancel(self._after);self._after=None
