"""Voz inglesa rápida: síntesis de texto y conversión al timbre de referencia."""
import asyncio
from pathlib import Path
import sys


def fragmentos(texto, primero=100, maximo=210):
    """Rangos contiguos; el primer audio puede salir antes del resto."""
    import re
    inicio=0
    while inicio<len(texto):
        limite=primero if inicio==0 else maximo
        fin=min(len(texto),inicio+limite)
        if fin<len(texto):
            puntos=list(re.finditer(r'[.!?](?:\s|$)',texto[inicio:fin]))
            if puntos:fin=inicio+puntos[-1].end()
            else:
                espacio=texto.rfind(' ',inicio,fin)
                if espacio>inicio:fin=espacio+1
        yield inicio,fin
        inicio=fin


class MotorRapido:
    def __init__(self, config):
        sys.path.insert(0,str(config['codigo']))
        import torch
        from openvoice.models import SynthesizerTrn
        from openvoice import utils
        from safetensors.torch import load_file
        self.torch=torch;self.config=config
        torch.set_num_threads(4)
        self.hps=utils.get_hparams_from_file(str(config['config']))
        self.device='cpu'
        try:
            if torch.cuda.is_available() and torch.cuda.mem_get_info()[0]>512*1024*1024:self.device='cuda:0'
        except RuntimeError:pass
        h=self.hps
        self.model=SynthesizerTrn(len(getattr(h,'symbols',[])),h.data.filter_length//2+1,
                                 n_speakers=h.data.n_speakers,**h.model).eval()
        estado=torch.load(config['pesos'],map_location='cpu',weights_only=True)
        faltan,sobran=self.model.load_state_dict(estado['model'],strict=False)
        if faltan or sobran:raise RuntimeError('Modelo de conversión incompleto.')
        perfiles=load_file(str(config['perfil']),device='cpu')
        if set(perfiles)!={'source','target'} or not all(torch.isfinite(t).all() for t in perfiles.values()):
            raise RuntimeError('Perfil de conversión inválido.')
        self.source=perfiles['source'];self.target=perfiles['target']
        try:self._mover(self.device)
        except RuntimeError:self._mover('cpu')
        # Preparar kernels antes de la primera petición; nunca se reproduce esto.
        import numpy as np
        self.convertir(np.zeros(h.data.sampling_rate,dtype=np.float32))
        print('Motor de voz rápida preparado en',self.device,file=sys.stderr,flush=True)

    def _mover(self,device):
        self.device=device;self.model=self.model.to(device)
        self.source=self.source.to(device);self.target=self.target.to(device)

    def convertir(self,audio):
        from openvoice.mel_processing import spectrogram_torch
        import librosa
        torch=self.torch;h=self.hps
        def ejecutar():
            y=torch.as_tensor(audio,dtype=torch.float32,device=self.device).unsqueeze(0)
            spec=spectrogram_torch(y,h.data.filter_length,h.data.sampling_rate,h.data.hop_length,h.data.win_length,center=False)
            with torch.inference_mode():
                resultado=self.model.voice_conversion(spec,torch.tensor([spec.size(-1)],device=self.device),
                                sid_src=self.source,sid_tgt=self.target,tau=.3)[0][0,0].float().cpu().numpy()
            return librosa.resample(resultado,orig_sr=h.data.sampling_rate,target_sr=24000)
        try:return ejecutar()
        except torch.cuda.OutOfMemoryError:
            if self.device=='cpu':raise
            self._mover('cpu');torch.cuda.empty_cache()
            return ejecutar()

    def generar(self,texto,destino):
        import edge_tts
        import librosa
        import numpy as np
        import soundfile as sf
        mp3=Path(destino).with_suffix('.mp3')
        async def preparar():
            comunicacion=edge_tts.Communicate(texto,self.config.get('voz_base','en-US-AriaNeural'),
                                            pitch=self.config.get('tono_base','+8Hz'))
            await asyncio.wait_for(comunicacion.save(str(mp3)),timeout=25)
        try:
            asyncio.run(preparar())
            audio,_=librosa.load(str(mp3),sr=self.hps.data.sampling_rate)
            salida=self.convertir(audio)
            if not salida.size or not np.isfinite(salida).all():raise RuntimeError('Audio de conversión inválido.')
            sf.write(destino,salida,24000,subtype='PCM_16')
        finally:mp3.unlink(missing_ok=True)
