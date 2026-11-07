"""Franja opcional de recursos integrada en la misma ventana del avatar."""
import time
from tema_ui import tk, LienzoUI, color, actual
from fuentes import FAMILIA
from idiomas import ui
from monitor_pc import MonitorPC
from monitor_diseno import dibujar_recursos


def gib(valor):return f'{valor/1024**3:.1f}'


class PanelMonitor:
    def __init__(self,app):
        self.app=app;self.root=app.root;self.monitor=MonitorPC()
        self.marco=None;self.visible=False;self.cerrado=False;self.alto=0
        self.tooltip=None;self.espera_tooltip=None;self.zona=None
        self.tarea=self.root.after(300,self.actualizar)

    def crear(self):
        self.marco=tk.Frame(self.root,bg='#010203',height=62)
        self.marco.pack_propagate(False)
        self.canvas=LienzoUI(self.marco,bg='#010203',highlightthickness=0)
        self.canvas.pack(anchor='center')
        self.canvas.bind('<Button-3>',self.app.menu)
        self.canvas.bind('<ButtonPress-1>',self.app._inicio_arrastre)
        self.canvas.bind('<B1-Motion>',self.app._arrastrar)
        # Arrastrar el monitor no debe enfocar el campo de conversación al soltar.
        self.canvas.bind('<ButtonRelease-1>',lambda e:setattr(self.app,'drag',None))
        self.canvas.bind('<Motion>',self.sobre_icono)
        self.canvas.bind('<Leave>',lambda e:self.quitar_tooltip())

    def ajustar(self):
        s=self.app.escala_avatar;alto=round(62*s);ancho=round(360*s)
        self.marco.configure(height=alto)
        self.canvas.configure(width=ancho,height=round(62*s))
        self.alto=alto
        self.app.entrada_compacta.unida=True;self.app.entrada_compacta.escala_marco=s
        self.app.entrada_compacta.dibujar()
        self.dibujar(ancho,round(62*s))

    def actualizar(self):
        if self.cerrado:return
        self.sincronizar()
        self.tarea=self.root.after(200,self.actualizar)

    def sincronizar(self):
        if self.cerrado:return
        a=self.app
        visible=(a.cfg.get('monitor_pc',False) and not a.es_personaje() and not a.intro_activa
                 and not a.saliendo and not a.cerrado and not a.transito
                 and self.root.state()=='normal' and not getattr(getattr(a,'visibilidad',None),'oculta',False))
        preparando=(a.cfg.get('monitor_pc',False) and not a.saliendo and not a.cerrado
                    and not getattr(getattr(a,'visibilidad',None),'oculta',False)
                    and ((a.intro_activa and not a.es_personaje()) or bool(a.transito)))
        self.monitor.activar(visible or preparando)
        if visible:
            if self.marco is None:self.crear()
            if not self.visible:
                self.marco.pack(fill='x',before=a.entrada_compacta)
                self.visible=True
                self.ajustar();a.aplicar_escala()
            self.ajustar()
        elif self.visible:self.ocultar()

    def dibujar(self,ancho,alto):
        d=self.monitor.datos
        caducado=not d.get('fecha') or time.monotonic()-d['fecha']>6
        llave=(d.get('fecha'),ancho,alto,actual(),caducado)
        if getattr(self,'pintado',None)==llave:return
        self.pintado=llave
        if caducado:d={}
        self.canvas.delete('all')
        dibujar_recursos(self.canvas,d,ancho/360)
        self.canvas.scale('all',0,0,ancho/360,alto/62)

    def sobre_icono(self,e):
        zona=min(3,max(0,int(e.x/max(1,self.canvas.winfo_width())*4)))
        if zona==self.zona:return
        self.quitar_tooltip();self.zona=zona
        self.espera_tooltip=self.root.after(550,lambda:self.mostrar_tooltip(zona))

    def mostrar_tooltip(self,zona):
        self.espera_tooltip=None
        if not self.visible:return
        d=self.monitor.datos
        if not d.get('fecha') or time.monotonic()-d['fecha']>6:d={}
        textos=['CPU · Uso total del procesador','RAM · Memoria del computador',
                'GPU · Motor gráfico más ocupado','VRAM · Memoria gráfica dedicada utilizada']
        texto=ui(textos[zona])
        if zona==1 and d.get('ram_total'):texto+=f"\n{gib(d['ram_used'])} / {gib(d['ram_total'])} GB"
        if zona==3 and d.get('shared') is not None:texto+='\n'+ui('RAM compartida: {0} GB · aparte de la VRAM').format(gib(d['shared']))
        v=self.tooltip=tk.Toplevel(self.root);v.withdraw();v.overrideredirect(True);v.attributes('-topmost',True)
        tk.Label(v,text=texto,bg='#100b18',fg='#eff7ff',font=(FAMILIA,9),padx=10,pady=6,
                 wraplength=260,justify='left',relief='solid',borderwidth=1).pack()
        v.update_idletasks()
        x=max(0,min(self.root.winfo_screenwidth()-v.winfo_reqwidth(),self.canvas.winfo_rootx()))
        v.geometry(f'+{x}+{max(0,self.marco.winfo_rooty()-v.winfo_reqheight()-4)}');v.deiconify()

    def quitar_tooltip(self):
        if self.espera_tooltip:self.root.after_cancel(self.espera_tooltip);self.espera_tooltip=None
        if self.tooltip is not None:self.tooltip.destroy();self.tooltip=None
        self.zona=None

    def ocultar(self):
        self.quitar_tooltip();self.monitor.activar(False)
        self.app.entrada_compacta.unida=False
        self.app.entrada_compacta.dibujar()
        if self.marco is not None:self.marco.pack_forget()
        estaba=self.visible;self.visible=False
        if estaba and not self.app.es_personaje() and not self.app.intro_activa and not self.app.transito and not self.app.saliendo:
            self.app.aplicar_escala()

    def cerrar(self):
        if self.cerrado:return
        self.ocultar();self.cerrado=True;self.monitor.cerrar()
        if self.tarea:self.root.after_cancel(self.tarea);self.tarea=None
        if self.marco is not None:self.marco.destroy();self.marco=None
