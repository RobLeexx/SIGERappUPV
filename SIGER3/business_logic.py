from datetime import datetime
from typing import List, Optional

from backend import RepositorioSIGER

FORMATO_FECHA = "%d/%m/%Y"


# ==========================================
# ENTIDADES DEL MODELO DE DOMINIO
# ==========================================

class Categoria:
    """Representa uno de los 4 niveles de calidad de reporteros y su tarifa por hoja/foto."""

    def __init__(self, nivel: int, nombre: str, precio_por_hoja: float):
        if nivel not in (1, 2, 3, 4):
            raise ValueError("El nivel de categoría debe estar comprendido entre 1 y 4.")
        if precio_por_hoja <= 0:
            raise ValueError("El precio por hoja escrita / foto debe ser mayor que 0.")

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
        return f"Nivel {self.nivel} - {self.nombre} ({self.precio_por_hoja:.2f} €)"


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
        self.equipo_fotografico = (
            equipo_fotografico.strip() if equipo_fotografico and equipo_fotografico.strip() else None
        )
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


class Reportaje:
    """Compendio de fotos sobre un tema concreto realizado por un reportero."""

    _contador = 1

    def __init__(
        self,
        reportero_dni: str,
        num_fotos: int,
        descripcion: str,
        identificador: Optional[int] = None,
    ):
        if identificador is None:
            self.__identificador = Reportaje._contador
            Reportaje._contador += 1
        else:
            self.__identificador = identificador
            Reportaje._contador = max(Reportaje._contador, identificador + 1)

        if num_fotos <= 0:
            raise ValueError("El número de fotos del reportaje debe ser mayor que 0.")
        if not descripcion or not descripcion.strip():
            raise ValueError("La descripción del reportaje es obligatoria.")

        self.__reportero_dni = reportero_dni.strip().upper()
        self.num_fotos = num_fotos
        self.descripcion = descripcion.strip()

    @property
    def identificador(self) -> int:
        return self.__identificador

    @property
    def reportero_dni(self) -> str:
        return self.__reportero_dni

    def to_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "reportero_dni": self.reportero_dni,
            "num_fotos": self.num_fotos,
            "descripcion": self.descripcion,
        }


class Editorial:
    """Editorial cliente a la que se venden reportajes y que propone exclusivas."""

    _contador = 1

    def __init__(
        self,
        nombre: str,
        cif: str,
        direccion: str,
        identificador: Optional[int] = None,
    ):
        if identificador is None:
            self.__identificador = Editorial._contador
            Editorial._contador += 1
        else:
            self.__identificador = identificador
            Editorial._contador = max(Editorial._contador, identificador + 1)

        self.nombre = nombre.strip()
        self.cif = cif.strip().upper()
        self.direccion = direccion.strip()

    @property
    def identificador(self) -> int:
        return self.__identificador

    def to_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "nombre": self.nombre,
            "cif": self.cif,
            "direccion": self.direccion,
        }


class AlbaranCompra:
    """Albarán generado al adquirir una editorial un reportaje (no exclusivo)."""

    _contador = 1

    def __init__(
        self,
        reportaje_id: int,
        editorial_id: int,
        precio_editorial: float,
        pago_reportero: float,
        fecha_creacion: datetime,
        identificador: Optional[int] = None,
    ):
        if identificador is None:
            self.__identificador = AlbaranCompra._contador
            AlbaranCompra._contador += 1
        else:
            self.__identificador = identificador
            AlbaranCompra._contador = max(AlbaranCompra._contador, identificador + 1)

        if pago_reportero < 0:
            raise ValueError("El importe a pagar al reportero no puede ser negativo.")
        if precio_editorial < pago_reportero:
            raise ValueError(
                f"El precio a cobrar a la editorial ({precio_editorial:.2f} €) nunca puede ser menor "
                f"que el precio a pagar al reportero ({pago_reportero:.2f} €)."
            )

        self.__reportaje_id = reportaje_id
        self.__editorial_id = editorial_id
        self.__precio_editorial = round(precio_editorial, 2)
        self.__pago_reportero = round(pago_reportero, 2)
        self.__fecha_creacion = fecha_creacion

    @property
    def identificador(self) -> int:
        return self.__identificador

    @property
    def reportaje_id(self) -> int:
        return self.__reportaje_id

    @property
    def editorial_id(self) -> int:
        return self.__editorial_id

    @property
    def precio_editorial(self) -> float:
        return self.__precio_editorial

    @property
    def pago_reportero(self) -> float:
        return self.__pago_reportero

    @property
    def margen_agencia(self) -> float:
        return round(self.__precio_editorial - self.__pago_reportero, 2)

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    def to_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "reportaje_id": self.reportaje_id,
            "editorial_id": self.editorial_id,
            "precio_editorial": self.precio_editorial,
            "pago_reportero": self.pago_reportero,
            "fecha_creacion": self.fecha_creacion.strftime(FORMATO_FECHA),
        }


