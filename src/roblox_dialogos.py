"""Personalidad de Capri para Roblox. Gustos ficticios y consistentes por outfit."""
from idiomas import codigo,idioma_actual

PERFILES={
 'clasica':('Capri clásica','Classic Capri','Capri clássica','いつものカプリ'),
 'terror':('Terror','Horror','Terror','ホラー'),
 'aventura':('Aventura','Adventure','Aventura','冒険'),
 'estilo':('Estilo','Style','Estilo','スタイル'),
 'discreta':('Discreta','Quiet','Discreta','控えめ'),
}

def elegir(opciones,idioma=None):return opciones[('es','en','pt','ja').index(codigo(idioma or idioma_actual()))]

def opinion(avatar,idioma=None):
    bancos=(
      ('Ese outfit sí tiene presencia. Parece que entras a la experiencia con tu propia música de jefe final. Me gusta.',
       'That outfit has presence. You look ready to enter with your own boss music. I like it.',
       'Esse visual tem presença. Parece que você entra com sua própria música de chefão. Gostei.',
       'そのコーデ、存在感あるね。専用のボス曲と一緒に登場しそう。好きだよ。'),
      ('Tiene personalidad. Para mí está en un punto tranquilo: no es mi favorito, pero tampoco necesita luces de neón para funcionar.',
       'It has personality. It feels understated to me: not my favorite, but it does not need neon lights to work.',
       'Tem personalidade. Para mim é discreto: não é meu favorito, mas não precisa de neon para funcionar.',
       '個性はあるね。私には落ち着いた印象。お気に入りではないけど、ネオンがなくてもいいと思う。'),
      ('Este conjunto no termina de convencerme. Yo probaría otra combinación de accesorios; mi gusto tiene bastante interferencia cyberpunk.',
       'This outfit does not quite win me over. I would try another accessory combination; my taste comes with plenty of cyberpunk interference.',
       'Esse conjunto não me convenceu muito. Eu tentaria outra combinação de acessórios; meu gosto tem bastante interferência cyberpunk.',
       'この組み合わせは、私の好みには少し合わないかな。別のアクセサリーの組み合わせを試したい。私の好みはかなりサイバーパンク寄りだけどね。'))
    from roblox_info import ubicacion
    import hashlib
    piezas=[p for p in avatar.get('piezas',[]) if ubicacion(p) and p.get('nombre')]
    if not piezas:return elegir(bancos[avatar['gusto']],idioma)
    orden={'hombro':0,'espalda':1,'rostro':2,'cabeza':3,'cuello':4,'frente':5,'cintura':6,'cabello':7}
    piezas=sorted(piezas,key=lambda p:(orden.get(ubicacion(p),8),str(p['id'])))[:3]
    zonas={
        'hombro':('En el hombro llevas «{0}».','On your shoulder you have “{0}”.','No ombro você usa «{0}».','肩には「{0}」が付いているね。'),
        'espalda':('En la espalda llevas «{0}».','On your back you have “{0}”.','Nas costas você usa «{0}».','背中には「{0}」が付いているね。'),
        'rostro':('El accesorio del rostro es «{0}».','Your face accessory is “{0}”.','O acessório do rosto é «{0}».','顔のアクセサリーは「{0}」だね。'),
        'cabeza':('En la cabeza llevas «{0}».','On your head you have “{0}”.','Na cabeça você usa «{0}».','頭には「{0}」を付けているね。'),
        'cuello':('En el cuello llevas «{0}».','Around your neck you have “{0}”.','No pescoço você usa «{0}».','首には「{0}」を付けているね。'),
        'otro':('También llevas «{0}».','You are also wearing “{0}”.','Você também usa «{0}».','「{0}」も身に付けているね。')}
    gustos=(
        ('Ese sí me gusta: lo dejaría como una de las piezas protagonistas de tu outfit.','I like that one: I would keep it as one of your outfit’s main pieces.','Desse eu gosto: deixaria como uma das peças principais do visual.','これは好き。コーデの主役として残したいな。'),
        ('Ese detalle me resulta más discreto; lo conservaría, aunque no es mi favorito del conjunto.','That detail feels more understated to me; I would keep it, although it is not my favorite piece.','Esse detalhe é mais discreto para mim; manteria, embora não seja meu favorito.','これは控えめな印象。残してもいいけど、一番のお気に入りではないかな。'),
        ('Ese accesorio no me convence tanto; yo probaría el conjunto sin él antes de cambiar lo demás.','That accessory does not quite work for me; I would try the outfit without it before changing anything else.','Esse acessório não me convence tanto; testaria o visual sem ele antes de mudar o resto.','このアクセサリーは少し好みと違うかな。他を変える前に、外したコーデも試してみたい。'))
    partes=[]
    for p in piezas:
        gusto=int(hashlib.sha256(str(p['id']).encode()).hexdigest()[:8],16)%3
        partes.append(elegir(zonas.get(ubicacion(p),zonas['otro']),idioma).format(p['nombre'])+' '+elegir(gustos[gusto],idioma))
    return elegir(('Me fijé en estos detalles de tu outfit:','These details caught my attention in your outfit:','Reparei nestes detalhes do seu visual:','コーデのこの辺りが気になったよ。'),idioma)+' '+' '.join(partes)

