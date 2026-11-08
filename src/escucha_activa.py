"""Turnos de escucha opcional, sin abrir micrófonos ni ejecutar órdenes."""
import re
import time

MODOS=('nombre','preguntas','continua')
OPCIONES=('Desactivada','Después de una pregunta','Escucha activa')
TEXTOS=('Escucha sin decir «Capri»',*OPCIONES,
        'Después de una pregunta: espera tu respuesta durante 15 segundos.',
        'Escucha activa: puedes hablar sin decir su nombre. Se pausa mientras Capri responde o escribes.',
        'Esc pausa la escucha activa. Di «Capri» o pulsa tu tecla para hablar para retomarla.',
        'El reconocimiento se procesa en este equipo. No se guardan grabaciones.',
        'Preparando escucha…','Habla sin decir «Capri»','Responde sin decir «Capri»',
        'Habla o escribe…','ESCUCHA ACTIVA','Escucha activa pausada',
        'No pude mantener la escucha activa. Puedes usar Hablar. ')


def normalizar(modo):return modo if isinstance(modo,str) and modo in MODOS else 'nombre'


def es_pregunta(texto):
    # Una pregunta citada o un ejemplo de código no abre otro turno por sí solo.
    texto=re.sub(r'```.*?```','',str(texto),flags=re.S)
    texto=re.sub(r'`[^`\n]*`','',texto)
    texto=re.sub(r'«[^»]*»|“[^”]*”|"[^"\n]*"','',texto)
    texto=re.sub(r'https?://[^\s<>]+','',texto,flags=re.I)
    texto=re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0E\uFE0F\u200D]','',texto)
    # Puede seguir una despedida o comentario: «¿Quieres una historia? ¡Espero
    # tu respuesta!». Se escucha al terminar TODO el mensaje, no a mitad de él.
    return bool(re.search(r'[?？]',texto))


class EscuchaActiva:
    ESPERA=15
    def __init__(self,modo='nombre',reloj=time.monotonic):
        self.reloj=reloj;self.configurar(modo)

    def configurar(self,modo):
        self.modo=normalizar(modo);self.pausada=False;self.cancelar();self.no_antes=0

    def cancelar(self):self.ticket=None;self.hasta=0

    def pausar(self):self.pausada=True;self.cancelar()

    def reanudar(self):self.pausada=False;self.cancelar()

    def preparar(self,ticket,texto,con_voz):
        self.cancelar()
        if self.modo=='preguntas' and not self.pausada and es_pregunta(texto):self.ticket=ticket
        if not con_voz:self.fin_voz(ticket)

    def fin_voz(self,ticket):
        # Dejar que termine la cola de audio antes de abrir el micrófono.
        self.no_antes=self.reloj()+.4
        if self.modo=='preguntas' and not self.pausada and self.ticket is not None and self.ticket==ticket:
            self.hasta=self.no_antes+self.ESPERA;self.ticket=None

    def tipo(self):
        if self.modo=='nombre' or self.pausada:return 'nombre'
        if self.reloj()<self.no_antes:return None
        if self.modo=='continua':return 'continua'
        return 'preguntas' if self.reloj()<self.hasta else 'nombre'

    def espera(self):
        return max(0,self.hasta-self.reloj()) if self.tipo()=='preguntas' else None


def crear_opciones(padre,config,guardar):
    from tema_ui import tk
    from ajustes_ui import SelectorCyber,FONDO,SUAVE,ACENTO
    from fuentes import FAMILIA
    from idiomas import ui
    tk.Label(padre,text=ui(TEXTOS[0]),bg=FONDO,fg=ACENTO,font=(FAMILIA,12,'bold')).pack(anchor='w',pady=(16,5))
    selector=SelectorCyber(padre,values=OPCIONES)
    selector.current(MODOS.index(normalizar(config.get('modo_escucha'))));selector.pack(fill='x',pady=(0,5))
    selector.bind('<<ComboboxSelected>>',lambda e:guardar('modo_escucha',MODOS[selector.current()]))
    for texto in TEXTOS[4:8]:
        tk.Label(padre,text=ui(texto),bg=FONDO,fg=SUAVE,font=(FAMILIA,9),wraplength=460,justify='left').pack(anchor='w',pady=(3,0))
    return selector
