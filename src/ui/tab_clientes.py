import tkinter as tk
from tkinter import ttk

from src.services import cliente_service
from src.ui.componentes import confirmar, crear_tabla, id_seleccionado, llenar_tabla, mostrar_error, mostrar_info


class TabClientes(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.filas = {}

        form = ttk.LabelFrame(self, text="Datos del cliente", padding=10)
        form.pack(fill="x")
        self.var_nombre = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_telefono = tk.StringVar()
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_nombre, width=35).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Correo:").grid(row=0, column=2, sticky="w", padx=(15, 0))
        ttk.Entry(form, textvariable=self.var_correo, width=35).grid(row=0, column=3, sticky="w", padx=5)
        ttk.Label(form, text="Teléfono:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_telefono, width=20).grid(row=1, column=1, sticky="w", padx=5)

        botones = ttk.Frame(form)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Agregar", command=self.agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Actualizar seleccionado", command=self.actualizar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar seleccionado", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        marco, self.tabla = crear_tabla(self, [("id", "ID", 50), ("nombre", "Nombre", 250),
                                               ("correo", "Correo", 280), ("telefono", "Teléfono", 150)])
        marco.pack(fill="both", expand=True, pady=(10, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)
        self.refrescar()

    def refrescar(self):
        filas = cliente_service.listar_clientes()
        self.filas = {f["id"]: f for f in filas}
        llenar_tabla(self.tabla, filas, ["id", "nombre", "correo", "telefono"])

    def al_seleccionar(self, _evento=None):
        fila = self.filas.get(id_seleccionado(self.tabla))
        if fila:
            self.var_nombre.set(fila["nombre"])
            self.var_correo.set(fila["correo"])
            self.var_telefono.set(fila["telefono"])

    def limpiar(self):
        self.tabla.selection_remove(self.tabla.selection())
        for variable in (self.var_nombre, self.var_correo, self.var_telefono):
            variable.set("")

    def agregar(self):
        try:
            cliente_service.crear_cliente(self.var_nombre.get(), self.var_correo.get(), self.var_telefono.get())
            self.limpiar()
            self.refrescar()
            mostrar_info("Cliente agregado.")
        except Exception as error:
            mostrar_error(error)

    def actualizar(self):
        cliente_id = id_seleccionado(self.tabla)
        if cliente_id is None:
            return mostrar_error(Exception("Seleccione un cliente de la tabla."))
        try:
            cliente_service.actualizar_cliente(cliente_id, self.var_nombre.get(),
                                               self.var_correo.get(), self.var_telefono.get())
            self.refrescar()
            mostrar_info("Cliente actualizado.")
        except Exception as error:
            mostrar_error(error)

    def eliminar(self):
        cliente_id = id_seleccionado(self.tabla)
        if cliente_id is None:
            return mostrar_error(Exception("Seleccione un cliente de la tabla."))
        if not confirmar("¿Eliminar el cliente seleccionado?"):
            return
        try:
            cliente_service.eliminar_cliente(cliente_id)
            self.limpiar()
            self.refrescar()
            mostrar_info("Cliente eliminado.")
        except Exception as error:
            mostrar_error(error)
