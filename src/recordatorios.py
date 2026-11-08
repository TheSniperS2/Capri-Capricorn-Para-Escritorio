"""Recordatorios personales de Capri, independientes de cualquier juego."""
import json,math,re,time,uuid,unicodedata

class ErrorRecordatorio(ValueError):pass

def normalizar(lista):
    salida=[];vistos=set()
    for r in (lista if isinstance(lista,list) else [])[:200]:
        if not isinstance(r,dict):continue
        i=r.get('id');fecha=r.get('vence');t=r.get('texto')
        if not isinstance(i,str) or not re.fullmatch('[a-f0-9]{20,32}',i) or i in vistos:continue
        if type(fecha) not in (int,float) or not math.isfinite(fecha) or not 0<fecha<4102444800:continue
        if not isinstance(t,str) or not t.strip():continue
        vistos.add(i);salida.append({'id':i,'vence':fecha,'texto':' '.join(t.split())[:300]})
    return salida

def agregar(lista,texto,minutos,ahora=None):
    lista=normalizar(lista)
    if len(lista)>=100:raise ErrorRecordatorio('Puedes guardar hasta 100 recordatorios.')
    if type(minutos) not in (int,float) or not math.isfinite(minutos) or not 1/60<=minutos<=10080:raise ErrorRecordatorio('Elige un plazo entre un segundo y siete días.')
    if not isinstance(texto,str) or not texto.strip():raise ErrorRecordatorio('Escribe qué quieres recordar.')
    return normalizar(lista+[{'id':uuid.uuid4().hex,'texto':texto,'vence':(time.time() if ahora is None else ahora)+minutos*60}])

def migrar(config):
    """Traslado idempotente de los avisos antiguos, preservando hora y texto."""
    rb=config.get('roblox');antiguos=rb.get('recordatorios',[]) if isinstance(rb,dict) else []
    actuales=normalizar(config.get('recordatorios',[]))
    config['recordatorios']=normalizar(actuales+antiguos)
    if antiguos:config['roblox']={**rb,'recordatorios':[]}
    return bool(antiguos)

def interpretar(texto):
    t=re.sub(r'^(?:(?:oye\s+)?capri|カプリ)[,、 :]*','',str(texto).strip(),flags=re.I).strip(' .!?¿¡')
    n=''.join(c for c in unicodedata.normalize('NFD',t.casefold()) if unicodedata.category(c)!='Mn')
    if t.startswith(('"',"'",'«','“')) or re.match(r'^(?:no|nao|not|never|don.t|nunca|si digo|dije|explica|como)\b',n):return None
    if n in ('abre mis recordatorios','abre los recordatorios','mis recordatorios','muestra mis recordatorios','open my reminders','show my reminders','abra meus lembretes','リマインダーを開いて'):return ('recordatorios_panel','')
    if n in ('cancela mis recordatorios','borra mis recordatorios','cancela todos los recordatorios','cancel my reminders','cancel all my reminders','cancele meus lembretes','リマインダーを全部取り消して'):return ('recordatorios_cancelar','')
    m=re.fullmatch(r'(?:recu[eé]rdame|av[ií]same) (?:en|dentro de) (\d{1,5}) (segundos?|minutos?|horas?) (.+)',t,re.I)
    if not m:m=re.fullmatch(r'(?:pon|crea) (?:un )?recordatorio (?:en|para dentro de) (\d{1,5}) (segundos?|minutos?|horas?) (?:para )?(.+)',t,re.I)
    if not m:m=re.fullmatch(r'remind me in (\d{1,5}) (seconds?|minutes?|hours?) (?:to )?(.+)',t,re.I)
    if not m:m=re.fullmatch(r'(?:lembre-me|me lembre|avise-me) (?:em|daqui a) (\d{1,5}) (segundos?|minutos?|horas?) (?:de )?(.+)',t,re.I)
    ja=re.fullmatch(r'(\d{1,5})(秒|分|時間)後に(.+)',t)
    if ja:
        mensaje=re.sub(r'(?:を教えて|を知らせて|を思い出させて)$','',ja[3])
        factor={'秒':1/60,'分':1,'時間':60}[ja[2]]
        return ('recordatorios_crear',json.dumps({'minutos':int(ja[1])*factor,'texto':mensaje},ensure_ascii=False))
    if m:
        factor=1/60 if m[2].lower().startswith(('segundo','second')) else 60 if m[2].lower().startswith(('hora','hour')) else 1
        return ('recordatorios_crear',json.dumps({'minutos':int(m[1])*factor,'texto':m[3]},ensure_ascii=False))
    return None
