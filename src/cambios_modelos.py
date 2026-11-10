"""Comparaciones para confirmar cambios antes de alterar las preferencias."""
import re
from idiomas import ui

GIB=1024**3


def gb(valor):return f'{valor/GIB:.1f} GB'


def _informe(ganas,coste,detalle='',nota=''):
    return dict(estado='desconocido',titulo=ui('Faltan datos para recomendarlo'),
                recomendacion=ui('Puedes decidir por sus ventajas y límites; Capri no inventará la capacidad que no pudo leer.'),
                ganas=ui(ganas),coste=ui(coste),detalle=detalle,nota=nota)


def _resumir(informe,resumen,equipo):
    """La interfaz muestra solo el intercambio y un consejo corto para este PC."""
    estado=informe['estado'];titulo=informe['titulo']
    if estado=='recomendado':consejo='Tu PC tiene recursos suficientes. Puedes cambiar.'
    elif estado=='limitado':consejo='No lo recomiendo en tu PC: puede ralentizarlo.'
    elif estado=='desconocido':consejo='No pude comprobar si conviene en tu PC.'
    elif titulo==ui('Comprueba el uso de tu GPU'):consejo='Podría funcionar con tu gráfica, pero no pude confirmarlo.'
    elif titulo==ui('La opción más ligera para tu equipo'):consejo='Es la opción más ligera para tu PC.'
    elif titulo==ui('La memoria alcanza; vigila la espera'):
        consejo='Puedes usarlo, pero tu procesador puede tardar más.' if equipo.get('hilos') else 'No pude comprobar la velocidad en tu PC.'
    elif titulo==ui('Poco margen libre ahora'):consejo='Ahora falta memoria libre. Cierra otras aplicaciones.'
    else:consejo='Puedes cambiar, pero podría restar fluidez a tus juegos.'
    informe.update(resumen=ui(resumen),consejo_breve=ui(consejo))
    return informe


def _memoria(informe,equipo,minimo,holgado):
    """Presupuesto conservador de CPU/RAM, no un requisito del fabricante."""
    total=equipo.get('ram_total');libre=equipo.get('ram_libre')
    if not total or libre is None:return informe
    reserva=max(2*GIB,total*.15)
    if total<minimo+reserva:
        informe.update(estado='limitado',titulo=ui('Mejor una opción más ligera'),
            recomendacion=ui('La RAM total deja poco margen para este cambio y tus otras aplicaciones. Recomiendo una opción más ligera, especialmente mientras juegas.'))
    elif libre<minimo:
        informe.update(estado='precaucion',titulo=ui('Poco margen libre ahora'),
            recomendacion=ui('Tu equipo tiene capacidad, pero ahora hay poca RAM disponible. Cierra aplicaciones o conserva la opción actual si estás jugando; volver a evaluar puede cambiar este consejo.'))
    elif libre<holgado+reserva:
        informe.update(estado='precaucion',titulo=ui('Viable, con margen ajustado'),
            recomendacion=ui('Puedes probarlo, aunque otras aplicaciones pueden competir por la memoria. Para priorizar fluidez mientras juegas, conserva una opción ligera.'))
    else:
        informe.update(estado='recomendado',titulo=ui('Buen margen para este cambio'),
            recomendacion=ui('La RAM disponible deja margen para esta opción y otras aplicaciones. Recomiendo probarla si su ventaja coincide con lo que buscas.'))
    return informe


