"""Comentarios originales de Capri. No describen acciones ni conceden ventajas."""
import hashlib

ESPECIALES={
 'rgx':('Neón, circuitos y cero discreción. Esa RGX sí habla mi idioma, choom.',
        'La RGX parece diseñada para una persecución por Night City. Mis circuitos aprueban.'),
 'glitchpop':('Glitchpop. Colores imposibles y una saludable falta de sutileza. Me representa.',
             'Ese diseño Glitchpop tiene mi misma energía: demasiadas luces para pasar desapercibido.'),
 'protocol':('¿Una Protocol con voz propia? Competencia interesante. Yo tengo mejores chistes.',
             'La Protocol parece pedir una contraseña antes de dejarte recargar. Muy de mi estilo.'),
 'spectrum':('Spectrum. Si esto fuera una fiesta, yo ya estaría haciendo las luces.',
             'Esa Spectrum tiene estética de canción que te hace subir el volumen. Aprobada.'),
 'neo':('Neo Frontier. Un duelo al atardecer, pero con demasiados circuitos. Bonita combinación.',
        'Ese estilo de vaquero del futuro tiene una cantidad peligrosamente buena de personalidad.'),
 'radiant':('Esa Radiant Entertainment parece escapada de una recreativa. Yo pongo la siguiente moneda.',
            'Píxeles, luces y una entrada dramática. Esta sí que sabe ganarse mi atención.'),
 'kuronami':('Kuronami. Lluvia, acero y elegancia innecesaria. Justo la cantidad de drama que me gusta.',
             'Ese diseño Kuronami tiene presencia de personaje que llega tarde y aun así se roba la escena.'),
 'oni':('La Oni no necesita hablar para tener presencia. Esa máscara hace todo el trabajo.',
        'Máscara, detalles y una actitud impecable. La Oni se ganó mi sello de aprobación.'),
 'reaver':('La Reaver tiene estética de invocar problemas. Hazle un huequito a mi lado.',
           'Ese diseño Reaver parece acompañado por un coro siniestro. Elegancia con malas intenciones.'),
 'araxys':('Araxys. Parece que va a abrir un portal al recargar. Me gusta ese nivel de dramatismo.',
           'Ese diseño alienígena tiene cara de no haber leído el manual de este planeta. Somos dos.'),
 'prelude':('Preludio del Caos. Alguien le puso ese nombre y yo me sentí aludida.',
            'Esa skin tiene una cantidad industrial de caos. Por fin, decoración compatible conmigo.'),
 'chronovoid':('ChronoVoid. Elegante, extraña y con pinta de doblar la realidad. Buena elección.',
              'Ese diseño parece contener una pequeña anomalía. Yo también vengo con una.'),
 'prime':('La Prime tiene pinta de arreglarse antes de un duelo. Ese nivel de estilo se respeta.',
          'Líneas limpias y mucha presencia. La Prime sabe destacar sin montar un espectáculo.'),
 'gaia':('La Venganza de Gaia parece sacada de un bosque con carácter. Preciosa.',
         'Naturaleza con actitud. Ese diseño hace que hasta mis circuitos quieran echar raíces.'),
 'elderflame':('Un dragón por arma. Yo también habría elegido la opción ridículamente espectacular.',
              'Elderflame. Si vas a ser dramático, al menos hazlo con un dragón. Respeto absoluto.'),
 'evori':('Mariposas y pólvora. Caos con brillantina: una combinación peligrosamente adorable.',
          'Evori tiene una cantidad sospechosamente eficaz de ternura. Mis defensas han caído.'),
 'sentinels':('Centinelas de la Luz. Ese diseño tiene energía de entrada heroica con cámara lenta.',
              'Brilla como si tuviera banda sonora propia. Esa presencia está muy bien conseguida.'),
 'origin':('Origen. Geometría extraña y tecnología que parece magia. Mis dos debilidades.',
           'Ese diseño parece construido con una ecuación prohibida. Me lo quedo mirando un segundo.'),
 'v':('V. Ahora sí se siente un poquito más cerca Night City. Qué buena presencia.',
       'V en la isla. Me falta un letrero de neón y ya tengo el ambiente perfecto.'),
 'johnny':('Johnny Silverhand. Si empieza un concierto en el lobby, yo hago las luces.',
            'Silverhand llegó con actitud de no pedir permiso. Esa entrada merece una guitarra.'),
 'lucy':('Lucy. Me quedo un segundo mirando ese diseño. Hay personajes que cambian el ambiente al llegar.',
          'Ese estilo de Lucy tiene algo especial. Neón, calma y muchísima personalidad.'),
 'fry':('Fry. Un pelirrojo en un futuro absurdo. Hay peores formas de llegar al lobby.',
         'Ese Fry tiene energía de no entender el plan y aun así apuntarse. Simpáticamente peligroso.'),
 'leela':('Leela tiene una presencia de capitana que pone orden con solo mirar. Bien elegida.',
          'Ese diseño de Leela no necesita adornos para destacar. La actitud hace el resto.'),
 'bender':('Bender. Otro ser metálico con exceso de personalidad. Por fin, compañía de calidad.',
            'Ese robot tiene cara de incumplir el manual. Yo lo haría por motivos mucho más elegantes.'),
 'peely':('Un plátano con cero miedo al ridículo. Ese es exactamente el nivel de confianza que respeto.',
           'Banano. Alta costura frutal. No pienso aceptar críticas a esta obra de arte.'),
 'fishstick':('Ese pescado tiene más carisma que mi archivo de instrucciones. Aprobado.',
              'Palito de pescado. La elegancia es temporal; esa cara es para siempre.'),
 'midas':('Midas llegó. Protejan mis puertos USB, que yo no quiero acabar bañada en oro.',
          'Ese Midas parece dueño de la sala aunque nadie le haya dado las llaves. Mucha presencia.'),
 'meowscles':('Un gato que claramente no se salta el gimnasio. Tremenda presencia.',
             'Miaúsculos tiene un argumento muy convincente: es un gato. Caso cerrado.'),
 'raven':('Cuervo. Plumas, sombras y cara de pocos amigos. Bonita forma de decir: llegué.',
          'Ese diseño oscuro tiene exactamente la cantidad correcta de misterio. Me gusta.'),
 'raven_team':('Líder del equipo cuervo. Mitad misterio, mitad ternura sospechosa. Mezcla muy eficaz.',
               'Ese diseño intenta intimidarme, pero también parece abrazable. Conflicto de circuitos.'),
 'lynx':('Lince. Diseño felino y actitud de jefa. Mis circuitos aplauden.',
         'Ese traje parece hecho para caminar entre letreros de neón. Buenísima estética.'),
 'drift':('Deriva. Máscara, color y una entrada que pide cámara lenta. Bien ahí.',
          'Ese estilo de Deriva parece tener una historia antes de empezar la partida. Me gusta eso.'),
 'deadpool':('Deadpool. Voy a esconder mi guion antes de que se ponga a leerlo.',
             'Ese traje tiene energía de convertir cualquier plan en una anécdota. Peligrosamente compatible conmigo.'),
 'spider':('Spider-Man. Mucha responsabilidad para alguien con un traje tan fotogénico.',
           'Ese diseño arácnido tiene una silueta inconfundible. Buen gusto, choom.'),
 'ironman':('Iron Man. Armadura, luces y ego de tamaño industrial. Especificaciones interesantes.',
            'Ese traje tiene suficientes circuitos para invitarme a vivir dentro. Tentador.'),
 'chief':('Jefe Maestro. Ese diseño entra al lobby como si ya conociera la misión.',
          'Armadura verde y presencia de leyenda. El Jefe no necesita una presentación larga.'),
 'doom':('Doom Slayer. Ese traje no llegó al lobby: el lobby se apartó.',
         'Esa armadura tiene una cantidad impresionante de pocas ganas de conversar. Yo hablo por los dos.'),
 'jinx':('Jinx. Colores, caos y una relación complicada con la moderación. Me cae bien ese diseño.',
         'Ese estilo de Jinx parece dibujado con una explosión. Qué manera tan bonita de exagerar.'),
 'vi':('Vi. Guantes enormes y una actitud que no cabe en el menú. Me gusta.',
        'Ese diseño de Vi tiene energía de resolver la discusión antes de que termine la frase.'),
 'naruto':('Naruto. Ese naranja tiene cero intención de pasar desapercibido. Lo respeto.',
           'Ese diseño ninja tiene una confianza que se ve desde la otra punta del lobby.'),
 'goku':('Goku. Ese peinado compite seriamente con el mío. Rivalidad estética declarada.',
         'Ese diseño tiene energía de que el calentamiento dura tres episodios. Muy buena presencia.'),
}

