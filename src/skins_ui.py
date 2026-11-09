"""Controles de personalidad y un probador de diálogos dentro de Ajustes."""
import random
from tema_ui import tk,LienzoUI
from ajustes_ui import BotonCyber,InterruptorCyber,SelectorCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui,idioma_actual
from reacciones_skins import normalizar,catalogo
from skins_dialogos import frases,opinion

TEXTOS=('Reacciones','Gustos y comentarios de Capri sobre las skins.','Capri también tiene estilo.',
        'Reaccionar a las skins','Equipamiento fuera de partida','Fichas del casillero y la tienda',
        'Frecuencia de los comentarios','Discreta','Equilibrada','Entusiasta',
        'Los comentarios esperan su momento. Capri no repite la misma skin constantemente.',
        'Observa solo el juego activo. Las capturas se procesan en este equipo y no se guardan.',
        'PRUEBA DE PERSONALIDAD','Skin de ejemplo','Favorita de Capri','Escuchar ejemplo','Mirar mi skin ahora',
        'Este ejemplo no analiza el juego ni cambia tu equipamiento.',
        'No reconoce atuendos solo por su silueta: en Fortnite necesita el nombre visible en una ficha.',
        'Reacciones a skins desactivadas','Esperando una skin reconocible fuera de partida',
        'Capri toma la primera ficha como referencia. Al seleccionar otra skin, confirma su nombre y comenta sin repetirla.',
        'Las frases varían, pero su opinión sobre cada skin se mantiene incluso al reiniciar.',
        'Le gusta','Opinión neutral','No es de sus favoritas',
        'Estos son ejemplos; Capri reconoce muchas más skins en el juego.')


