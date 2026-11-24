from datetime import datetime
from typing import List, Optional

from backend import RepositorioSIGER

FORMATO_FECHA = "%d/%m/%Y"


# ==========================================
# ENTIDADES DEL MODELO DE DOMINIO
# ==========================================

class Categoria:
    """Representa uno de los 4 niveles de calidad de reporteros y su precio por hoja."""

    def __init__(self, nivel: int, nombre: str, precio_por_hoja: float):
        if nivel not in (1, 2, 3, 4):
            raise ValueError("El nivel de categoría debe estar comprendido entre 1 y 4.")
        if precio_por_hoja <= 0:
            raise ValueError("El precio por hoja escrita debe ser mayor que 0.")

        self.__nivel = nivel
        self.nombre = nombre
        self.precio_por_hoja = round(precio_por_hoja, 2)

    @property
    def nivel(self) -> int:
        return self.__nivel

    def to_dict(self) -> dict:
        return {
            "nivel": self.nivel,
            "nombre": self.nombre,
            "precio_por_hoja": self.precio_por_hoja,
        }

    def __str__(self) -> str:
        return f"Nivel {self.nivel} - {self.nombre} ({self.precio_por_hoja:.2f} €/hoja)"


class Reportero:
    """Representa a un reportero (datos personales fijos; en bolsa si tiene categoría asignada)."""

    def __init__(
        self,
        dni: str,
        nombre: str,
        apellidos: str,
        direccion: str,
        ciudad: str,
        codigo_postal: str,
        telefono: str,
        categoria_nivel: Optional[int] = None,
    ):
        self.__dni = dni.strip().upper()
        self.nombre = nombre.strip()
        self.apellidos = apellidos.strip()
        self.direccion = direccion.strip()
        self.ciudad = ciudad.strip()
        self.codigo_postal = codigo_postal.strip()
        self.telefono = telefono.strip()
        # None = aún no aprobado en bolsa; 1..4 = categoría asignada en bolsa
        self.__categoria_nivel: Optional[int] = categoria_nivel

    @property
    def dni(self) -> str:
        return self.__dni

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellidos}"

    @property
    def categoria_nivel(self) -> Optional[int]:
        return self.__categoria_nivel

    @property
    def en_bolsa(self) -> bool:
        return self.__categoria_nivel is not None

    def aprobar_en_categoria(self, nuevo_nivel: int) -> None:
        if nuevo_nivel not in (1, 2, 3, 4):
            raise ValueError("La categoría debe ser un nivel del 1 al 4.")
        self.__categoria_nivel = nuevo_nivel

    def promocionar_a_categoria(self, nuevo_nivel: int) -> None:
        if self.__categoria_nivel is None:
            raise ValueError("El reportero no está en la bolsa; primero debe ser aprobado.")
        if nuevo_nivel not in (1, 2, 3, 4):
            raise ValueError("La categoría destino debe ser un nivel del 1 al 4.")
        if nuevo_nivel <= self.__categoria_nivel:
            raise ValueError(
                f"Solo se puede ascender a categorías superiores "
                f"(actual: Nivel {self.__categoria_nivel}, destino: Nivel {nuevo_nivel})."
            )
        self.__categoria_nivel = nuevo_nivel

    def to_dict(self) -> dict:
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "codigo_postal": self.codigo_postal,
            "telefono": self.telefono,
            "categoria_nivel": self.categoria_nivel,
        }

    def __str__(self) -> str:
        estado = f"En bolsa (Nivel {self.categoria_nivel})" if self.en_bolsa else "Pendiente / No en bolsa"
        return f"[{self.dni}] {self.nombre_completo} — {estado}"