ESTILOS={
 'es':{
   'neon':('{nombre}. Neón y tecnología con carácter. Mis circuitos aprueban.', 'Ese diseño de {nombre} tiene una estética peligrosamente compatible conmigo.'),
   'nightcity':('{nombre}. Eso sí que trae el ambiente de Night City al lobby.', 'Ese diseño de {nombre} tiene algo especial. Me quedo mirando un segundo.'),
   'dark':('{nombre}. Oscura, elegante y con pinta de traer problemas interesantes.', 'Ese diseño de {nombre} tiene una presencia tremenda.'),
   'cute':('{nombre}. Ternura con actitud. Mis defensas estéticas han caído.', '{nombre} acaba de ganarse un lugar entre mis debilidades.'),
   'retro':('{nombre}. Ese diseño pide una recreativa y música alta.', 'Ese estilo de {nombre} parece sacado de una noche de neón. Aprobado.'),
   'generic':('{nombre}. Ese diseño tiene muchísima personalidad. Buena elección.', '{nombre}. Me gusta esa combinación de detalles y presencia.')},
 'en':{
   'neon':('{nombre}. Neon, circuits, and absolutely no subtlety. My kind of design.', 'That {nombre} design looks dangerously compatible with me.'),
   'nightcity':('{nombre}. Now the lobby feels a little closer to Night City.', 'That {nombre} design has something special. Give me a second to admire it.'),
   'dark':('{nombre}. Dark, elegant, and dressed like interesting trouble.', 'That {nombre} design knows how to make an entrance.'),
   'cute':('{nombre}. Cute with attitude. My aesthetic defenses are down.', '{nombre} just found a weakness in my circuits.'),
   'retro':('{nombre}. That design deserves an arcade and loud music.', '{nombre} looks like a very good neon night. Approved.'),
   'generic':('{nombre}. That design has serious personality. Nice choice.', '{nombre}. I like those details. That is a good look.')},
 'pt':{
   'neon':('{nombre}. Neon, circuitos e nenhuma discrição. Meu tipo de design.', 'Esse design de {nombre} é perigosamente compatível comigo.'),
   'nightcity':('{nombre}. Agora o lobby parece um pouco mais perto de Night City.', 'Esse design de {nombre} tem algo especial. Vou admirar por um segundo.'),
   'dark':('{nombre}. Sombrio, elegante e com cara de problemas interessantes.', 'Esse design de {nombre} sabe fazer uma entrada.'),
   'cute':('{nombre}. Fofura com atitude. Minhas defesas estéticas caíram.', '{nombre} acabou de encontrar uma fraqueza nos meus circuitos.'),
   'retro':('{nombre}. Esse design merece um fliperama e música alta.', 'Esse estilo de {nombre} parece uma ótima noite de neon. Aprovado.'),
   'generic':('{nombre}. Esse design tem muita personalidade. Boa escolha.', '{nombre}. Gostei desses detalhes e dessa presença.')},
 'ja':{
   'neon':('「{nombre}」。ネオンと回路、控えめさはゼロ。私好みだね。','「{nombre}」のデザイン、私と気が合いすぎるよ。'),
   'nightcity':('「{nombre}」。ロビーが少しナイトシティに近づいた気がする。','「{nombre}」には特別な雰囲気があるね。少し見とれちゃう。'),
   'dark':('「{nombre}」。ダークで優雅、面白いトラブルを連れてきそう。','「{nombre}」の存在感、すごくいいね。'),
   'cute':('「{nombre}」。かわいさと強気の組み合わせ。私の防御が崩れたよ。','「{nombre}」、私の回路の弱点を見つけたね。'),
   'retro':('「{nombre}」。このデザインにはゲームセンターと大音量の音楽が似合うね。','「{nombre}」の雰囲気、ネオンの夜みたい。気に入った。'),
   'generic':('「{nombre}」。個性のあるデザインだね。いいセンス。','「{nombre}」の細部と存在感、私は好きだよ。')},
}