def informe_modelo(actual,nuevo,modelos,equipo):
    anterior=modelos.get(actual,{}) or {};destino=modelos.get(nuevo,{}) or {}
    a=parametros(anterior);b=parametros(destino)
    if a and b and b>a*1.15:
        resumen='Puede dar respuestas más completas, con más espera y consumo.'
        gana='Más parámetros pueden ayudar con preguntas complejas y respuestas detalladas. El entrenamiento y la familia también importan; no garantizan mayor calidad.'
        coste='Puede necesitar más memoria y tardar más en generar cada respuesta. Conviene si prefieres profundidad antes que rapidez.'
    elif a and b and b<a*.85:
        resumen='Puede responder más rápido y consumir menos, pero con menos detalle.'
        gana='Un modelo más pequeño puede responder antes y dejar más recursos para tus juegos. Es una buena dirección si priorizas agilidad.'
        coste='Puede perder detalle o capacidad en preguntas difíciles. Compara sus respuestas antes de elegirlo como modelo habitual de la conversación.'
    else:
        resumen='Cambiará su forma de responder; no hay una mejora clara de calidad o rapidez.'
        gana='Otra familia puede seguir mejor tus instrucciones o encajar mejor con tu forma de conversar. Prueba respuestas conocidas para compararlas.'
        coste='Cambiar de familia no garantiza más calidad ni rapidez. La primera respuesta puede tardar mientras se carga el modelo.'
    nota=ui('La recomendación es orientativa: contexto, cuantización y aplicaciones abiertas cambian el consumo. La GPU detectada no confirma que Ollama la use; su VRAM no se suma a la RAM.')
    informe=_informe(gana,coste,nota=nota)
    peso=destino.get('size')
    if isinstance(peso,(int,float)) and not isinstance(peso,bool) and peso>0:
        minimo=peso+max(GIB,peso*.25);holgado=peso+max(2*GIB,peso*.75)
        informe['detalle']=ui('Archivo del modelo: {0}. Margen de RAM orientativo para ejecución en CPU: {1}–{2}.').format(gb(peso),gb(minimo),gb(holgado))
        anterior_peso=anterior.get('size')
        if isinstance(anterior_peso,(int,float)) and not isinstance(anterior_peso,bool) and anterior_peso>0:
            informe['detalle']=ui('Archivo actual: {0}.').format(gb(anterior_peso))+' '+informe['detalle']
        informe['nota']+=' '+ui('La RAM libre es una instantánea: al sustituir el modelo, el anterior puede liberar memoria.')
        _memoria(informe,equipo,minimo,holgado)
        dedicada=max((g.get('dedicada',0) for g in equipo.get('gpus',[])),default=0)
        if informe['estado']=='limitado' and dedicada>=holgado:
            informe.update(estado='precaucion',titulo=ui('Comprueba el uso de tu GPU'),
                recomendacion=ui('La RAM es ajustada, pero una gráfica tiene {0} de memoria dedicada. Si Ollama puede usarla, podría descargar parte del trabajo. No confirmé compatibilidad ni VRAM libre: es una posibilidad que debes verificar, no una garantía.').format(gb(dedicada)))
    else:
        informe['detalle']=ui('No hay tamaño local fiable para este modelo. El nombre o la cantidad de parámetros no bastan para calcular su memoria.')
    if equipo.get('hilos') and equipo['hilos']<=4:
        if informe['estado']=='recomendado':informe.update(estado='precaucion',titulo=ui('La memoria alcanza; vigila la espera'))
        informe['coste']+=' '+ui('Tu CPU tiene hasta 4 hilos lógicos. Si la IA trabaja en CPU, un modelo grande puede añadir espera; no es una medida de su velocidad real.')
    return _resumir(informe,resumen,equipo)


def informe_reconocimiento(actual_motor,actual_modelo,nuevo_motor,nuevo_modelo,equipo):
    if nuevo_motor=='rapido':
        resumen='Te entiende más rápido y usa menos recursos, pero puede cometer más errores.'
        gana='Vosk prioriza respuestas rápidas y deja más recursos para jugar. Es la opción más ligera para órdenes frecuentes en español.'
        coste='Puede fallar más con nombres en inglés, frases largas o ruido. El menor consumo no significa que entienda mejor.'
        minimo,holgado=.35*GIB,.7*GIB
    elif nuevo_modelo=='small':
        resumen='Suele entenderte mejor, pero tarda más y usa más recursos.'
        gana='Whisper Small puede entender mejor nombres difíciles, acentos y frases complejas. Conviene si la precisión te importa más que una respuesta inmediata.'
        coste='Usa más RAM y trabajo de CPU que Base. Puedes notar más espera al terminar de hablar, sobre todo mientras juegas.'
        minimo,holgado=1.5*GIB,3*GIB
    else:
        resumen=('Te entiende más rápido y usa menos recursos, con algo menos de precisión.'
                 if actual_motor!='rapido' else 'Suele entenderte mejor que Vosk, pero tarda más y consume más.')
        gana='Whisper Base equilibra precisión y rapidez. Frente a Small deja más recursos libres; frente a Vosk puede entender mejor frases y nombres difíciles.'
        coste='Puede perder precisión frente a Small en audio difícil y tardar más que Vosk. El resultado depende de tu micrófono y del ruido.'
        minimo,holgado=.8*GIB,1.5*GIB
    informe=_informe(gana,coste,
        ui('Este reconocimiento usa tu procesador. La GPU no lo acelera en la configuración actual de Capri.'),
        ui('El criterio considera RAM disponible y hilos lógicos; no sustituye una prueba con tu voz. Cambia cómo Capri te entiende, no la voz con la que responde.'))
    _memoria(informe,equipo,minimo,holgado)
    hilos=equipo.get('hilos')
    if nuevo_motor=='rapido' and informe['estado']=='limitado':
        informe.update(estado='precaucion',titulo=ui('La opción más ligera para tu equipo'),
            recomendacion=ui('Vosk es la opción más ligera disponible. Frente a Whisper deja más margen, aunque la poca RAM de tu equipo puede seguir limitando otras aplicaciones.'))
    if nuevo_motor!='rapido' and hilos is None:
        if informe['estado']=='recomendado':informe.update(estado='precaucion',titulo=ui('La memoria alcanza; vigila la espera'))
        informe['recomendacion']+=' '+ui('No pude leer la capacidad de tu CPU. La memoria por sí sola no permite recomendar la velocidad de este reconocimiento.')
    elif nuevo_motor!='rapido' and hilos<=4:
        if informe['estado']=='recomendado':
            informe.update(estado='precaucion',titulo=ui('La memoria alcanza; vigila la espera'))
        informe['recomendacion']+=' '+ui('Con pocos hilos de CPU, recomiendo Base para equilibrar precisión y rapidez, o Vosk para priorizar agilidad. Small es una prueba de precisión, no una mejora de velocidad.')
    return _resumir(informe,resumen,equipo)


