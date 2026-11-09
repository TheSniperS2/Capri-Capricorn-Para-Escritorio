"""Navegación de ajustes: juego y categoría, compartiendo el scroll principal."""
from tema_ui import tk
from ajustes_ui import SelectorCyber,BotonCyber,FONDO,TARJETA,TEXTO,SUAVE,ACENTO
from fuentes import FAMILIA
from idiomas import ui

JUEGOS=(('lol','League of Legends'),('valorant','Valorant'),('fortnite','Fortnite'),
        ('cs2','Counter-Strike'),('roblox','Roblox'))
TEXTOS=('Partidas, personajes y avisos organizados por juego.','Juego','Partidas','Skins','Avisos',
        'Búsqueda, aceptación y prioridades de campeones por línea.',
        'Búsqueda y hasta tres agentes por orden de preferencia.',
        'Modo de juego, tamaño del equipo y búsqueda de partida.',
        'Mapas preferidos y búsqueda de partida.',
        'Experiencias favoritas, avatar y reacciones a lo que juegas.',
        'Abre el panel del juego para ajustar sus opciones y controlar las partidas.')


class AjustesJuegos:
    def __init__(self,padre,seleccion='lol',al_cambiar=None):
        self.padre=padre;self.al_cambiar=al_cambiar or (lambda:None)
        self.actual=None;self.paginas={};self.navegacion={};self.pestanas={};self.elegidas={}
        tk.Label(padre,text=ui('Juego'),bg=FONDO,fg=TEXTO,font=(FAMILIA,11,'bold')).pack(anchor='w',pady=(0,6))
        self.selector=SelectorCyber(padre,values=[v for k,v in JUEGOS])
        self.selector.pack(fill='x',pady=(0,14))
        self.selector.bind('<<ComboboxSelected>>',lambda e:self.mostrar(JUEGOS[self.selector.current()][0]))
        for juego,nombre in JUEGOS:
            pagina=tk.Frame(padre,bg=FONDO);self.paginas[juego]=pagina
            nav=tk.Frame(pagina,bg=FONDO);self.navegacion[juego]=nav
        self.mostrar(seleccion if seleccion in self.paginas else 'lol')

    def seccion(self,juego,nombre):
        pagina=self.paginas[juego]
        f=tk.Frame(pagina,bg=FONDO)
        boton=BotonCyber(self.navegacion[juego],text=nombre,command=lambda:self.mostrar(juego,nombre),
                        bg=TARJETA,fg=SUAVE,font=(FAMILIA,10,'bold'),pady=8)
        boton.pack(side='left',fill='x',expand=True,padx=(0,6))
        self.pestanas[juego,nombre]=(f,boton)
        if juego not in self.elegidas:self.elegidas[juego]=nombre;f.pack(fill='x');boton.configure(fg=TEXTO,bg='#421327')
        else:self.navegacion[juego].pack(fill='x',pady=(0,14),before=self.pestanas[juego,self.elegidas[juego]][0])
        return f

    def mostrar(self,juego,pestana=None):
        if self.actual:self.paginas[self.actual].pack_forget()
        self.actual=juego;self.selector.current([k for k,v in JUEGOS].index(juego))
        if pestana is not None and (juego,pestana) in self.pestanas:
            anterior=self.elegidas.get(juego)
            if anterior:
                f,b=self.pestanas[juego,anterior];f.pack_forget();b.configure(bg=TARJETA,fg=SUAVE)
            self.elegidas[juego]=pestana
            f,b=self.pestanas[juego,pestana];f.pack(fill='x');b.configure(bg='#421327',fg=TEXTO)
        self.paginas[juego].pack(fill='x')
        self.padre._root().after_idle(lambda:self.al_cambiar() if self.padre.winfo_exists() else None)
