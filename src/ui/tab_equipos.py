import tkinter as tk
from tkinter import ttk

from src.factory.equipo_factory import TIPOS_EQUIPO, producto_de
from src.services import categoria_service, equipo_service
from src.ui.componentes import (confirmar, crear_tabla, formato_pesos, id_seleccionado, llenar_tabla,
                            mostrar_error, mostrar_info)


class TabEquipos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.filas = {}
        self.mapa_categorias = {}  # nombre de categoría -> id

        form = ttk.LabelFrame(self, text="Datos del equipo", padding=10)
        form.pack(fill="x")
        self.var_nombre = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_tipo = tk.StringVar(value="GENERAL")
        self.var_precio = tk.StringVar()
        self.var_stock = tk.StringVar()

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_nombre, width=30).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Categoría:").grid(row=0, column=2, sticky="w", padx=(15, 0))
        self.combo_categoria = ttk.Combobox(form, textvariable=self.var_categoria, state="readonly", width=25)
        self.combo_categoria.grid(row=0, column=3, sticky="w", padx=5)

        ttk.Label(form, text="Precio diario ($):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_precio, width=15).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Stock total:").grid(row=1, column=2, sticky="w", padx=(15, 0))
        ttk.Entry(form, textvariable=self.var_stock, width=10).grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(form, text="Tipo (Factory):").grid(row=2, column=0, sticky="w", pady=3)
        combo_tipo = ttk.Combobox(form, textvariable=self.var_tipo, values=TIPOS_EQUIPO, state="readonly", width=15)
        combo_tipo.grid(row=2, column=1, sticky="w", padx=5)
        combo_tipo.bind("<<ComboboxSelected>>", self.mostrar_descripcion_tipo)
        self.lbl_tipo = ttk.Label(form, text="", foreground="#555555")
        self.lbl_tipo.grid(row=2, column=2, columnspan=2, sticky="w", padx=(15, 0))

        botones = ttk.Frame(form)
        botones.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Agregar", command=self.agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Actualizar seleccionado", command=self.actualizar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar seleccionado", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        columnas = [("id", "ID", 45), ("nombre", "Nombre", 190), ("categoria", "Categoría", 130),
                    ("tipo", "Tipo", 90), ("precio", "Precio diario", 100),
                    ("stock_total", "Stock total", 80), ("stock_disponible", "Disponible", 80)]
        marco, self.tabla = crear_tabla(self, columnas)
        marco.pack(fill="both", expand=True, pady=(10, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        self.mostrar_descripcion_tipo()
        self.refrescar()

    def mostrar_descripcion_tipo(self, _evento=None):
        try:
            self.lbl_tipo.config(text=producto_de(self.var_tipo.get()).describir())
        except Exception:
            self.lbl_tipo.config(text="")

    def refrescar(self):
        categorias = categoria_service.listar_categorias()
        self.mapa_categorias = {c["nombre"]: c["id"] for c in categorias}
        self.combo_categoria["values"] = list(self.mapa_categorias)
        if self.var_categoria.get() not in self.mapa_categorias:
            self.var_categoria.set("")

        equipos = equipo_service.listar_equipos()
        self.filas = {e["id"]: e for e in equipos}
        filas_tabla = [dict(e, precio=formato_pesos(e["precio_diario"])) for e in equipos]
        llenar_tabla(self.tabla, filas_tabla,
                     ["id", "nombre", "categoria", "tipo", "precio", "stock_total", "stock_disponible"])

    def al_seleccionar(self, _evento=None):
        fila = self.filas.get(id_seleccionado(self.tabla))
        if fila:
            self.var_nombre.set(fila["nombre"])
            self.var_categoria.set(fila["categoria"])
            self.var_tipo.set(fila["tipo"])
            self.var_precio.set(f"{fila['precio_diario']:g}")
            self.var_stock.set(str(fila["stock_total"]))
            self.mostrar_descripcion_tipo()

    def limpiar(self):
        self.tabla.selection_remove(self.tabla.selection())
        for variable in (self.var_nombre, self.var_categoria, self.var_precio, self.var_stock):
            variable.set("")
        self.var_tipo.set("GENERAL")
        self.mostrar_descripcion_tipo()

    def _datos_formulario(self):
        return (self.var_nombre.get(), self.mapa_categorias.get(self.var_categoria.get()),
                self.var_precio.get(), self.var_stock.get(), self.var_tipo.get())

    def agregar(self):
        try:
            equipo_service.crear_equipo(*self._datos_formulario())
            self.limpiar()
            self.refrescar()
            mostrar_info("Equipo agregado.")
        except Exception as error:
            mostrar_error(error)

    def actualizar(self):
        equipo_id = id_seleccionado(self.tabla)
        if equipo_id is None:
            return mostrar_error(Exception("Seleccione un equipo de la tabla."))
        try:
            equipo_service.actualizar_equipo(equipo_id, *self._datos_formulario())
            self.refrescar()
            mostrar_info("Equipo actualizado.")
        except Exception as error:
            mostrar_error(error)

    def eliminar(self):
        equipo_id = id_seleccionado(self.tabla)
        if equipo_id is None:
            return mostrar_error(Exception("Seleccione un equipo de la tabla."))
        if not confirmar("¿Eliminar el equipo seleccionado?"):
            return
        try:
            equipo_service.eliminar_equipo(equipo_id)
            self.limpiar()
            self.refrescar()
            mostrar_info("Equipo eliminado.")
        except Exception as error:
            mostrar_error(error)
