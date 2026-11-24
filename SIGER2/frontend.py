import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Dict, Optional

from backend import RepositorioSIGER
from business_logic import FORMATO_FECHA, ServicioSIGER


class InterfazSIGER(tk.Tk):
    """Interfaz gráfica de SIGER (Sistema de Gestión de Reporteros - Journ SL)."""

    def __init__(self, servicio: ServicioSIGER):
        super().__init__()
        self.servicio = servicio

        self.title("SIGER — Sistema de Gestión de Reporteros (Journ SL)")
        self.geometry("1260x740")
        self.minsize(1100, 640)

        self._mapa_cat_combo: Dict[str, int] = {}
        self._mapa_rep_bolsa_combo: Dict[str, str] = {}
        self._mapa_reportaje_combo: Dict[str, int] = {}
        self._mapa_editorial_combo: Dict[str, int] = {}

        self._solicitud_sel_id: Optional[int] = None
        self._editorial_sel_id: Optional[int] = None

        self._configurar_estilos()
        self._construir_ui()
        self._refrescar_todo()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Titulo.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Subtitulo.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Destacado.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1b5e20")

    def _construir_ui(self) -> None:
        cabecera = ttk.Frame(self, padding=(12, 8))
        cabecera.pack(fill=tk.X)
        ttk.Label(cabecera, text="SIGER — JOURN SL", style="Titulo.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            cabecera,
            text="Formato de fecha manual: DD/MM/AAAA",
            foreground="#555555",
        ).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tab_solicitudes = ttk.Frame(self.notebook, padding=10)
        self.tab_aprobacion = ttk.Frame(self.notebook, padding=10)
        self.tab_categorias = ttk.Frame(self.notebook, padding=10)
        self.tab_promocion = ttk.Frame(self.notebook, padding=10)
        self.tab_reportajes = ttk.Frame(self.notebook, padding=10)
        self.tab_editoriales = ttk.Frame(self.notebook, padding=10)
        self.tab_albaranes = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_solicitudes, text="1.1 Solicitudes")
        self.notebook.add(self.tab_aprobacion, text="1.2 Aprobar")
        self.notebook.add(self.tab_categorias, text="1.3 Categorías")
        self.notebook.add(self.tab_promocion, text="1.4 Promocionar")
        self.notebook.add(self.tab_reportajes, text="2.1 Reportajes")
        self.notebook.add(self.tab_editoriales, text="2.2 Editoriales")
        self.notebook.add(self.tab_albaranes, text="2.3 Adquirir / Albaranes")

        self._construir_tab_solicitudes()
        self._construir_tab_aprobacion()
        self._construir_tab_categorias()
        self._construir_tab_promocion()
        self._construir_tab_reportajes()
        self._construir_tab_editoriales()
        self._construir_tab_albaranes()

    @staticmethod
    def _parsear_fecha(texto: str, campo: str) -> datetime:
        valor = texto.strip()
        if not valor:
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        try:
            return datetime.strptime(valor, FORMATO_FECHA)
        except ValueError as exc:
            raise ValueError(f"Formato de fecha inválido en '{campo}'. Usa DD/MM/AAAA.") from exc

    @staticmethod
    def _parsear_entero(texto: str, campo: str) -> int:
        valor = texto.strip()
        if not valor:
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        try:
            return int(valor)
        except ValueError as exc:
            raise ValueError(f"El campo '{campo}' debe ser un número entero.") from exc

    @staticmethod
    def _parsear_real(texto: str, campo: str) -> float:
        valor = texto.strip().replace(",", ".")
        if not valor:
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        try:
            return float(valor)
        except ValueError as exc:
            raise ValueError(f"El campo '{campo}' debe ser un número decimal válido.") from exc

    @staticmethod
    def _crear_tabla(contenedor: ttk.Frame, columnas: tuple, anchos: tuple) -> ttk.Treeview:
        frame = ttk.Frame(contenedor)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=columnas, show="headings", selectmode="browse")
        for col, ancho in zip(columnas, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor=tk.W)

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ==========================================
    # 1.1 ALTA Y LISTADO HISTÓRICO DE SOLICITUDES
    # ==========================================

    def _construir_tab_solicitudes(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_solicitudes, text="Nueva Solicitud de Reportero", padding=10)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(panel_izq, text="DNI del Reportero (*):").grid(row=0, column=0, sticky=tk.W, pady=2)
        fila_dni = ttk.Frame(panel_izq)
        fila_dni.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.ent_sol_dni = ttk.Entry(fila_dni, width=16)
        self.ent_sol_dni.pack(side=tk.LEFT)
        ttk.Button(fila_dni, text="Comprobar DNI", command=self._comprobar_dni_reportero).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        self.lbl_estado_dni = ttk.Label(
            panel_izq, text="Introduce un DNI y pulsa 'Comprobar DNI'", foreground="#1565c0"
        )
        self.lbl_estado_dni.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        ttk.Label(panel_izq, text="Fecha Solicitud (DD/MM/AAAA) (*):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ent_sol_fecha = ttk.Entry(panel_izq, width=28)
        self.ent_sol_fecha.grid(row=2, column=1, pady=2)

        ttk.Label(panel_izq, text="Equipo Fotográfico (opcional):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ent_sol_equipo = ttk.Entry(panel_izq, width=28)
        self.ent_sol_equipo.grid(row=3, column=1, pady=2)

        ttk.Label(panel_izq, text="Resumen CV (*):").grid(row=4, column=0, sticky=tk.NW, pady=2)
        self.txt_sol_cv = tk.Text(panel_izq, width=28, height=4)
        self.txt_sol_cv.grid(row=4, column=1, pady=2)

        ttk.Separator(panel_izq, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=6)
        ttk.Label(
            panel_izq, text="Datos Personales (obligatorios si es su 1.ª solicitud):", style="Subtitulo.TLabel"
        ).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        campos_personales = [
            ("Nombre:", "ent_rep_nombre"),
            ("Apellidos:", "ent_rep_apellidos"),
            ("Dirección:", "ent_rep_direccion"),
            ("Ciudad:", "ent_rep_ciudad"),
            ("Código Postal:", "ent_rep_cp"),
            ("Teléfono:", "ent_rep_telefono"),
        ]
        self._entradas_personales = {}
        for idx, (etiqueta, attr) in enumerate(campos_personales, start=7):
            ttk.Label(panel_izq, text=etiqueta).grid(row=idx, column=0, sticky=tk.W, pady=2)
            entrada = ttk.Entry(panel_izq, width=28)
            entrada.grid(row=idx, column=1, pady=2)
            setattr(self, attr, entrada)
            self._entradas_personales[attr] = entrada

        btns = ttk.Frame(panel_izq)
        btns.grid(row=14, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="Registrar Solicitud", command=self._registrar_solicitud).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Limpiar Formulario", command=self._limpiar_form_solicitud).pack(side=tk.LEFT, padx=4)

        panel_der = ttk.LabelFrame(self.tab_solicitudes, text="Histórico General de Solicitudes", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_solicitudes = self._crear_tabla(
            panel_der,
            ("ID", "Fecha", "DNI", "Reportero", "Estado", "Cat.", "Equipo Foto", "Resumen CV"),
            (50, 90, 95, 140, 85, 50, 120, 180),
        )

    def _comprobar_dni_reportero(self) -> None:
        dni = self.ent_sol_dni.get().strip().upper()
        if not dni:
            messagebox.showwarning("Aviso", "Introduce un DNI para comprobar.")
            return
        rep = self.servicio.obtener_reportero(dni)
        if rep:
            hist = self.servicio.solicitudes_de_reportero(dni)
            self.lbl_estado_dni.config(
                text=f"Reportero conocido: {rep.nombre_completo} ({len(hist)} solicitud/es previas)",
                foreground="#2e7d32",
            )
            self.ent_rep_nombre.delete(0, tk.END)
            self.ent_rep_nombre.insert(0, rep.nombre)
            self.ent_rep_apellidos.delete(0, tk.END)
            self.ent_rep_apellidos.insert(0, rep.apellidos)
            self.ent_rep_direccion.delete(0, tk.END)
            self.ent_rep_direccion.insert(0, rep.direccion)
            self.ent_rep_ciudad.delete(0, tk.END)
            self.ent_rep_ciudad.insert(0, rep.ciudad)
            self.ent_rep_cp.delete(0, tk.END)
            self.ent_rep_cp.insert(0, rep.codigo_postal)
            self.ent_rep_telefono.delete(0, tk.END)
            self.ent_rep_telefono.insert(0, rep.telefono)
            for entrada in self._entradas_personales.values():
                entrada.config(state="readonly")
        else:
            for entrada in self._entradas_personales.values():
                entrada.config(state="normal")
            self.lbl_estado_dni.config(
                text="Nuevo reportero: completa todos sus datos personales",
                foreground="#c62828",
            )

    def _registrar_solicitud(self) -> None:
        try:
            dni = self.ent_sol_dni.get()
            fecha = self._parsear_fecha(self.ent_sol_fecha.get(), "Fecha de solicitud")
            equipo = self.ent_sol_equipo.get().strip() or None
            cv = self.txt_sol_cv.get("1.0", tk.END).strip()

            sol = self.servicio.registrar_solicitud(
                dni=dni,
                fecha=fecha,
                resumen_cv=cv,
                equipo_fotografico=equipo,
                nombre=self.ent_rep_nombre.get(),
                apellidos=self.ent_rep_apellidos.get(),
                direccion=self.ent_rep_direccion.get(),
                ciudad=self.ent_rep_ciudad.get(),
                codigo_postal=self.ent_rep_cp.get(),
                telefono=self.ent_rep_telefono.get(),
            )
            messagebox.showinfo(
                "Solicitud Registrada",
                f"Solicitud #{sol.identificador} registrada con estado '{sol.estado}'.",
            )
            self._limpiar_form_solicitud()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    def _limpiar_form_solicitud(self) -> None:
        self.ent_sol_dni.delete(0, tk.END)
        self.ent_sol_fecha.delete(0, tk.END)
        self.ent_sol_equipo.delete(0, tk.END)
        self.txt_sol_cv.delete("1.0", tk.END)
        for entrada in self._entradas_personales.values():
            entrada.config(state="normal")
            entrada.delete(0, tk.END)
        self.lbl_estado_dni.config(
            text="Introduce un DNI y pulsa 'Comprobar DNI'", foreground="#1565c0"
        )

    # ==========================================
    # 1.2 APROBAR SOLICITUDES
    # ==========================================

    def _construir_tab_aprobacion(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_aprobacion, text="Aprobar Solicitud Seleccionada", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_apr_sel = ttk.Label(panel_izq, text="Solicitud seleccionada: Ninguna", style="Subtitulo.TLabel")
        self.lbl_apr_sel.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(panel_izq, text="Categoría inicial (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_apr_cat = ttk.Combobox(panel_izq, width=28, state="readonly")
        self.cmb_apr_cat.grid(row=1, column=1, pady=4)

        ttk.Button(panel_izq, text="Aprobar e Incorporar a Bolsa", command=self._aprobar_solicitud).grid(
            row=2, column=0, columnspan=2, pady=(12, 0)
        )

        panel_der = ttk.Frame(self.tab_aprobacion)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        box_pend = ttk.LabelFrame(panel_der, text="Solicitudes Pendientes (Clic para seleccionar)", padding=8)
        box_pend.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.tree_pendientes = self._crear_tabla(
            box_pend,
            ("ID", "Fecha", "DNI", "Reportero", "Equipo Foto", "Resumen CV"),
            (50, 90, 95, 160, 130, 210),
        )
        self.tree_pendientes.bind("<<TreeviewSelect>>", self._seleccionar_pendiente)

        box_aprob = ttk.LabelFrame(panel_der, text="Solicitudes Aceptadas / Aprobadas", padding=8)
        box_aprob.pack(fill=tk.BOTH, expand=True)
        self.tree_aprobadas = self._crear_tabla(
            box_aprob,
            ("ID", "Fecha", "DNI", "Reportero", "Categoría Asignada"),
            (50, 95, 100, 180, 220),
        )

    def _seleccionar_pendiente(self, _event) -> None:
        sel = self.tree_pendientes.selection()
        if not sel:
            return
        valores = self.tree_pendientes.item(sel[0], "values")
        self._solicitud_sel_id = int(valores[0])
        self.lbl_apr_sel.config(
            text=f"Solicitud seleccionada: #{self._solicitud_sel_id} ({valores[3]})"
        )

    def _aprobar_solicitud(self) -> None:
        try:
            if self._solicitud_sel_id is None:
                raise ValueError("Selecciona primero una solicitud pendiente en la tabla.")
            cat_txt = self.cmb_apr_cat.get()
            if cat_txt not in self._mapa_cat_combo:
                raise ValueError("Selecciona la categoría en la que entra el reportero.")
            nivel = self._mapa_cat_combo[cat_txt]

            sol = self.servicio.aprobar_solicitud(self._solicitud_sel_id, nivel)
            messagebox.showinfo(
                "Solicitud Aprobada",
                f"Solicitud #{sol.identificador} aprobada. Reportero incorporado a la bolsa en Nivel {nivel}.",
            )
            self._solicitud_sel_id = None
            self.lbl_apr_sel.config(text="Solicitud seleccionada: Ninguna")
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    # ==========================================
    # 1.3 GESTIONAR CATEGORÍAS
    # ==========================================

    def _construir_tab_categorias(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_categorias, text="Actualizar Tarifa por Hoja / Foto", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(panel_izq, text="Categoría (*):").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cmb_cat_precio = ttk.Combobox(panel_izq, width=28, state="readonly")
        self.cmb_cat_precio.grid(row=0, column=1, pady=4)

        ttk.Label(panel_izq, text="Nuevo Precio (€) (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_cat_precio = ttk.Entry(panel_izq, width=30)
        self.ent_cat_precio.grid(row=1, column=1, pady=4)

        ttk.Button(panel_izq, text="Actualizar Tarifa", command=self._actualizar_precio_categoria).grid(
            row=2, column=0, columnspan=2, pady=(12, 0)
        )

        panel_der = ttk.LabelFrame(self.tab_categorias, text="Categorías de Reporteros (4 Niveles)", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_categorias = self._crear_tabla(
            panel_der,
            ("Nivel", "Nombre de Categoría", "Tarifa por Hoja / Foto (€)"),
            (80, 260, 160),
        )

    def _actualizar_precio_categoria(self) -> None:
        try:
            cat_txt = self.cmb_cat_precio.get()
            if cat_txt not in self._mapa_cat_combo:
                raise ValueError("Selecciona una categoría.")
            nivel = self._mapa_cat_combo[cat_txt]
            nuevo_precio = self._parsear_real(self.ent_cat_precio.get(), "Nuevo precio")

            cat = self.servicio.actualizar_precio_categoria(nivel, nuevo_precio)
            messagebox.showinfo(
                "Tarifa Actualizada",
                f"{cat.nombre} ahora tiene una tarifa de {cat.precio_por_hoja:.2f} €.",
            )
            self.ent_cat_precio.delete(0, tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    # ==========================================
    # 1.4 PROMOCIONAR REPORTERO
    # ==========================================

    def _construir_tab_promocion(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_promocion, text="Ascender Reportero de Categoría", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(panel_izq, text="Reportero en bolsa (*):").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cmb_promo_rep = ttk.Combobox(panel_izq, width=30, state="readonly")
        self.cmb_promo_rep.grid(row=0, column=1, pady=4)

        ttk.Label(panel_izq, text="Nueva categoría superior (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_promo_cat = ttk.Combobox(panel_izq, width=30, state="readonly")
        self.cmb_promo_cat.grid(row=1, column=1, pady=4)

        ttk.Button(panel_izq, text="Promocionar Reportero", command=self._promocionar_reportero).grid(
            row=2, column=0, columnspan=2, pady=(12, 0)
        )

        panel_der = ttk.LabelFrame(self.tab_promocion, text="Bolsa de Reporteros Activos", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_bolsa = self._crear_tabla(
            panel_der,
            ("DNI", "Nombre y Apellidos", "Teléfono", "Ciudad", "Categoría Actual", "Tarifa (€)"),
            (100, 180, 105, 110, 170, 110),
        )

    def _promocionar_reportero(self) -> None:
        try:
            rep_txt = self.cmb_promo_rep.get()
            if rep_txt not in self._mapa_rep_bolsa_combo:
                raise ValueError("Selecciona un reportero de la bolsa.")
            dni = self._mapa_rep_bolsa_combo[rep_txt]

            cat_txt = self.cmb_promo_cat.get()
            if cat_txt not in self._mapa_cat_combo:
                raise ValueError("Selecciona la categoría superior de destino.")
            nuevo_nivel = self._mapa_cat_combo[cat_txt]

            rep = self.servicio.promocionar_reportero(dni, nuevo_nivel)
            messagebox.showinfo(
                "Promoción Registrada",
                f"{rep.nombre_completo} ({rep.dni}) promocionado a Nivel {rep.categoria_nivel}.",
            )
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    # ==========================================
    # 2.1 DAR DE ALTA UN REPORTAJE NUEVO
    # ==========================================

    def _construir_tab_reportajes(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_reportajes, text="Dar de Alta Reportaje", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(panel_izq, text="Reportero en bolsa (*):").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cmb_rpt_rep = ttk.Combobox(panel_izq, width=32, state="readonly")
        self.cmb_rpt_rep.grid(row=0, column=1, pady=4)

        ttk.Label(panel_izq, text="Número de fotos (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_rpt_fotos = ttk.Entry(panel_izq, width=34)
        self.ent_rpt_fotos.grid(row=1, column=1, pady=4)

        ttk.Label(panel_izq, text="Descripción breve (*):").grid(row=2, column=0, sticky=tk.NW, pady=4)
        self.txt_rpt_desc = tk.Text(panel_izq, width=34, height=5)
        self.txt_rpt_desc.grid(row=2, column=1, pady=4)

        ttk.Button(panel_izq, text="Registrar Reportaje", command=self._crear_reportaje).grid(
            row=3, column=0, columnspan=2, pady=(12, 0)
        )

        panel_der = ttk.LabelFrame(self.tab_reportajes, text="Reportajes Disponibles en el Sistema", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_reportajes = self._crear_tabla(
            panel_der,
            ("ID", "DNI", "Reportero", "Cat.", "N.º Fotos", "Pago Base Reportero (€)", "Descripción"),
            (55, 95, 160, 55, 80, 145, 250),
        )

    def _crear_reportaje(self) -> None:
        try:
            rep_txt = self.cmb_rpt_rep.get()
            if rep_txt not in self._mapa_rep_bolsa_combo:
                raise ValueError("Selecciona un reportero de la bolsa.")
            dni = self._mapa_rep_bolsa_combo[rep_txt]
            num_fotos = self._parsear_entero(self.ent_rpt_fotos.get(), "Número de fotos")
            descripcion = self.txt_rpt_desc.get("1.0", tk.END).strip()

            rpt = self.servicio.crear_reportaje(dni, num_fotos, descripcion)
            messagebox.showinfo(
                "Reportaje Creado",
                f"Reportaje RPT-{rpt.identificador} registrado con {rpt.num_fotos} fotos.",
            )
            self.ent_rpt_fotos.delete(0, tk.END)
            self.txt_rpt_desc.delete("1.0", tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    # ==========================================
    # 2.2 GESTIONAR DATOS DE LAS EDITORIALES
    # ==========================================

    def _construir_tab_editoriales(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_editoriales, text="Datos de la Editorial", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lbl_edi_modo = ttk.Label(panel_izq, text="Modo: Nueva Editorial", style="Subtitulo.TLabel")
        self.lbl_edi_modo.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        ttk.Label(panel_izq, text="Nombre (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_edi_nombre = ttk.Entry(panel_izq, width=30)
        self.ent_edi_nombre.grid(row=1, column=1, pady=4)

        ttk.Label(panel_izq, text="CIF (*):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_edi_cif = ttk.Entry(panel_izq, width=30)
        self.ent_edi_cif.grid(row=2, column=1, pady=4)

        ttk.Label(panel_izq, text="Dirección (*):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.ent_edi_direccion = ttk.Entry(panel_izq, width=30)
        self.ent_edi_direccion.grid(row=3, column=1, pady=4)

        btns = ttk.Frame(panel_izq)
        btns.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btns, text="Guardar Editorial", command=self._guardar_editorial).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Borrar", command=self._borrar_editorial).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Limpiar", command=self._limpiar_form_editorial).pack(side=tk.LEFT, padx=3)

        panel_der = ttk.LabelFrame(
            self.tab_editoriales, text="Editoriales Registradas (Clic para editar o borrar)", padding=10
        )
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_editoriales = self._crear_tabla(
            panel_der,
            ("ID", "Nombre", "CIF", "Dirección"),
            (60, 220, 120, 280),
        )
        self.tree_editoriales.bind("<<TreeviewSelect>>", self._seleccionar_editorial)

    def _guardar_editorial(self) -> None:
        try:
            nombre = self.ent_edi_nombre.get()
            cif = self.ent_edi_cif.get()
            direccion = self.ent_edi_direccion.get()

            if self._editorial_sel_id is None:
                edi = self.servicio.crear_editorial(nombre, cif, direccion)
                messagebox.showinfo("Éxito", f"Editorial EDI-{edi.identificador} creada.")
            else:
                edi = self.servicio.editar_editorial(self._editorial_sel_id, nombre, cif, direccion)
                messagebox.showinfo("Éxito", f"Editorial EDI-{edi.identificador} actualizada.")

            self._limpiar_form_editorial()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    def _borrar_editorial(self) -> None:
        try:
            if self._editorial_sel_id is None:
                raise ValueError("Selecciona primero una editorial en la tabla.")
            if not messagebox.askyesno("Confirmar borrado", "¿Deseas borrar la editorial seleccionada?"):
                return
            self.servicio.borrar_editorial(self._editorial_sel_id)
            messagebox.showinfo("Éxito", "Editorial borrada correctamente.")
            self._limpiar_form_editorial()
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    def _seleccionar_editorial(self, _event) -> None:
        sel = self.tree_editoriales.selection()
        if not sel:
            return
        valores = self.tree_editoriales.item(sel[0], "values")
        self._editorial_sel_id = int(valores[0])
        self.lbl_edi_modo.config(text=f"Modo: Editando EDI-{self._editorial_sel_id}")

        self.ent_edi_nombre.delete(0, tk.END)
        self.ent_edi_nombre.insert(0, valores[1])
        self.ent_edi_cif.delete(0, tk.END)
        self.ent_edi_cif.insert(0, valores[2])
        self.ent_edi_direccion.delete(0, tk.END)
        self.ent_edi_direccion.insert(0, valores[3])

    def _limpiar_form_editorial(self) -> None:
        self._editorial_sel_id = None
        self.lbl_edi_modo.config(text="Modo: Nueva Editorial")
        for ent in (self.ent_edi_nombre, self.ent_edi_cif, self.ent_edi_direccion):
            ent.delete(0, tk.END)
        self.tree_editoriales.selection_remove(self.tree_editoriales.selection())

    # ==========================================
    # 2.3 ADQUIRIR UN REPORTAJE / ALBARANES
    # ==========================================

    def _construir_tab_albaranes(self) -> None:
        panel_izq = ttk.LabelFrame(self.tab_albaranes, text="Crear Albarán de Compra", padding=12)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(panel_izq, text="Reportaje (*):").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cmb_alb_reportaje = ttk.Combobox(panel_izq, width=32, state="readonly")
        self.cmb_alb_reportaje.grid(row=0, column=1, pady=4)
        self.cmb_alb_reportaje.bind("<<ComboboxSelected>>", self._actualizar_pago_reportero_preview)

        ttk.Label(panel_izq, text="Editorial (*):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_alb_editorial = ttk.Combobox(panel_izq, width=32, state="readonly")
        self.cmb_alb_editorial.grid(row=1, column=1, pady=4)

        self.lbl_alb_pago_rep = ttk.Label(
            panel_izq, text="A pagar al reportero: 0.00 €", style="Destacado.TLabel"
        )
        self.lbl_alb_pago_rep.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 6))

        ttk.Label(panel_izq, text="Precio a cobrar Editorial (€) (*):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.ent_alb_precio_edi = ttk.Entry(panel_izq, width=34)
        self.ent_alb_precio_edi.grid(row=3, column=1, pady=4)

        ttk.Label(panel_izq, text="Fecha Creación (DD/MM/AAAA) (*):").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.ent_alb_fecha = ttk.Entry(panel_izq, width=34)
        self.ent_alb_fecha.grid(row=4, column=1, pady=4)

        ttk.Button(panel_izq, text="Emitir Albarán", command=self._emitir_albaran).grid(
            row=5, column=0, columnspan=2, pady=(12, 0)
        )

        panel_der = ttk.LabelFrame(self.tab_albaranes, text="Albaranes de Compra Emitidos", padding=10)
        panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree_albaranes = self._crear_tabla(
            panel_der,
            ("Albarán", "Fecha", "Reportaje", "Editorial", "Cobro Editorial (€)", "Pago Reportero (€)", "Agencia (€)"),
            (70, 90, 180, 160, 115, 115, 95),
        )

    def _actualizar_pago_reportero_preview(self, _event=None) -> None:
        rpt_txt = self.cmb_alb_reportaje.get()
        if rpt_txt not in self._mapa_reportaje_combo:
            self.lbl_alb_pago_rep.config(text="A pagar al reportero: 0.00 €")
            return
        rpt_id = self._mapa_reportaje_combo[rpt_txt]
        try:
            pago = self.servicio.calcular_pago_reportero_reportaje(rpt_id)
            self.lbl_alb_pago_rep.config(text=f"A pagar al reportero: {pago:.2f} €")
        except ValueError as err:
            self.lbl_alb_pago_rep.config(text=f"Aviso: {err}")

    def _emitir_albaran(self) -> None:
        try:
            rpt_txt = self.cmb_alb_reportaje.get()
            if rpt_txt not in self._mapa_reportaje_combo:
                raise ValueError("Selecciona un reportaje.")
            rpt_id = self._mapa_reportaje_combo[rpt_txt]

            edi_txt = self.cmb_alb_editorial.get()
            if edi_txt not in self._mapa_editorial_combo:
                raise ValueError("Selecciona una editorial.")
            edi_id = self._mapa_editorial_combo[edi_txt]

            precio_edi = self._parsear_real(self.ent_alb_precio_edi.get(), "Precio a cobrar a la editorial")
            fecha_creacion = self._parsear_fecha(self.ent_alb_fecha.get(), "Fecha de creación del albarán")

            alb = self.servicio.adquirir_reportaje(rpt_id, edi_id, precio_edi, fecha_creacion)
            messagebox.showinfo(
                "Albarán Emitido",
                f"Albarán ALB-{alb.identificador} registrado.\n"
                f"Cobro editorial: {alb.precio_editorial:.2f} € | "
                f"Pago reportero: {alb.pago_reportero:.2f} € | "
                f"Agencia: {alb.margen_agencia:.2f} €",
            )
            self.ent_alb_precio_edi.delete(0, tk.END)
            self.ent_alb_fecha.delete(0, tk.END)
            self._refrescar_todo()
        except (ValueError, RuntimeError) as err:
            messagebox.showerror("Error", str(err))

    # ==========================================
    # SINCRONIZACIÓN DE TODAS LAS VISTAS
    # ==========================================

    def _refrescar_todo(self) -> None:
        # 1. Categorías
        self.tree_categorias.delete(*self.tree_categorias.get_children())
        self._mapa_cat_combo.clear()
        for c in self.servicio.categorias:
            self.tree_categorias.insert("", tk.END, values=(c.nivel, c.nombre, f"{c.precio_por_hoja:.2f}"))
            etiqueta = f"Nivel {c.nivel} — {c.nombre} ({c.precio_por_hoja:.2f} €)"
            self._mapa_cat_combo[etiqueta] = c.nivel

        cats_labels = list(self._mapa_cat_combo.keys())
        self.cmb_apr_cat["values"] = cats_labels
        self.cmb_cat_precio["values"] = cats_labels
        self.cmb_promo_cat["values"] = cats_labels

        # 2. Solicitudes
        self.tree_solicitudes.delete(*self.tree_solicitudes.get_children())
        self.tree_pendientes.delete(*self.tree_pendientes.get_children())
        self.tree_aprobadas.delete(*self.tree_aprobadas.get_children())

        for s in self.servicio.solicitudes:
            rep = self.servicio.obtener_reportero(s.reportero_dni)
            nombre_rep = rep.nombre_completo if rep else s.reportero_dni
            cat_str = f"Nivel {s.categoria_asignada}" if s.categoria_asignada else "—"
            equipo_str = s.equipo_fotografico or "Sin equipo"
            fecha_str = s.fecha.strftime(FORMATO_FECHA)

            self.tree_solicitudes.insert(
                "",
                tk.END,
                values=(
                    s.identificador,
                    fecha_str,
                    s.reportero_dni,
                    nombre_rep,
                    s.estado,
                    cat_str,
                    equipo_str,
                    s.resumen_cv,
                ),
            )

            if s.estado == "Pendiente":
                self.tree_pendientes.insert(
                    "",
                    tk.END,
                    values=(s.identificador, fecha_str, s.reportero_dni, nombre_rep, equipo_str, s.resumen_cv),
                )
            elif s.estado == "Aprobada":
                cat_obj = self.servicio.obtener_categoria(s.categoria_asignada or 0)
                cat_desc = cat_obj.nombre if cat_obj else cat_str
                self.tree_aprobadas.insert(
                    "",
                    tk.END,
                    values=(s.identificador, fecha_str, s.reportero_dni, nombre_rep, cat_desc),
                )

        # 3. Reporteros en bolsa
        self.tree_bolsa.delete(*self.tree_bolsa.get_children())
        self._mapa_rep_bolsa_combo.clear()
        for r in self.servicio.listar_reporteros_en_bolsa():
            cat_obj = self.servicio.obtener_categoria(r.categoria_nivel or 0)
            cat_nombre = cat_obj.nombre if cat_obj else f"Nivel {r.categoria_nivel}"
            precio_str = f"{cat_obj.precio_por_hoja:.2f}" if cat_obj else "—"
            self.tree_bolsa.insert(
                "",
                tk.END,
                values=(r.dni, r.nombre_completo, r.telefono, r.ciudad, cat_nombre, precio_str),
            )
            etiqueta = f"{r.dni} — {r.nombre_completo} (Nivel {r.categoria_nivel})"
            self._mapa_rep_bolsa_combo[etiqueta] = r.dni

        bolsa_labels = list(self._mapa_rep_bolsa_combo.keys())
        self.cmb_promo_rep["values"] = bolsa_labels
        self.cmb_rpt_rep["values"] = bolsa_labels

        # 4. Reportajes
        self.tree_reportajes.delete(*self.tree_reportajes.get_children())
        self._mapa_reportaje_combo.clear()
        for rpt in self.servicio.reportajes:
            rep = self.servicio.obtener_reportero(rpt.reportero_dni)
            nombre_rep = rep.nombre_completo if rep else rpt.reportero_dni
            cat_str = f"Nivel {rep.categoria_nivel}" if rep and rep.categoria_nivel else "—"
            try:
                pago_base = f"{self.servicio.calcular_pago_reportero_reportaje(rpt.identificador):.2f}"
            except ValueError:
                pago_base = "—"
            self.tree_reportajes.insert(
                "",
                tk.END,
                values=(
                    rpt.identificador,
                    rpt.reportero_dni,
                    nombre_rep,
                    cat_str,
                    rpt.num_fotos,
                    pago_base,
                    rpt.descripcion,
                ),
            )
            etiqueta_rpt = f"RPT-{rpt.identificador} | {rpt.descripcion[:28]} ({rpt.num_fotos} fotos)"
            self._mapa_reportaje_combo[etiqueta_rpt] = rpt.identificador

        self.cmb_alb_reportaje["values"] = list(self._mapa_reportaje_combo.keys())

        # 5. Editoriales
        self.tree_editoriales.delete(*self.tree_editoriales.get_children())
        self._mapa_editorial_combo.clear()
        for edi in self.servicio.editoriales:
            self.tree_editoriales.insert(
                "",
                tk.END,
                values=(edi.identificador, edi.nombre, edi.cif, edi.direccion),
            )
            etiqueta_edi = f"EDI-{edi.identificador} | {edi.nombre} ({edi.cif})"
            self._mapa_editorial_combo[etiqueta_edi] = edi.identificador

        self.cmb_alb_editorial["values"] = list(self._mapa_editorial_combo.keys())

        # 6. Albaranes
        self.tree_albaranes.delete(*self.tree_albaranes.get_children())
        for alb in self.servicio.albaranes:
            rpt = self.servicio.obtener_reportaje(alb.reportaje_id)
            edi = self.servicio.obtener_editorial(alb.editorial_id)
            rpt_desc = f"RPT-{alb.reportaje_id} ({rpt.descripcion[:20]}...)" if rpt else f"RPT-{alb.reportaje_id}"
            edi_desc = edi.nombre if edi else f"EDI-{alb.editorial_id}"
            self.tree_albaranes.insert(
                "",
                tk.END,
                values=(
                    alb.identificador,
                    alb.fecha_creacion.strftime(FORMATO_FECHA),
                    rpt_desc,
                    edi_desc,
                    f"{alb.precio_editorial:.2f}",
                    f"{alb.pago_reportero:.2f}",
                    f"{alb.margen_agencia:.2f}",
                ),
            )

        self._actualizar_pago_reportero_preview()


def main() -> None:
    try:
        repositorio = RepositorioSIGER("datos_siger.json")
        servicio = ServicioSIGER(repositorio)
        app = InterfazSIGER(servicio)
        app.mainloop()
    except RuntimeError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error crítico", f"No se pudo iniciar SIGER:\n{exc}")


if __name__ == "__main__":
    main()