def reaccion(evento,perfil='clasica',idioma=None):
    if evento=='duda':return elegir(('Vi que apareció el aviso de fin, pero no quedó claro el resultado. ¿Ganaste, perdiste o moriste?',
                                    'I saw an end message, but the result was unclear. Did you win, lose or die?',
                                    'Vi um aviso de fim, mas o resultado não ficou claro. Você ganhou, perdeu ou morreu?',
                                    '終了の表示は見えたけど結果が分からなかった。勝った？負けた？それとも倒れた？'),idioma)
    bancos={
     'victoria':{
       'clasica':('¡Eso es! Otra victoria para el registro, choom. Te guardo los aplausos; la próxima no viene regalada.',
          'That is it! Another win for the log, choom. Enjoy the applause; the next one still needs earning.',
          'É isso! Mais uma vitória no registro, choom. Aproveite os aplausos; a próxima ainda precisa ser conquistada.',
          'やったね！記録にまた一勝、チューム。拍手は君のもの。次も気を抜かずにね。'),
       'terror':('Saliste de esa. Bien. Ahora deja de mirar atrás... mejor reviso yo la puerta.',
          'You made it through. Good. Stop looking behind you... I will keep an eye on the door.',
          'Você saiu dessa. Ótimo. Pare de olhar para trás... eu fico de olho na porta.',
          '切り抜けたね。よかった。後ろばかり見ないで……扉は私が見ておく。'),
       'aventura':('¡Ruta completada! Si alguien pregunta, tu guía digital fue absolutamente indispensable.',
          'Route complete! If anyone asks, your digital guide was absolutely indispensable.',
          'Rota concluída! Se alguém perguntar, sua guia digital foi absolutamente indispensável.',
          'ルート攻略！誰かに聞かれたら、デジタルガイドの活躍が欠かせなかったって言ってね。'),
       'estilo':('Victoria y presencia. Me gusta cuando el resultado también combina con la actitud.',
          'Victory and presence. I like it when the result matches the attitude.',
          'Vitória e presença. Gosto quando o resultado combina com a atitude.',
          '勝利も存在感もばっちり。結果と雰囲気が揃うのっていいね。')},
     'derrota':{'clasica':('Esta se escapó. Respira, reajusta el plan y vuelve cuando tengas ganas. Yo sigo de tu lado.',
          'This one got away. Breathe, adjust your plan and return when you feel ready. I am still on your side.',
          'Essa escapou. Respire, ajuste o plano e volte quando quiser. Continuo do seu lado.',
          '今回は逃したね。一息ついて、作戦を見直そう。また挑みたくなったらね。私は味方だよ。')},
     'muerte':{'clasica':('Este intento llegó hasta aquí. Te guardo el orgullo mientras preparas el siguiente.',
          'That is where this attempt ended. I will look after your pride while you prepare the next one.',
          'Essa tentativa terminou aqui. Cuido do seu orgulho enquanto você prepara a próxima.',
          '今回はここまでだったね。次の挑戦を準備する間、プライドは私が預かっておく。'),
       'terror':('De acuerdo... esa sí me dio un pequeño fallo de señal. Tomémonos un segundo.',
          'All right... that one gave me a small signal glitch. Let us take a second.',
          'Certo... essa me deu uma pequena falha de sinal. Vamos respirar um segundo.',
          'うん……今のはちょっと信号が乱れた。一息つこう。')},
    }
    if perfil=='discreta':return elegir({'victoria':('Bien jugado, choom.','Well played, choom.','Bem jogado, choom.','よくやったね、チューム。'),
                                       'derrota':('Aquí sigo contigo.','I am still here with you.','Continuo aqui com você.','そばにいるよ。'),
                                       'muerte':('Un respiro y seguimos.','Take a breath, then continue.','Respire e seguimos.','一息ついて、また行こう。')}[evento],idioma)
    opciones=bancos[evento]
    return elegir(opciones.get(perfil,opciones['clasica']),idioma)

def contexto(datos):
    """El perfil describe a Capri; la nota sigue siendo un dato aportado por el usuario."""
    estilo={
        'clasica':'Curiosa y juguetona; conserva tu personalidad normal.',
        'terror':'La descripción o categoría pública indica terror. Eres una compañera atenta y discreta. Humor suave, sin inventar sustos ni afirmar que viste un enemigo.',
        'aventura':'Compañera entusiasta de aventura. Anima sin inventar avances, recompensas o victorias.',
        'estilo':'Compañera interesada en la creatividad y los conjuntos. No inventes prendas que no se hayan consultado.',
        'discreta':'Responde brevemente, sin ofrecer otra pregunta innecesaria.',
    }
    return {**datos,'tono_de_capri':estilo.get(datos.get('perfil'),estilo['clasica'])}