class AjustesSkins:
    def __init__(self,padre,config,guardar,enviar,ejemplo,monitor):
        self.config=normalizar(config);self.guardar=guardar;self.enviar=enviar;self.ejemplo=ejemplo;self.monitor=monitor
        self.f=padre;self.raiz=padre._root();self._after=None
        tk.Label(padre,text=ui('Capri también tiene estilo.'),bg=FONDO,fg=TEXTO,font=(FAMILIA,21,'bold')).pack(anchor='w',pady=(2,12))
        self.activo=tk.BooleanVar(value=self.config['activo'])
        InterruptorCyber(padre,text='Reaccionar a las skins',variable=self.activo,
                         command=lambda:self.cambiar('activo',self.activo.get()),bg=FONDO,fg=TEXTO).pack(anchor='w',pady=(0,14))
        self.juegos={}
        for juego,titulo,detalle in (('valorant','VALORANT','Equipamiento fuera de partida'),('fortnite','FORTNITE','Fichas del casillero y la tienda')):
            f=tk.Frame(padre,bg=TARJETA);f.pack(fill='x',pady=(0,8))
            v=tk.BooleanVar(value=self.config[juego]);self.juegos[juego]=v
            InterruptorCyber(f,text=titulo,variable=v,command=lambda k=juego,var=v:self.cambiar(k,var.get()),
                             bg=TARJETA,fg=TEXTO).pack(anchor='w',padx=12,pady=(10,2))
            tk.Label(f,text=ui(detalle),bg=TARJETA,fg=SUAVE,font=(FAMILIA,9)).pack(anchor='w',padx=12,pady=(0,10))
        tk.Label(padre,text=ui('Frecuencia de los comentarios'),bg=FONDO,fg=TEXTO,font=(FAMILIA,11,'bold')).pack(anchor='w',pady=(12,5))
        self.frecuencia=SelectorCyber(padre,values=('Discreta','Equilibrada','Entusiasta'))
        self.frecuencia.current(('discreta','equilibrada','entusiasta').index(self.config['frecuencia']));self.frecuencia.pack(fill='x')
        self.frecuencia.bind('<<ComboboxSelected>>',lambda e:self.cambiar('frecuencia',('discreta','equilibrada','entusiasta')[self.frecuencia.current()]))
        for t in ('Capri toma la primera ficha como referencia. Al seleccionar otra skin, confirma su nombre y comenta sin repetirla.',
                  'Las frases varían, pero su opinión sobre cada skin se mantiene incluso al reiniciar.',
                  'Observa solo el juego activo. Las capturas se procesan en este equipo y no se guardan.',
                  'No reconoce atuendos solo por su silueta: en Fortnite necesita el nombre visible en una ficha.'):
            tk.Label(padre,text=ui(t),bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=480,justify='left').pack(anchor='w',pady=(8,0))
        self.estado=tk.StringVar(value=ui(monitor.estado))
        tk.Label(padre,textvariable=self.estado,bg=FONDO,fg=ACENTO,font=(FAMILIA,9),wraplength=480,justify='left').pack(anchor='w',pady=(12,16))
        tk.Label(padre,text=ui('PRUEBA DE PERSONALIDAD'),bg=FONDO,fg=ACENTO,font=(FAMILIA,10,'bold')).pack(anchor='w',pady=(4,8))
        self.juego=SelectorCyber(padre,values=('Valorant','Fortnite'));self.juego.current(0);self.juego.pack(fill='x',pady=(0,6))
        self.juego.bind('<<ComboboxSelected>>',lambda e:self.llenar())
        self.selector=SelectorCyber(padre);self.selector.pack(fill='x')
        self.selector.bind('<<ComboboxSelected>>',lambda e:self.previsualizar())
        self.tarjeta=LienzoUI(padre,bg=FONDO,highlightthickness=0,height=60);self.tarjeta.pack(fill='x',pady=(8,0))
        self.tarjeta.bind('<Configure>',lambda e:self.dibujar())
        self.texto=tk.StringVar()
        tk.Label(padre,textvariable=self.texto,bg=TARJETA,fg=TEXTO,font=(FAMILIA,12),wraplength=460,justify='left',padx=14,pady=16).pack(fill='x')
        self.escuchar=BotonCyber(padre,text='Escuchar ejemplo',command=self.probar);self.escuchar.pack(fill='x',pady=(8,4))
        self.mirar=BotonCyber(padre,text='Mirar mi skin ahora',command=lambda:self.enviar('mira mi skin en '+('valorant' if self.juego.current()==0 else 'fortnite')))
        self.mirar.pack(fill='x',pady=(4,8))
        for texto in ('Este ejemplo no analiza el juego ni cambia tu equipamiento.',
                      'Estos son ejemplos; Capri reconoce muchas más skins en el juego.'):
            tk.Label(padre,text=ui(texto),bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=480,justify='left').pack(anchor='w',pady=(0,8))
        self._previa={};self.llenar();self.refrescar()
        padre.bind('<Destroy>',self.destruir,add='+')

    def cambiar(self,k,v):
        self.config=normalizar({**self.config,k:v});self.guardar('reacciones_skins',dict(self.config))

    def llenar(self):
        juego='valorant' if self.juego.current()==0 else 'fortnite';por_perfil={}
        # Una muestra por colección, priorizando Vandal/Phantom frente a armas
        # secundarias, para que el probador no sea una lista interminable.
        for s in sorted(catalogo(),key=lambda s:s.get('arma') not in ('Vandal','Phantom')):
            if s['juego']==juego and s['perfil']!='generica':por_perfil.setdefault(s['perfil'],s)
        # Probador breve: incluye Goku Black y ejemplos de las tres opiniones.
        genericas=[s for s in catalogo() if s['juego']==juego and s['perfil']=='generica']
        muestras={}
        for s in genericas:
            if s['nombres']['en']=='Goku Black':muestras[s['id']]=s
        for gusto in ('buena','neutral','mala'):
            s=next((s for s in genericas if opinion(s)==gusto and (juego=='fortnite' or s.get('arma')=='Vandal')),None)
            if s:muestras[s['id']]=s
        self.opciones=sorted([*por_perfil.values(),*muestras.values()],key=lambda s:(not s['favorita'],s['nombres'].get(idioma_actual(),s['nombres']['en'])))
        self.selector.configure(values=tuple(s['nombres'].get(idioma_actual(),s['nombres']['en']) for s in self.opciones))
        if self.opciones:self.selector.current(0);self.previsualizar()

    def previsualizar(self):
        if not self.opciones:return
        s=self.opciones[max(0,self.selector.current())];opciones=frases(s,idioma_actual());previa=self._previa.get(s['id'])
        self.texto.set(random.choice([f for f in opciones if f!=previa] or list(opciones)));self._previa[s['id']]=self.texto.get();self.dibujar()

    def dibujar(self):
        c=self.tarjeta;c.delete('all');w=max(100,c.winfo_width())
        if not getattr(self,'opciones',None):return
        s=self.opciones[max(0,self.selector.current())]
        c.create_polygon(1,1,w-13,1,w-1,13,w-1,57,1,57,fill=TARJETA,outline=ACENTO)
        c.create_polygon(14,29,27,14,40,29,27,44,fill=FONDO,outline=ACENTO,width=2)
        c.create_line(20,29,34,29,fill=TEXTO,width=2)
        c.create_text(52,21,text=s['nombres'].get(idioma_actual(),s['nombres']['en']),anchor='w',fill=TEXTO,font=(FAMILIA,10,'bold'),traducir=False)
        gusto={'buena':'Le gusta','neutral':'Opinión neutral','mala':'No es de sus favoritas'}[opinion(s)]
        c.create_text(52,41,text=ui('Favorita de Capri') if s['favorita'] else ui(gusto),anchor='w',fill=SUAVE,font=(FAMILIA,9))

    def probar(self):
        self.previsualizar();self.ejemplo(self.texto.get())

    def refrescar(self):
        self.estado.set(ui(self.monitor.estado));self._after=self.raiz.after(600,self.refrescar)

    def destruir(self,e):
        if e.widget is self.f and self._after:
            self.raiz.after_cancel(self._after);self._after=None
