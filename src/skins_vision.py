"""Ficha visible de Valorant mediante OCR local; sin entradas al juego."""
from pathlib import Path
import tempfile
from fortnite import ErrorFortnite,Pantalla
from fortnite_vision import VistaFortnite,leer_imagen


class VistaValorantSkins(VistaFortnite):
    # La selección de ventana heredada verifica la ruta del proceso real.
    NOMBRES={'valorant-win64-shipping.exe'}

    def capturar(self,activar=False):
        try:
            h=self._ventana();recuperada=self._activar(h) if activar else False
            imagen,rect,inicio=self._imagen(h,esperar=recuperada)
            with tempfile.TemporaryDirectory(prefix='capri-valorant-skin-') as temporal:
                ruta=Path(temporal)/'ficha.png';imagen.save(ruta);textos=leer_imagen(ruta)
            self._validar(h,rect)
            return Pantalla(h,rect,textos,inicio)
        except ErrorFortnite as e:
            raise ErrorFortnite(str(e).replace('Fortnite','Valorant').replace('lobby','colección')) from e
