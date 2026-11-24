import json
from pathlib import Path
from typing import Any, Dict


class RepositorioSIGER:
    """Capa de persistencia: lee y guarda los datos del sistema SIGER en JSON."""

    CLAVES_COLECCIONES = (
        "categorias",
        "reporteros",
        "solicitudes",
    )

    def __init__(self, ruta_archivo: str = "datos_siger.json"):
        self.archivo = Path(ruta_archivo)

    def _estructura_vacia(self) -> Dict[str, list]:
        return {clave: [] for clave in self.CLAVES_COLECCIONES}

    def cargar(self) -> Dict[str, Any]:
        if not self.archivo.exists():
            return self._estructura_vacia()

        try:
            with self.archivo.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            if not isinstance(datos, dict):
                raise RuntimeError("El formato del fichero JSON no es válido.")

            resultado = self._estructura_vacia()
            for clave in self.CLAVES_COLECCIONES:
                if clave in datos and isinstance(datos[clave], list):
                    resultado[clave] = datos[clave]
            return resultado
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Error al cargar el fichero '{self.archivo}': {exc}") from exc

    def guardar(self, datos: Dict[str, Any]) -> None:
        try:
            with self.archivo.open("w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            raise RuntimeError(f"Error al guardar en el fichero '{self.archivo}': {exc}") from exc