"""Elección de voz inglesa sin alterar las voces de los demás idiomas."""
from tema_ui import tk
from ajustes_ui import SelectorCyber,FONDO,TEXTO,SUAVE
from fuentes import FAMILIA
from idiomas import ui

TEXTOS=(
    'Voz por idioma, volumen y velocidad de Capri.','Voz en inglés',
    'Responde con menos espera. Necesita internet.',
    'Tarda más en preparar cada respuesta.',
    'Esta voz no está disponible en este equipo. Se usará la voz habitual.',
)


class OpcionesVoz(tk.Frame):
    def __init__(self,padre,config,guardar):
        super().__init__(padre,bg=FONDO)
        self.cfg=config;self.guardar=guardar
        self.titulo=tk.Label(self,bg=FONDO,fg=TEXTO,font=(FAMILIA,13,'bold'))
        self.ingles=tk.Frame(self,bg=FONDO)
        self.selector=SelectorCyber(self.ingles,values=('Capri V1','Capri V2'))
        self.selector.pack(fill='x',pady=(0,10))
        self.selector.bind('<<ComboboxSelected>>',lambda e:self.guardar('voz_ingles_modo',('rapida','local')[self.selector.current()]))
        self.descripcion=tk.Label(self,bg=FONDO,fg=SUAVE,font=(FAMILIA,9),justify='left',anchor='w')
        self.pie=tk.Frame(padre,bg=FONDO)
        self.aviso=tk.Label(self.pie,bg=FONDO,fg=SUAVE,font=(FAMILIA,9),justify='left',anchor='w')
        self.bind('<Configure>',self.adaptar)
        self.actualizar()

    def adaptar(self,e):
        ancho=max(180,e.width-30)
        for etiqueta in (self.descripcion,self.aviso):etiqueta.configure(wraplength=ancho)

    def actualizar(self):
        from voz_local import disponible,rapida_disponible
        idioma=self.cfg.get('idioma','es');modo=self.cfg.get('voz_ingles_modo','rapida')
        if idioma=='en':
            self.titulo.pack(anchor='w',pady=(0,8))
            self.titulo.configure(text=ui('Voz en inglés'))
            self.ingles.pack(fill='x')
            self.selector.current(0 if modo=='rapida' else 1)
            self.descripcion.pack(fill='x')
            self.descripcion.configure(text=ui(TEXTOS[2] if modo=='rapida' else TEXTOS[3]))
            lista=rapida_disponible() if modo=='rapida' else disponible()
            if lista:self.aviso.pack_forget()
            else:self.aviso.configure(text=ui(TEXTOS[4]));self.aviso.pack(fill='x',pady=(4,0))
        else:
            self.titulo.pack_forget()
            self.ingles.pack_forget()
            self.descripcion.pack_forget()
            self.aviso.pack_forget()
