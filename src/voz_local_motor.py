"""Motor opcional de Qwen3-TTS; se ejecuta con su propio Python, nunca en Tk."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def bucle_rapido(config, protocolo):
    import wave
    from voz_local import wav_valido,podar_cache
    from voz_rapida import MotorRapido,fragmentos
    motor=MotorRapido(config['rapida'])
    cache=config['cache'];cache.mkdir(parents=True,exist_ok=True)
    for linea in sys.stdin:
        ticket=None;trabajo=None
        try:
            peticion=json.loads(linea);ticket=peticion['id'];texto=peticion['texto']
            if not re.fullmatch('[a-f0-9]{32}',ticket) or not isinstance(texto,str) or not 0<len(texto)<=1800:
                raise ValueError('Petición inválida.')
            destino=Path(peticion['destino']).resolve()
            if destino.parent!=cache.resolve() or not re.fullmatch(r'[a-f0-9]{64}\.wav',destino.name):raise ValueError('Destino inválido.')
            if not wav_valido(destino):
                trabajo=cache/'trabajos'/ticket;trabajo.mkdir(parents=True,exist_ok=True)
                partes=[]
                for i,(a,b) in enumerate(fragmentos(texto)):
                    clip=trabajo/f'{i}.wav'
                    motor.generar(texto[a:b].strip(),clip)
                    if not wav_valido(clip):raise RuntimeError('Fragmento inválido.')
                    partes.append(clip)
                    if peticion.get('fragmentos'):
                        print(json.dumps({'id':ticket,'tipo':'fragmento','archivo':str(clip),'inicio':a,'fin':b}),file=protocolo,flush=True)
                temporal=trabajo/'completo.wav'
                with wave.open(str(temporal),'wb') as out:
                    out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000)
                    for clip in partes:
                        with wave.open(str(clip),'rb') as src:out.writeframes(src.readframes(src.getnframes()))
                temporal.replace(destino)
            podar_cache(cache,destino)
            print(json.dumps({'id':ticket,'ok':True,'archivo':str(destino)}),file=protocolo,flush=True)
        except Exception as error:
            import traceback
            traceback.print_exc(file=sys.stderr)
            print(json.dumps({'id':ticket,'ok':False,'error':type(error).__name__}),file=protocolo,flush=True)
        finally:
            if trabajo and not peticion.get('fragmentos') and trabajo.is_dir():
                for p in trabajo.iterdir():
                    if p.is_file():p.unlink(missing_ok=True)
                trabajo.rmdir()


def fragmentar(texto, maximo=220):
    trozos = []
    for frase in re.split(r'(?<=[.!?])\s+', texto.strip()):
        while len(frase) > maximo:
            corte = frase.rfind(' ', 0, maximo + 1)
            if corte <= 0:corte = maximo
            trozos.append(frase[:corte].strip());frase = frase[corte:].strip()
        if frase:trozos.append(frase)
    partes = []
    for trozo in trozos:
        if partes and len(partes[-1]) + 1 + len(trozo) <= maximo:partes[-1] += ' ' + trozo
        else:partes.append(trozo)
    return partes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--modo', choices=['local','rapida'],default='local')
    args = parser.parse_args()
    from voz_local import cargar_config, wav_valido
    config = cargar_config(args.config)
    protocolo = sys.stdout
    # Los avisos de las librerías se guardan en el diagnóstico, no en el protocolo.
    sys.stdout = sys.stderr
    if args.modo=='rapida':return bucle_rapido(config,protocolo)
    os.environ.update(HF_HUB_OFFLINE='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1', TOKENIZERS_PARALLELISM='false')
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem
    from safetensors import safe_open
    from safetensors.torch import load_file
    torch.set_num_threads(4)
    modelo = None;prompt = None
    def cargar():
        nonlocal modelo,prompt
        if modelo is not None:return
        modelo = Qwen3TTSModel.from_pretrained(str(config['modelo']), device_map='cpu', dtype=torch.float32,
                                             attn_implementation='eager', local_files_only=True)
        with safe_open(str(config['perfil']), framework='pt', device='cpu') as f:meta = f.metadata()
        tensores = load_file(str(config['perfil']), device='cpu')
        if not meta.get('ref_text') or 'ref_code' not in tensores:raise RuntimeError('Perfil de voz incompleto.')
        if not torch.isfinite(tensores['ref_spk_embedding']).all():raise RuntimeError('Perfil inválido.')
        prompt = [VoiceClonePromptItem(ref_code=tensores['ref_code'], ref_spk_embedding=tensores['ref_spk_embedding'],
                                      x_vector_only_mode=False, icl_mode=True, ref_text=meta['ref_text'])]
    cache = config['cache'];cache.mkdir(parents=True, exist_ok=True)
    for linea in sys.stdin:
        ticket = None
        try:
            peticion = json.loads(linea);ticket = peticion['id']
            texto = peticion['texto']
            if not isinstance(texto, str) or not 0 < len(texto) <= 1800:raise ValueError('Texto inválido.')
            archivo = Path(peticion['destino']).resolve()
            if archivo.parent != cache.resolve() or not re.fullmatch(r'[a-f0-9]{64}\.wav', archivo.name):
                raise ValueError('Destino inválido.')
            if not wav_valido(archivo):
                cargar();audios=[];sr=None
                torch.manual_seed(42)
                for parte in fragmentar(texto):
                    audio, sr = modelo.generate_voice_clone(
                        text=parte, language='English', voice_clone_prompt=prompt,
                        non_streaming_mode=True, max_new_tokens=640,
                        temperature=.75, top_p=.95, subtalker_temperature=.75, repetition_penalty=1.05)
                    a = np.asarray(audio[0], dtype=np.float32)
                    if not a.size or not np.isfinite(a).all() or len(a) / sr >= 50:
                        raise RuntimeError('La generación no terminó correctamente.')
                    if audios:audios.append(np.zeros(round(sr * .12), dtype=np.float32))
                    audios.append(a)
                fd, nombre = tempfile.mkstemp(prefix='.generando-', suffix='.wav', dir=cache);os.close(fd)
                temporal = Path(nombre)
                try:
                    sf.write(temporal, np.concatenate(audios), sr, subtype='PCM_16')
                    if not wav_valido(temporal):raise RuntimeError('Audio inválido.')
                    temporal.replace(archivo)
                finally:temporal.unlink(missing_ok=True)
                antiguos = sorted((p for p in cache.glob('*.wav') if re.fullmatch('[a-f0-9]{64}\.wav', p.name)),
                                   key=lambda p:p.stat().st_mtime, reverse=True)
                total = 0
                for i, previo in enumerate(antiguos):
                    total += previo.stat().st_size
                    if previo != archivo and (i >= 256 or total > 128 * 1024 * 1024):
                        previo.unlink(missing_ok=True)
            print(json.dumps({'id':ticket, 'ok':True, 'archivo':str(archivo)}), file=protocolo, flush=True)
        except Exception as error:
            import traceback
            traceback.print_exc(file=sys.stderr)
            print(json.dumps({'id':ticket, 'ok':False, 'error':type(error).__name__}), file=protocolo, flush=True)


if __name__ == '__main__':main()