class Exclusiva:
    """Propuesta de fotos sobre una temática concreta realizada por una editorial."""

    _contador = 1
    ESTADOS = ("Ofertada", "Asignada", "Finalizada")

    def __init__(
        self,
        editorial_id: int,
        tematica: str,
        precio_reportero: float,
        fecha_creacion: datetime,
        estado: str = "Ofertada",
        reportero_dni: Optional[str] = None,
        fecha_asignacion: Optional[datetime] = None,
        fecha_finalizacion: Optional[datetime] = None,
        identificador: Optional[int] = None,
    ):
        if identificador is None:
            self.__identificador = Exclusiva._contador
            Exclusiva._contador += 1
        else:
            self.__identificador = identificador
            Exclusiva._contador = max(Exclusiva._contador, identificador + 1)

        if estado not in self.ESTADOS:
            raise ValueError(f"Estado de exclusiva no válido: {estado}")
        if not tematica or not tematica.strip():
            raise ValueError("La descripción de la temática es obligatoria.")
        if precio_reportero <= 0:
            raise ValueError("El precio a pagar al reportero debe ser mayor que 0.")

        self.__editorial_id = editorial_id
        self.tematica = tematica.strip()
        self.precio_reportero = round(precio_reportero, 2)
        self.__fecha_creacion = fecha_creacion
        self.__estado = estado
        self.__reportero_dni: Optional[str] = reportero_dni.strip().upper() if reportero_dni else None
        self.__fecha_asignacion: Optional[datetime] = fecha_asignacion
        self.__fecha_finalizacion: Optional[datetime] = fecha_finalizacion

    @property
    def identificador(self) -> int:
        return self.__identificador

    @property
    def editorial_id(self) -> int:
        return self.__editorial_id

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def reportero_dni(self) -> Optional[str]:
        return self.__reportero_dni

    @property
    def fecha_asignacion(self) -> Optional[datetime]:
        return self.__fecha_asignacion

    @property
    def fecha_finalizacion(self) -> Optional[datetime]:
        return self.__fecha_finalizacion

    def asignar(self, reportero_dni: str, fecha_asignacion: datetime) -> None:
        if self.__estado == "Finalizada":
            raise ValueError("Una exclusiva finalizada no puede asignarse a ningún reportero.")
        if self.__estado == "Asignada" or self.__reportero_dni is not None:
            raise ValueError(
                f"La exclusiva #{self.__identificador} ya está asignada al reportero {self.__reportero_dni}."
            )
        if fecha_asignacion < self.__fecha_creacion:
            raise ValueError(
                f"La fecha de asignación ({fecha_asignacion.strftime(FORMATO_FECHA)}) no puede ser "
                f"inferior a la fecha de creación ({self.__fecha_creacion.strftime(FORMATO_FECHA)})."
            )

        self.__reportero_dni = reportero_dni.strip().upper()
        self.__fecha_asignacion = fecha_asignacion
        self.__estado = "Asignada"

    def finalizar(self, fecha_finalizacion: datetime) -> None:
        if self.__estado != "Asignada" or self.__fecha_asignacion is None:
            raise ValueError("Solo se puede finalizar una exclusiva que esté actualmente asignada.")
        if fecha_finalizacion < self.__fecha_asignacion:
            raise ValueError(
                f"La fecha de finalización ({fecha_finalizacion.strftime(FORMATO_FECHA)}) debe ser "
                f"superior o igual a la fecha de asignación ({self.__fecha_asignacion.strftime(FORMATO_FECHA)})."
            )

        self.__fecha_finalizacion = fecha_finalizacion
        # Al finalizar la exclusiva, se desasigna el reportero que la estaba realizando
        self.__reportero_dni = None
        self.__estado = "Finalizada"

    def to_dict(self) -> dict:
        return {
            "identificador": self.identificador,
            "editorial_id": self.editorial_id,
            "tematica": self.tematica,
            "precio_reportero": self.precio_reportero,
            "fecha_creacion": self.fecha_creacion.strftime(FORMATO_FECHA),
            "estado": self.estado,
            "reportero_dni": self.reportero_dni,
            "fecha_asignacion": self.fecha_asignacion.strftime(FORMATO_FECHA) if self.fecha_asignacion else None,
            "fecha_finalizacion": self.fecha_finalizacion.strftime(FORMATO_FECHA) if self.fecha_finalizacion else None,
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
        self.reportajes: List[Reportaje] = []
        self.editoriales: List[Editorial] = []
        self.albaranes: List[AlbaranCompra] = []
        self.exclusivas: List[Exclusiva] = []
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

        for item in datos["reportajes"]:
            self.reportajes.append(
                Reportaje(
                    reportero_dni=item["reportero_dni"],
                    num_fotos=item["num_fotos"],
                    descripcion=item["descripcion"],
                    identificador=item["identificador"],
                )
            )

        for item in datos["editoriales"]:
            self.editoriales.append(
                Editorial(
                    nombre=item["nombre"],
                    cif=item["cif"],
                    direccion=item["direccion"],
                    identificador=item["identificador"],
                )
            )

        for item in datos["albaranes"]:
            self.albaranes.append(
                AlbaranCompra(
                    reportaje_id=item["reportaje_id"],
                    editorial_id=item["editorial_id"],
                    precio_editorial=item["precio_editorial"],
                    pago_reportero=item["pago_reportero"],
                    fecha_creacion=datetime.strptime(item["fecha_creacion"], FORMATO_FECHA),
                    identificador=item["identificador"],
                )
            )

        for item in datos["exclusivas"]:
            f_asig = (
                datetime.strptime(item["fecha_asignacion"], FORMATO_FECHA)
                if item.get("fecha_asignacion")
                else None
            )
            f_fin = (
                datetime.strptime(item["fecha_finalizacion"], FORMATO_FECHA)
                if item.get("fecha_finalizacion")
                else None
            )
            self.exclusivas.append(
                Exclusiva(
                    editorial_id=item["editorial_id"],
                    tematica=item["tematica"],
                    precio_reportero=item["precio_reportero"],
                    fecha_creacion=datetime.strptime(item["fecha_creacion"], FORMATO_FECHA),
                    estado=item.get("estado", "Ofertada"),
                    reportero_dni=item.get("reportero_dni"),
                    fecha_asignacion=f_asig,
                    fecha_finalizacion=f_fin,
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
            "reportajes": [rp.to_dict() for rp in self.reportajes],
            "editoriales": [ed.to_dict() for ed in self.editoriales],
            "albaranes": [al.to_dict() for al in self.albaranes],
            "exclusivas": [ex.to_dict() for ex in self.exclusivas],
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

    def obtener_reportaje(self, identificador: int) -> Optional[Reportaje]:
        return next((r for r in self.reportajes if r.identificador == identificador), None)

    def obtener_editorial(self, identificador: int) -> Optional[Editorial]:
        return next((e for e in self.editoriales if e.identificador == identificador), None)

    def obtener_exclusiva(self, identificador: int) -> Optional[Exclusiva]:
        return next((ex for ex in self.exclusivas if ex.identificador == identificador), None)

    def listar_solicitudes_aprobadas(self) -> List[Solicitud]:
        return [s for s in self.solicitudes if s.estado == "Aprobada"]

    def listar_reporteros_en_bolsa(self) -> List[Reportero]:
        return [r for r in self.reporteros if r.en_bolsa]

    def solicitudes_de_reportero(self, dni: str) -> List[Solicitud]:
        dni_limpio = dni.strip().upper()
        return [s for s in self.solicitudes if s.reportero_dni == dni_limpio]

    def listar_exclusivas_ofertadas(self) -> List[Exclusiva]:
        return [ex for ex in self.exclusivas if ex.estado == "Ofertada"]

    def listar_exclusivas_asignadas(self) -> List[Exclusiva]:
        return [ex for ex in self.exclusivas if ex.estado == "Asignada"]

    def listar_exclusivas_finalizadas(self) -> List[Exclusiva]:
        return [ex for ex in self.exclusivas if ex.estado == "Finalizada"]

    def calcular_pago_reportero_reportaje(self, reportaje_id: int) -> float:
        reportaje = self.obtener_reportaje(reportaje_id)
        if not reportaje:
            raise ValueError(f"No existe ningún reportaje con ID {reportaje_id}.")
        reportero = self.obtener_reportero(reportaje.reportero_dni)
        if not reportero or not reportero.en_bolsa:
            raise ValueError("El reportero del reportaje no está dado de alta en la bolsa.")
        categoria = self.obtener_categoria(reportero.categoria_nivel or 0)
        if not categoria:
            raise ValueError("No se encontró la categoría asignada al reportero.")
        return round(categoria.precio_por_hoja * reportaje.num_fotos, 2)

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
            raise ValueError("El nuevo precio debe ser mayor que 0.")

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

    # --- 2.1 Dar de alta un reportaje nuevo ---
    def crear_reportaje(self, reportero_dni: str, num_fotos: int, descripcion: str) -> Reportaje:
        dni_limpio = self._obligatorio(reportero_dni, "DNI del reportero").upper()
        reportero = self.obtener_reportero(dni_limpio)
        if not reportero:
            raise ValueError(f"No existe ningún reportero con DNI {dni_limpio}.")
        if not reportero.en_bolsa:
            raise ValueError(
                f"El reportero {reportero.nombre_completo} ({dni_limpio}) no forma parte de la bolsa."
            )

        reportaje = Reportaje(
            reportero_dni=dni_limpio,
            num_fotos=num_fotos,
            descripcion=descripcion,
        )
        self.reportajes.append(reportaje)
        self._guardar_estado()
        return reportaje

    # --- 2.2 Gestionar datos de las editoriales ---
    def crear_editorial(self, nombre: str, cif: str, direccion: str) -> Editorial:
        editorial = Editorial(
            nombre=self._obligatorio(nombre, "nombre"),
            cif=self._obligatorio(cif, "CIF").upper(),
            direccion=self._obligatorio(direccion, "dirección"),
        )
        self.editoriales.append(editorial)
        self._guardar_estado()
        return editorial

    def editar_editorial(
        self,
        editorial_id: int,
        nombre: str,
        cif: str,
        direccion: str,
    ) -> Editorial:
        editorial = self.obtener_editorial(editorial_id)
        if not editorial:
            raise ValueError(f"No existe ninguna editorial con ID {editorial_id}.")

        editorial.nombre = self._obligatorio(nombre, "nombre")
        editorial.cif = self._obligatorio(cif, "CIF").upper()
        editorial.direccion = self._obligatorio(direccion, "dirección")
        self._guardar_estado()
        return editorial

    def borrar_editorial(self, editorial_id: int) -> None:
        editorial = self.obtener_editorial(editorial_id)
        if not editorial:
            raise ValueError(f"No existe ninguna editorial con ID {editorial_id}.")
        self.editoriales = [e for e in self.editoriales if e.identificador != editorial_id]
        self._guardar_estado()

    # --- 2.3 Adquirir un reportaje ---
    def adquirir_reportaje(
        self,
        reportaje_id: int,
        editorial_id: int,
        precio_editorial: float,
        fecha_creacion: datetime,
    ) -> AlbaranCompra:
        reportaje = self.obtener_reportaje(reportaje_id)
        if not reportaje:
            raise ValueError(f"No existe ningún reportaje con ID {reportaje_id}.")

        editorial = self.obtener_editorial(editorial_id)
        if not editorial:
            raise ValueError(f"No existe ninguna editorial con ID {editorial_id}.")

        pago_reportero = self.calcular_pago_reportero_reportaje(reportaje_id)

        albaran = AlbaranCompra(
            reportaje_id=reportaje.identificador,
            editorial_id=editorial.identificador,
            precio_editorial=precio_editorial,
            pago_reportero=pago_reportero,
            fecha_creacion=fecha_creacion,
        )
        self.albaranes.append(albaran)
        self._guardar_estado()
        return albaran

    # --- 3.1 Dar de alta una exclusiva nueva ---
    def crear_exclusiva(
        self,
        editorial_id: int,
        tematica: str,
        precio_reportero: float,
        fecha_creacion: datetime,
    ) -> Exclusiva:
        editorial = self.obtener_editorial(editorial_id)
        if not editorial:
            raise ValueError(f"No existe ninguna editorial con ID {editorial_id}.")

        exclusiva = Exclusiva(
            editorial_id=editorial.identificador,
            tematica=tematica,
            precio_reportero=precio_reportero,
            fecha_creacion=fecha_creacion,
        )
        self.exclusivas.append(exclusiva)
        self._guardar_estado()
        return exclusiva

    # --- 3.2 Asignar exclusiva a reportero ---
    def asignar_exclusiva(
        self,
        exclusiva_id: int,
        reportero_dni: str,
        fecha_asignacion: datetime,
    ) -> Exclusiva:
        exclusiva = self.obtener_exclusiva(exclusiva_id)
        if not exclusiva:
            raise ValueError(f"No existe ninguna exclusiva con ID {exclusiva_id}.")

        dni_limpio = self._obligatorio(reportero_dni, "DNI del reportero").upper()
        reportero = self.obtener_reportero(dni_limpio)
        if not reportero:
            raise ValueError(f"No existe ningún reportero con DNI {dni_limpio}.")
        if not reportero.en_bolsa:
            raise ValueError(
                f"El reportero {reportero.nombre_completo} ({dni_limpio}) no está en la bolsa de reporteros."
            )

        exclusiva.asignar(dni_limpio, fecha_asignacion)
        self._guardar_estado()
        return exclusiva

    # --- 3.3 Finalizar la exclusiva ---
    def finalizar_exclusiva(
        self,
        exclusiva_id: int,
        fecha_finalizacion: datetime,
    ) -> Exclusiva:
        exclusiva = self.obtener_exclusiva(exclusiva_id)
        if not exclusiva:
            raise ValueError(f"No existe ninguna exclusiva con ID {exclusiva_id}.")

        exclusiva.finalizar(fecha_finalizacion)
        self._guardar_estado()
        return exclusiva