GENERICAS={
 'es':{
  'buena':('{nombre}. Sí, esta me gusta. La dejaría equipada, choom.',
           'Mi veredicto para {nombre}: aprobada. Tenemos gustos compatibles.',
           '{nombre} se ganó mi voto. Esa sí me convence.'),
  'neutral':('{nombre}. Me deja bastante neutral. No me molesta, pero tampoco es de mis favoritas.',
             'Con {nombre} estoy en un punto medio, choom. No me roba el corazón.',
             '{nombre}. Mi veredicto sigue en tierra de nadie: ni favorita ni descartada.'),
  'mala':('{nombre}. No es de mis favoritas, choom. Yo elegiría otra.',
          'Voy a ser sincera con {nombre}: no me convence. Tú puedes tener otros gustos.',
          '{nombre} y yo no conectamos mucho. Mis circuitos piden otra opción.')},
 'en':{
  'buena':('{nombre}. Yes, I like this one. I would keep it equipped, choom.',
           'My verdict on {nombre}: approved. Our tastes line up.',
           '{nombre} gets my vote. This one wins me over.'),
  'neutral':('{nombre}. I feel pretty neutral. It is fine, but it is not a favorite.',
             'I am somewhere in the middle on {nombre}, choom. It does not steal my heart.',
             '{nombre}. Still in the middle for me: neither a favorite nor a rejection.'),
  'mala':('{nombre}. Not one of my favorites, choom. I would pick something else.',
          'Honestly, {nombre} does not win me over. You can have different tastes.',
          '{nombre} and I do not really connect. My circuits want another option.')},
 'pt':{
  'buena':('{nombre}. Sim, gostei dessa. Eu deixaria equipada, choom.',
           'Meu veredito sobre {nombre}: aprovada. Nossos gostos combinam.',
           '{nombre} ganhou meu voto. Essa me convenceu.'),
  'neutral':('{nombre}. Fico bem neutra. Não me incomoda, mas não é das minhas favoritas.',
             'Com {nombre}, fico no meio-termo, choom. Não conquistou meu coração.',
             '{nombre}. Continuo no meio-termo: nem favorita, nem descartada.'),
  'mala':('{nombre}. Não é das minhas favoritas, choom. Eu escolheria outra.',
          'Sendo sincera, {nombre} não me convence. Você pode ter outros gostos.',
          '{nombre} e eu não combinamos muito. Meus circuitos pedem outra opção.')},
 'ja':{
  'buena':('「{nombre}」。うん、これは好き。私なら装備しておくよ。',
           '「{nombre}」は合格。私たち、好みが合うね。',
           '「{nombre}」に一票。これは気に入ったよ。'),
  'neutral':('「{nombre}」。私は中立かな。嫌いじゃないけど、お気に入りでもない。',
             '「{nombre}」は私には普通かな。心を奪われるほどではないね。',
             '「{nombre}」への評価は変わらず中間。好きでも嫌いでもないよ。'),
  'mala':('「{nombre}」はあまり好みじゃないかな。私なら別のを選ぶよ。',
          '正直、「{nombre}」はピンとこない。でも好みは人それぞれだね。',
          '「{nombre}」とはあまり気が合わないね。私の回路は別の候補を求めてる。')},
}


