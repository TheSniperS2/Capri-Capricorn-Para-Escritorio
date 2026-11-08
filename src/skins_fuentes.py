"""Lecturas de skins, sin modificar compras, equipamiento ni colas.

La observación automática conserva el foco. Una petición manual puede recuperar
Fortnite para leer la ficha que el usuario dejó abierta.
"""
import hashlib
import time
from functools import lru_cache
from reacciones_skins import Lectura,catalogo,clave
from fortnite import Pantalla,ErrorFortnite


@lru_cache(maxsize=2)
def indice_nombres(juego):
    exactos={};longitudes={}
    for s in catalogo():
        if s['juego']!=juego:continue
        for alias in {*map(clave,s['alias']),*map(clave,s['nombres'].values())}:
            if alias:exactos.setdefault(alias,{})[s['id']]=s
    for alias in exactos:longitudes.setdefault(len(alias),[]).append(alias)
    return exactos,longitudes


def resolver_nombres(juego,textos):
    """La igualdad exacta prevalece sobre parecidos a otra skin del catálogo."""
    exactos,longitudes=indice_nombres(juego);encontradas={}
    for texto in set(textos):encontradas.update(exactos.get(texto,{}))
    if encontradas:return encontradas
    from core import error_de_una_letra
    for texto in set(textos):
        for largo in (len(texto)-1,len(texto),len(texto)+1):
            if largo<8:continue
            for alias in longitudes.get(largo,()):
                if error_de_una_letra(texto,alias):encontradas.update(exactos[alias])
    return encontradas


