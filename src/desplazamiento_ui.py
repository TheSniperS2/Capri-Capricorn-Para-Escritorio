"""Desplazamiento local con barra discreta. La rueda nunca mueve otro panel."""
from tema_ui import tk,LienzoUI

class Desplazable(tk.Frame):
    def __init__(self,padre,bg='#10090d',**kw):
        super().__init__(padre,bg=bg,**kw)
        self.lienzo=LienzoUI(self,bg=bg,highlightthickness=0,yscrollincrement=1)
        self.lienzo.pack(side='left',fill='both',expand=True)
        self.barra=LienzoUI(self,width=7,bg=bg,highlightthickness=0,cursor='hand2')
        self.interior=tk.Frame(self.lienzo,bg=bg);self.item=self.lienzo.create_window(0,0,window=self.interior,anchor='nw')
        self.fraccion=(0.,1.);self.arrastre=None;self.restante=0
        self.lienzo.configure(yscrollcommand=self.actualizar_barra)
        self.lienzo.bind('<Configure>',self.ajustar);self.interior.bind('<Configure>',self.ajustar)
        self.barra.bind('<Configure>',lambda e:self.pintar_barra())
        self.barra.bind('<Button-1>',self.pulsar);self.barra.bind('<B1-Motion>',self.arrastrar)
        self.tag='CapriScroll'+str(id(self));self.bind_class(self.tag,'<MouseWheel>',self.rueda)
        self.bind_class(self.tag,'<Button-4>',lambda e:self.mover(-3));self.bind_class(self.tag,'<Button-5>',lambda e:self.mover(3))
        self.bind('<Destroy>',self.destruir,add='+');self.conectar()
    def destruir(self,e):
        if e.widget==self:
            for evento in ('<MouseWheel>','<Button-4>','<Button-5>'):self.unbind_class(self.tag,evento)
    def conectar(self,w=None):
        w=w or self
        if self.tag not in w.bindtags():w.bindtags((self.tag,)+w.bindtags())
        for hijo in w.winfo_children():self.conectar(hijo)
    def ajustar(self,e=None):
        ancho=max(1,self.lienzo.winfo_width());visible=max(1,self.lienzo.winfo_height())
        self.lienzo.itemconfigure(self.item,width=ancho)
        alto=max(1,self.interior.winfo_reqheight())
        # Tk permite desplazar una región más pequeña que la vista hacia coordenadas
        # negativas. La región mínima ocupa toda la vista, con el contenido arriba.
        self.lienzo.configure(scrollregion=(0,0,ancho,max(visible,alto)))
        if alto<=visible:
            self.lienzo.yview_moveto(0);self.restante=0;self.arrastre=None
    def actualizar_barra(self,a,b):
        self.fraccion=float(a),float(b)
        if float(b)-float(a)<.999:self.barra.pack(side='right',fill='y',padx=(7,0))
        else:self.barra.pack_forget()
        self.pintar_barra()
    def limites(self):
        h=max(1,self.barra.winfo_height());a,b=self.fraccion
        alto=min(h,max(28,(b-a)*h));y=(h-alto)*a/max(.0001,1-(b-a))
        return y,y+alto
    def pintar_barra(self):
        self.barra.delete('all');a,b=self.limites()
        self.barra.create_line(3,a+3,3,max(a+3,b-3),fill='#925c83',width=4,capstyle='round')
    def pulsar(self,e):
        a,b=self.limites()
        if a<=e.y<=b:self.arrastre=(e.y,self.fraccion[0])
        else:self.lienzo.yview_moveto(max(0,e.y/max(1,self.barra.winfo_height())-(self.fraccion[1]-self.fraccion[0])/2));self.arrastre=None
    def arrastrar(self,e):
        if self.arrastre:
            y,f=self.arrastre;self.lienzo.yview_moveto(f+(e.y-y)/max(1,self.barra.winfo_height()))
    def mover(self,n):
        if self.interior.winfo_reqheight()<=self.lienzo.winfo_height():
            self.lienzo.yview_moveto(0);self.restante=0
        else:self.lienzo.yview_scroll(n*18,'units')
        return 'break'
    def rueda(self,e):
        self.restante-=e.delta/120*3
        pasos=int(self.restante);self.restante-=pasos
        if pasos:self.mover(pasos)
        return 'break'