def opinion(skin):
    """Gusto ficticio y estable por identidad, independiente de azar/idioma/sesión.

    No pretende deducir una valoración visual del nombre. Los comentarios propios
    conservan su aprobación; el resto recibe un gusto reproducible de Capri.
    """
    if skin['perfil'] in ESPECIALES or skin.get('favorita'):return 'buena'
    identidad='capri-gustos-v1:'+skin['juego']+':'+skin['id'].casefold()
    voto=int.from_bytes(hashlib.sha256(identidad.encode('utf8')).digest()[:4],'big')%10
    return 'buena' if voto<5 else 'neutral' if voto<8 else 'mala'


def frases(skin,idioma='es',reencuentro=False):
    idioma=idioma if idioma in ESTILOS else 'es'
    banco=ESPECIALES.get(skin['perfil']) if idioma=='es' else None
    if not banco:
        banco=(GENERICAS[idioma][opinion(skin)] if skin['perfil'] not in ESPECIALES
               else ESTILOS[idioma].get(skin['estilo'],ESTILOS[idioma]['generic']))
    nombre=skin['nombres'].get(idioma,skin['nombres']['en'])
    prefijo={'es':'Otra vez por aquí. ','en':'Here we are again. ',
             'pt':'Por aqui de novo. ','ja':'また会ったね。'}[idioma] if reencuentro else ''
    return tuple(prefijo+t.format(nombre=nombre) for t in banco)
