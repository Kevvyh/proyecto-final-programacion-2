import tkinter as tk
from tkinter import ttk

from src.services import categoria_service
from src.ui.componentes import confirmar, crear_tabla, id_seleccionado, llenar_tabla, mostrar_error, mostrar_info


class TabCategorias(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.filas = {}

        form = ttk.LabelFrame(self, text="Datos de la categoría", padding=10)
        form.pack(fill="x")
        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_nombre, width=35).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Descripción:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_descripcion, width=70).grid(row=1, column=1, sticky="w", padx=5)

        botones = ttk.Frame(form)
        botones.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Agregar", command=self.agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Actualizar seleccionada", command=self.actualizar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar seleccionada", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        marco, self.tabla = crear_tabla(self, [("id", "ID", 60), ("nombre", "Nombre", 220), ("descripcion", "Descripción", 460)])
        marco.pack(fill="both", expand=True, pady=(10, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        self.refrescar()

    def refrescar(self):
        filas = categoria_service.listar_categorias()
        self.filas = {f["id"]: f for f in filas}
        llenar_tabla(self.tabla, filas, ["id", "nombre", "descripcion"])

    def al_seleccionar(self, _evento=None):
        fila = self.filas.get(id_seleccionado(self.tabla))
        if fila:
            self.var_nombre.set(fila["nombre"])
            self.var_descripcion.set(fila["descripcion"])

    def limpiar(self):
        self.tabla.selection_remove(self.tabla.selection())
        self.var_nombre.set("")
        self.var_descripcion.set("")

    def agregar(self):
        try:
            categoria_service.crear_categoria(self.var_nombre.get(), self.var_descripcion.get())
            self.limpiar()
            self.refrescar()
            mostrar_info("Categoria agregada.")
        except Exception as error:
            mostrar_error(error)

    def actualizar(self):
        categoria_id = id_seleccionado(self.tabla)
        if categoria_id is None:
            return mostrar_error(Exception("Seleccione una categoria de la tabla."))
        try:
            categoria_service.actualizar_categoria(categoria_id, self.var_nombre.get(), self.var_descripcion.get())
            self.refrescar()
            mostrar_info("Categoria actualizada.")
        except Exception as error:
            mostrar_error(error)

    def eliminar(self):
        categoria_id = id_seleccionado(self.tabla)
        if categoria_id is None:
            return mostrar_error(Exception("Seleccione una categoria de la tabla."))
        if not confirmar("¿Eliminar la categoria seleccionada?"):
            return
        try:
            categoria_service.eliminar_categoria(categoria_id)
            self.limpiar()
            self.refrescar()
            mostrar_info("Categoria eliminada.")
        except Exception as error:
            mostrar_error(error)