class FuentesSkins:
    def __init__(self,cliente=None,vista=None,vista_valorant=None):
        self.cliente=cliente;self.vista=vista;self.vista_valorant=vista_valorant
        self._cliente_real=cliente is None;self.estado='Esperando una skin reconocible fuera de partida'
        self.catalogo=catalogo();self.ids={ident:s for s in self.catalogo if s['juego']=='valorant' for ident in s['ids']}

    @staticmethod
    def primer_plano():
        from escritorio import valorant_en_primer_plano,fortnite_en_primer_plano
        if valorant_en_primer_plano():return 'valorant'
        if fortnite_en_primer_plano():return 'fortnite'
        return ''

    def leer(self,juego,manual=False):
        return self._valorant(manual=manual) if juego=='valorant' else self._fortnite(manual=manual) if juego=='fortnite' else None

    def _valorant(self,manual=False):
        if self.cliente is None:
            from valorant_cliente import ClienteValorant
            self.cliente=ClienteValorant()
        c=self.cliente;yo=c.jugador
        if c.pedir('GET',f'/core-game/v1/players/{yo}') or c.pedir('GET',f'/pregame/v1/players/{yo}'):
            self.estado='En partida o selección: Capri reserva sus comentarios';return None
        # La ficha inspeccionada tiene prioridad sobre cualquier otra arma
        # equipada. No confundir "esta skin" con una favorita del inventario.
        visible=None;ficha_abierta=False
        if self.vista_valorant is not None or self._cliente_real and (manual or self.primer_plano()=='valorant'):
            if self.vista_valorant is None:
                from skins_vision import VistaValorantSkins
                self.vista_valorant=VistaValorantSkins()
            try:
                p=self.vista_valorant.capturar(activar=manual)
                ficha_abierta=self.es_ficha_valorant(p);visible=self.valorant_visible(p)
            except (ErrorFortnite,OSError):pass
        if visible or ficha_abierta:
            if c.pedir('GET',f'/core-game/v1/players/{yo}') or c.pedir('GET',f'/pregame/v1/players/{yo}'):return None
            self.estado='Ficha de Valorant reconocida' if visible else 'Muestra el nombre completo de la skin de Valorant'
            return visible
        datos=c.pedir('GET',f'/personalization/v2/players/{yo}/playerloadout')
        if not isinstance(datos,dict) or datos.get('Subject')!=yo:return None
        encontrados={}
        for gun in datos.get('Guns',[]) if isinstance(datos.get('Guns'),list) else []:
            if not isinstance(gun,dict):continue
            candidatas={self.ids[v]['id']:self.ids[v] for k in ('SkinID','SkinLevelID','ChromaID')
                        if isinstance((v:=gun.get(k)),str) and v in self.ids}
            if len(candidatas)!=1:continue
            skin=next(iter(candidatas.values()))
            if gun.get('SkinID') and gun['SkinID'] not in skin.get('padres',[skin['id']]):continue
            if gun.get('ID')==skin.get('arma_id'):encontrados[skin['id']]=skin
        # La selección puede empezar mientras se lee el equipamiento. Revalidar
        # antes de proponer el comentario evita usar una fase anterior.
        if c.pedir('GET',f'/core-game/v1/players/{yo}') or c.pedir('GET',f'/pregame/v1/players/{yo}'):
            self.estado='En partida o selección: Capri reserva sus comentarios';return None
        # No leer ni conservar cuenta, nivel, sprays, amigos, saldo o inventario.
        self.estado='Equipamiento de Valorant comprobado' if encontrados else 'No hay una skin del catálogo equipada'
        if manual and len(encontrados)>1:
            self.estado='Abre la ficha de la skin que quieres comentar';return None
        return Lectura('valorant','equipamiento',tuple(encontrados.values()),hashlib.sha256(yo.encode()).hexdigest()[:12])

    @staticmethod
    def es_ficha_valorant(p):
        return (p.contiene(('coleccion','collection','tienda','store','collection'))
                and p.contiene(('equipar','equipado','equip','equipped','variantes','variants','niveles','levels','mejorar','upgrade'))
                and not p.contiene(('encontrar partida','match found','selecciona tu agente','select your agent','fase de compra','buy phase')))

    def valorant_visible(self,p):
        if not self.es_ficha_valorant(p):return None
        ancho=p.rect[2]-p.rect[0];alto=p.rect[3]-p.rect[1]
        textos=[]
        for t in p.textos:
            # Encabezados del arma/ficha; excluir navegación, chat y cuadrícula
            # inferior de miniaturas. Solo nombres completos del catálogo.
            if not (ancho*.14<t.rect[0]<ancho*.86 and alto*.12<t.rect[1]<alto*.72):continue
            textos.append(clave(t.texto))
            for otro in p.textos:
                if 0<otro.rect[1]-t.rect[1]<t.rect[3]*1.7 and abs(otro.rect[0]-t.rect[0])<ancho*.04:
                    textos.append(clave(t.texto+' '+otro.texto))
        exactos,_=indice_nombres('valorant');posibles={}
        for n in textos:posibles.update(exactos.get(n,{}))
        if len(posibles)!=1:return None
        return Lectura('valorant','ficha',tuple(posibles.values()))

    def _fortnite(self,manual=False):
        # La observación automática no restaura el juego ni cambia el foco.
        if not manual and self.primer_plano()!='fortnite':return None
        if self.vista is None:
            from fortnite_vision import VistaFortnite
            self.vista=VistaFortnite()
        p=self.vista.capturar(activar=manual)
        lectura=self._reconocer_ficha(p)
        if manual:
            for _ in range(2):
                if lectura or self.primer_plano()!='fortnite':break
                # La restauración puede entregar primero el cuadro del cambio
                # de ventana. Repetir solo lecturas y no pedir el foco otra vez.
                time.sleep(.2);p=self.vista.capturar(activar=False);lectura=self._reconocer_ficha(p)
        self.estado='Skin visible de Fortnite reconocida' if lectura else 'Muestra la ficha de un atuendo en el casillero o la tienda'
        return lectura

    def _reconocer_ficha(self,p):
        lectura=self.fortnite_visible(p)
        if lectura:return lectura
        ampliar=getattr(self.vista,'leer_ficha',None)
        if callable(ampliar):
            try:detalle=ampliar(p)
            except (ErrorFortnite,OSError):detalle=None
            if isinstance(detalle,Pantalla):return self.fortnite_visible(detalle)
        return None

    def fortnite_visible(self,p):
        # El rótulo de casillero en la navegación existe también en el lobby;
        # exigir además una ficha de atuendo y su nombre, no un apodo del chat.
        from fortnite_vision import es_rotulo_atuendo
        acciones=('equipar','equipado','editar estilo','estilos','guardar y salir','comprar','vista previa',
                  'equip','equipped','edit style','styles','purchase','preview','usar','estilo')
        if not p.contiene(acciones):return None
        if p.contiene(('buscando partida','emparejamiento','matchmaking','tiempo restante','storm eye','ojo de la tormenta')):return None
        alto=p.rect[3]-p.rect[1];ancho=p.rect[2]-p.rect[0]
        anclas=[t for t in p.textos if es_rotulo_atuendo(t.texto)]
        if not anclas:return None
        # Las fichas de detalles tienen un único nombre; una cuadrícula con
        # varias skins del catálogo se considera ambigua y permanece en silencio.
        textos=[]
        for t in p.textos:
            if not alto*.12<t.rect[1]<alto*.92:continue
            cerca=any(abs(a.rect[0]-t.rect[0])<ancho*.16 and abs(a.rect[1]-t.rect[1])<alto*.16 for a in anclas)
            if not cerca:continue
            textos.append(clave(t.texto))
            for otro in p.textos:
                if 0<otro.rect[1]-t.rect[1]<t.rect[3]*1.7 and abs(otro.rect[0]-t.rect[0])<ancho*.04:
                    textos.append(clave(t.texto+' '+otro.texto))
        posibles=resolver_nombres('fortnite',textos)
        if len(posibles)!=1:return None
        return Lectura('fortnite','ficha',tuple(posibles.values()))