class Solicitud:
    """Representa una solicitud presentada por un reportero en una fecha concreta."""

    _contador = 1
    ESTADOS_VALIDOS = ("Pendiente", "Aprobada")

    def __init__(
        self,
        reportero_dni: str,
        fecha: datetime,
        resumen_cv: str,
        equipo_fotografico: Optional[str] = None,
        estado: str = "Pendiente",
        categoria_asignada: Optional[int] = None,
        identificador: Optional[int] = None,
    ):
        if identificador is None:
            self.__identificador = Solicitud._contador
            Solicitud._contador += 1
        else:
            self.__identificador = identificador
            Solicitud._contador = max(Solicitud._contador, identificador + 1)

        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado de solicitud no válido: {estado}")

        self.__reportero_dni = reportero_dni.strip().upper()
        self.__fecha = fecha
        self.equipo_fotografico = equipo_fotografico.strip() if equipo_fotografico and equipo_fotografico.strip() else None
        self.resumen_cv = resumen_cv.strip()
        self.__estado = estado
        self.__categoria_asignada = categoria_asignada

    @property
    def identificador(self) -> int:
        return self.__identificador

    @property
    def reportero_dni(self) -> str:
        return self.__reportero_dni

    @property
    def fecha(self) -> datetime:
        return self.__fecha

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def categoria_asignada(self) -> Optional[int]:
        return self.__categoria_asignada

    def marcar_aprobada(self, nivel_categoria: int) -> None:
        if nivel_categoria not in (1, 2, 3, 4):
            raise ValueError("La categoría asignada debe ser de nivel 1 a 4.")
        self.__estado = "Aprobada"
        self.__categoria_asignada = nivel_categoria

    def to_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "reportero_dni": self.reportero_dni,
            "fecha": self.fecha.strftime(FORMATO_FECHA),
            "equipo_fotografico": self.equipo_fotografico,
            "resumen_cv": self.resumen_cv,
            "estado": self.estado,
            "categoria_asignada": self.categoria_asignada,
        }


# ==========================================
# SERVICIO DE LÓGICA DE NEGOCIO SIGER
# ==========================================

