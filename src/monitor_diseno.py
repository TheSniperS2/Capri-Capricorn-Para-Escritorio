"""Mismo dise?o vectorial para Tk y los fotogramas de animaci?n."""
from tema_ui import color
from fuentes import FAMILIA

def gib(valor):return f'{valor/1024**3:.1f}'

def icono(c,clave,x,y,tinta):
    """Iconos vectoriales: CPU, módulo RAM, tarjeta gráfica y memoria de vídeo."""
    def linea(*p):c.create_line(*p,fill=tinta,width=1.3)
    def caja(*p):c.create_rectangle(*p,outline=tinta,width=1.3)
    if clave=='cpu':
        caja(x-7,y-7,x+7,y+7);caja(x-3,y-3,x+3,y+3)
        for d in (-4,0,4):
            linea(x+d,y-10,x+d,y-7);linea(x+d,y+7,x+d,y+10)
            linea(x-10,y+d,x-7,y+d);linea(x+7,y+d,x+10,y+d)
    elif clave=='ram':
        caja(x-10,y-6,x+10,y+5)
        for d in (-6,0,6):caja(x+d-1.5,y-3,x+d+1.5,y+2)
        for d in (-7,-3,1,5,9):linea(x+d,y+5,x+d,y+8)
    elif clave=='gpu':
        caja(x-10,y-7,x+9,y+6);linea(x-12,y-9,x-12,y+9)
        c.create_oval(x-5,y-5,x+5,y+5,outline=tinta,width=1.3)
        linea(x,y-4,x,y+4);linea(x-4,y,x+4,y);linea(x-6,y+7,x+5,y+7)
    else:
        for d in (-4,4):
            caja(x-9,y+d-3,x+9,y+d+2)
            for z in (-5,0,5):linea(x+z,y+d-1,x+z+1,y+d-1)


def dibujar_recursos(c,d,escala_fuente=1):
    s=escala_fuente
    def fuente(tamano,*estilo):return (FAMILIA,max(6,round(tamano*s)),*estilo)
    c.create_rectangle(8,0,352,62,fill=color('#120b10'),outline='')
    for x in (8,352):c.create_line(x,0,x,62,fill=color('#8e304a'))
    c.create_line(21,0,339,0,fill=color('#8e304a'))
    c.create_line(21,59,339,59,fill=color('#8e304a'))
    for i,(clave,titulo) in enumerate((('cpu','CPU'),('ram','RAM'),('gpu','GPU'),('vram','VRAM'))):
        x=24+i*80;v=d.get(clave)
        tinta='#ffc466' if clave!='vram' and v is not None and v>=85 else '#ff9eaf'
        if i:c.create_line(x-4,13,x-4,48,fill=color('#44202d'))
        icono(c,clave,x+13,27,color(tinta))
        c.create_text(x+29,15,text=titulo,anchor='w',fill=color('#b2a4be'),font=fuente(7))
        valor='—' if v is None else (gib(v)+'G' if clave=='vram' else f'{v:.0f}%')
        c.create_text(x+29,32,text=valor,anchor='w',fill=color('#eff7ff'),font=fuente(11,'bold'))
        if clave!='vram':
            for j in range(10):
                lleno=v is not None and j<v/10
                c.create_rectangle(x+2+j*6,49,x+6+j*6,52,
                                   fill=color(tinta if lleno else '#35101d'),outline='')
        else:
            c.create_text(x+2,50,text='GB dedicados',anchor='w',fill=color('#897d98'),font=fuente(6))