def informe_activacion(equipo):
    informe=_informe(
        'La IA local permite conversar libremente y hacer preguntas usando tu computador. Después de preparar el modelo, la conversación puede funcionar sin internet.',
        'La preparación puede descargar Ollama y un modelo de unos 2 GB. Al conversar compartirá recursos con tus juegos y otras aplicaciones.',
        ui('Empieza con el modelo ligero incluido. Después podrás comparar otros modelos con su tamaño local conocido.'),
        ui('La evaluación inicial es general: todavía no conocemos el consumo del modelo instalado. No es una garantía de rapidez.'))
    return _resumir(_memoria(informe,equipo,3*GIB,5*GIB),
        'Podrás conversar libremente con Capri, pero usará recursos de tu PC.',equipo)

TEXTOS=(
 'El modelo elegido tiene más parámetros. Puede necesitar más memoria y tardar más al responder.',
 'El modelo elegido tiene menos parámetros. Puede consumir menos y responder antes, pero perder detalle en algunas respuestas.',
 'El consumo y la rapidez dependen del tamaño del modelo y de tu equipo. Cambiar de familia no garantiza una mejora.',
 'La calidad de las respuestas puede variar. La primera respuesta puede tardar más mientras se carga el modelo.',
 'Whisper Small suele reconocer mejor frases y nombres difíciles, pero necesita más memoria y tiempo que Base.',
 'Whisper Base consume menos memoria y suele responder antes que Small, pero puede perder precisión con frases o nombres difíciles.',
 'Vosk usa menos recursos y responde rápido. Puede reconocer peor los nombres en inglés y las frases difíciles.',
 'Whisper suele reconocer mejor frases y nombres en inglés que Vosk, pero utiliza más recursos y puede tardar más.',
 'Este cambio afecta a cómo se entiende tu voz; no cambia la voz con la que responde Capri.',
)


def parametros(modelo):
    detalle=modelo.get('details',{}) if isinstance(modelo,dict) else {}
    if not isinstance(detalle,dict):return None
    m=re.fullmatch(r'\s*(\d+(?:[.,]\d+)?)\s*([BM])\s*',str(detalle.get('parameter_size','')),re.I)
    if m:return float(m[1].replace(',','.'))*(1e9 if m[2].upper()=='B' else 1e6)


def comparar_modelos(actual,nuevo,modelos):
    a=parametros(modelos.get(actual,{}));b=parametros(modelos.get(nuevo,{}))
    if a and b and b>a*1.15:texto=TEXTOS[0]
    elif a and b and b<a*.85:texto=TEXTOS[1]
    else:texto=TEXTOS[2]
    return ui(texto)+'\n\n'+ui(TEXTOS[3])


def comparar_reconocimiento(actual_motor,actual_modelo,nuevo_motor,nuevo_modelo):
    if nuevo_motor=='rapido':texto=TEXTOS[6]
    elif actual_motor=='rapido':
        texto=TEXTOS[7]
        if nuevo_modelo=='small':return ui(texto)+'\n\n'+ui(TEXTOS[4])
    elif nuevo_modelo=='small':texto=TEXTOS[4]
    else:texto=TEXTOS[5]
    return ui(texto)+'\n\n'+ui(TEXTOS[8])