class ServicioSIGER:
    """Capa de negocio de SIGER para Journ SL."""

    CATEGORIAS_POR_DEFECTO = (
        (1, "Categoría 1 (Básica)", 15.00),
        (2, "Categoría 2 (Estándar)", 22.00),
        (3, "Categoría 3 (Avanzada)", 30.00),
        (4, "Categoría 4 (Especialista)", 40.00),
    )

    def __init__(self, repositorio: RepositorioSIGER):
        self._repo = repositorio
        self.categorias: List[Categoria] = []
        self.reporteros: List[Reportero] = []
        self.solicitudes: List[Solicitud] = []
        self._cargar_estado()

    def _cargar_estado(self) -> None:
        datos = self._repo.cargar()

        if datos["categorias"]:
            for item in datos["categorias"]:
                self.categorias.append(
                    Categoria(
                        nivel=item["nivel"],
                        nombre=item["nombre"],
                        precio_por_hoja=item["precio_por_hoja"],
                    )
                )
        else:
            for nivel, nombre, precio in self.CATEGORIAS_POR_DEFECTO:
                self.categorias.append(Categoria(nivel, nombre, precio))

        self.categorias.sort(key=lambda c: c.nivel)

        for item in datos["reporteros"]:
            self.reporteros.append(
                Reportero(
                    dni=item["dni"],
                    nombre=item["nombre"],
                    apellidos=item["apellidos"],
                    direccion=item["direccion"],
                    ciudad=item["ciudad"],
                    codigo_postal=item["codigo_postal"],
                    telefono=item["telefono"],
                    categoria_nivel=item.get("categoria_nivel"),
                )
            )

        for item in datos["solicitudes"]:
            self.solicitudes.append(
                Solicitud(
                    reportero_dni=item["reportero_dni"],
                    fecha=datetime.strptime(item["fecha"], FORMATO_FECHA),
                    resumen_cv=item["resumen_cv"],
                    equipo_fotografico=item.get("equipo_fotografico"),
                    estado=item.get("estado", "Pendiente"),
                    categoria_asignada=item.get("categoria_asignada"),
                    identificador=item["identificador"],
                )
            )

        if not datos["categorias"]:
            self._guardar_estado()

    def _guardar_estado(self) -> None:
        self._repo.guardar({
            "categorias": [c.to_dict() for c in self.categorias],
            "reporteros": [r.to_dict() for r in self.reporteros],
            "solicitudes": [s.to_dict() for s in self.solicitudes],
        })

    @staticmethod
    def _obligatorio(valor: str, campo: str) -> str:
        if not valor or not valor.strip():
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        return valor.strip()

    # --- Consultas ---
    def obtener_categoria(self, nivel: int) -> Optional[Categoria]:
        return next((c for c in self.categorias if c.nivel == nivel), None)

    def obtener_reportero(self, dni: str) -> Optional[Reportero]:
        dni_limpio = dni.strip().upper()
        return next((r for r in self.reporteros if r.dni == dni_limpio), None)

    def obtener_solicitud(self, identificador: int) -> Optional[Solicitud]:
        return next((s for s in self.solicitudes if s.identificador == identificador), None)

    def listar_solicitudes_aprobadas(self) -> List[Solicitud]:
        return [s for s in self.solicitudes if s.estado == "Aprobada"]

    def listar_reporteros_en_bolsa(self) -> List[Reportero]:
        return [r for r in self.reporteros if r.en_bolsa]

    def solicitudes_de_reportero(self, dni: str) -> List[Solicitud]:
        dni_limpio = dni.strip().upper()
        return [s for s in self.solicitudes if s.reportero_dni == dni_limpio]

    # --- 1.1 Dar de alta una nueva solicitud ---
    def registrar_solicitud(
        self,
        dni: str,
        fecha: datetime,
        resumen_cv: str,
        equipo_fotografico: Optional[str] = None,
        nombre: Optional[str] = None,
        apellidos: Optional[str] = None,
        direccion: Optional[str] = None,
        ciudad: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        telefono: Optional[str] = None,
    ) -> Solicitud:
        dni_limpio = self._obligatorio(dni, "DNI").upper()
        cv_limpio = self._obligatorio(resumen_cv, "resumen del CV")

        reportero = self.obtener_reportero(dni_limpio)

        if reportero is None:
            # Primera solicitud del reportero: exige todos sus datos personales
            rep_nuevo = Reportero(
                dni=dni_limpio,
                nombre=self._obligatorio(nombre or "", "nombre"),
                apellidos=self._obligatorio(apellidos or "", "apellidos"),
                direccion=self._obligatorio(direccion or "", "dirección"),
                ciudad=self._obligatorio(ciudad or "", "ciudad"),
                codigo_postal=self._obligatorio(codigo_postal or "", "código postal"),
                telefono=self._obligatorio(telefono or "", "teléfono"),
                categoria_nivel=None,
            )
            self.reporteros.append(rep_nuevo)
            reportero = rep_nuevo
        else:
            # Restricción: no más de una solicitud por reportero en el mismo mes y año
            mismo_mes = any(
                s.reportero_dni == dni_limpio
                and s.fecha.month == fecha.month
                and s.fecha.year == fecha.year
                for s in self.solicitudes
            )
            if mismo_mes:
                raise ValueError(
                    f"El reportero {reportero.nombre_completo} ({dni_limpio}) ya ha presentado "
                    f"una solicitud en {fecha.month:02d}/{fecha.year}. Solo se permite una por mes."
                )

        solicitud = Solicitud(
            reportero_dni=reportero.dni,
            fecha=fecha,
            resumen_cv=cv_limpio,
            equipo_fotografico=equipo_fotografico,
            estado="Pendiente",
            categoria_asignada=None,
        )
        self.solicitudes.append(solicitud)
        self._guardar_estado()
        return solicitud

    # --- 1.2 Aprobar solicitudes ---
    def aprobar_solicitud(self, solicitud_id: int, nivel_categoria: int) -> Solicitud:
        solicitud = self.obtener_solicitud(solicitud_id)
        if not solicitud:
            raise ValueError(f"No existe ninguna solicitud con ID {solicitud_id}.")
        if solicitud.estado == "Aprobada":
            raise ValueError(f"La solicitud #{solicitud_id} ya figura como aprobada.")
        if not self.obtener_categoria(nivel_categoria):
            raise ValueError(f"No existe la categoría de nivel {nivel_categoria}.")

        reportero = self.obtener_reportero(solicitud.reportero_dni)
        if not reportero:
            raise ValueError(f"No se encontró el reportero asociado al DNI {solicitud.reportero_dni}.")

        solicitud.marcar_aprobada(nivel_categoria)
        reportero.aprobar_en_categoria(nivel_categoria)
        self._guardar_estado()
        return solicitud

    # --- 1.3 Gestionar categorías ---
    def actualizar_precio_categoria(self, nivel: int, nuevo_precio_por_hoja: float) -> Categoria:
        categoria = self.obtener_categoria(nivel)
        if not categoria:
            raise ValueError(f"No existe la categoría de nivel {nivel}.")
        if nuevo_precio_por_hoja <= 0:
            raise ValueError("El nuevo precio por hoja escrita debe ser mayor que 0.")

        categoria.precio_por_hoja = round(nuevo_precio_por_hoja, 2)
        self._guardar_estado()
        return categoria

    # --- 1.4 Promocionar reportero ---
    def promocionar_reportero(self, dni: str, nuevo_nivel: int) -> Reportero:
        reportero = self.obtener_reportero(dni)
        if not reportero:
            raise ValueError(f"No existe ningún reportero con DNI {dni}.")
        if not self.obtener_categoria(nuevo_nivel):
            raise ValueError(f"No existe la categoría de nivel {nuevo_nivel}.")

        reportero.promocionar_a_categoria(nuevo_nivel)
        self._guardar_estado()
        return reportero