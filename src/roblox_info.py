"""Interpretación local de información pública; nunca adivina sucesos de una partida."""
import re
import unicodedata

def limpio(t):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(t).casefold()) if unicodedata.category(c)!='Mn').split())

def perfil_automatico(info):
    categoria=' '.join(str(info.get(k,'')) for k in ('genero','subgenero','genero_original'))
    descripcion=re.sub(r'https?://\S+','',str(info.get('descripcion','')))
    t=limpio(categoria+' '+str(info.get('nombre',''))+' '+descripcion)
    # Terror explícito prima sobre etiquetas antiguas como Adventure/Survival.
    grupos=(('terror',r'\b(horror|terror|scary|jumpscares?|haunted|pesadillas?|nightmares?)\b'),
            ('estilo',r'\b(fashion|dress up|dressup|outfits?|moda|vestir|pasarela|runway|styling|makeover)\b'),
            ('aventura',r'\b(adventure|aventura|obby|platformer|exploration|explorar|quest|rpg|open world)\b'),
            ('discreta',r'\b(puzzle|relaxing|relajante|hangout|cozy|meditation)\b'))
    for perfil,patron in grupos:
        if re.search(patron,t):return perfil
    return 'clasica'

# Tipos oficiales AvatarAssetType. La posición procede del tipo, no del nombre.
TIPOS={2:'camiseta',8:'cabeza',11:'camisa',12:'pantalones',19:'equipamiento',41:'cabello',42:'rostro',43:'cuello',
       44:'hombro',45:'frente',46:'espalda',47:'cintura',64:'camiseta',65:'camisa',66:'pantalones',67:'chaqueta',
       68:'sueter',69:'shorts',70:'calzado',71:'calzado',72:'falda'}
POR_NOMBRE={'hat':'cabeza','hairaccessory':'cabello','faceaccessory':'rostro','neckaccessory':'cuello',
            'shoulderaccessory':'hombro','frontaccessory':'frente','backaccessory':'espalda','waistaccessory':'cintura',
            'shirt':'camisa','pants':'pantalones','tshirt':'camiseta','jacketaccessory':'chaqueta'}

def ubicacion(pieza):
    tipo=pieza.get('tipo_id')
    return (TIPOS.get(tipo) if type(tipo) is int else None) or POR_NOMBRE.get(limpio(pieza.get('tipo','')).replace(' ',''))

REGLAS_AUTOMATICAS={
 'victoria':'victory|you win|you won|winner|round won|victoria|has ganado|ganaste|vitoria|voce venceu|勝利',
 'derrota':'defeat|you lose|you lost|round lost|derrota|has perdido|perdiste|voce perdeu|敗北',
 'muerte':'you died|you are dead|you have died|has muerto|moriste|voce morreu|死亡',
 'duda':'game over|round over|match over|fin de la partida|partida terminada|fim de jogo|ゲームオーバー',
}

def resolver_resultado(texto):
    t=limpio(texto).strip(' .!?¿¡…')
    for evento,frases in {'victoria':('si','si gane','gane','ganamos','ganamos la partida','venci'),
                         'derrota':('perdi','perdimos','perdi la partida'),
                         'muerte':('mori','me mori','he muerto','morimos')}.items():
        if t in frases:return evento
    return None
