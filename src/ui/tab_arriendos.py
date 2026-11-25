import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from src.services import arriendo_service, cliente_service, consulta_service, equipo_service
from src.ui.componentes import (confirmar, crear_tabla, formato_pesos, id_seleccionado, llenar_tabla,
                            mostrar_error, mostrar_info)
from src.utils.validaciones import ErrorNegocio


class TabArriendos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.mapa_equipos = {}    # texto del combobox -> id
        self.mapa_clientes = {}

        form = ttk.LabelFrame(self, text="Nuevo arriendo", padding=10)
        form.pack(fill="x")
        self.var_equipo = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_inicio = tk.StringVar(value=date.today().isoformat())
        self.var_fin = tk.StringVar(value=(date.today() + timedelta(days=7)).isoformat())
        self.var_cantidad = tk.StringVar(value="1")
        self.var_filtro = tk.StringVar(value="Activos")

        ttk.Label(form, text="Equipo:").grid(row=0, column=0, sticky="w", pady=3)
        self.combo_equipo = ttk.Combobox(form, textvariable=self.var_equipo, state="readonly", width=42)
        self.combo_equipo.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Cliente:").grid(row=0, column=2, sticky="w", padx=(15, 0))
        self.combo_cliente = ttk.Combobox(form, textvariable=self.var_cliente, state="readonly", width=38)
        self.combo_cliente.grid(row=0, column=3, sticky="w", padx=5)

        ttk.Label(form, text="Fecha inicio (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_inicio, width=14).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Término previsto:").grid(row=1, column=2, sticky="w", padx=(15, 0))
        ttk.Entry(form, textvariable=self.var_fin, width=14).grid(row=1, column=3, sticky="w", padx=5)
        ttk.Label(form, text="Cantidad:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.var_cantidad, width=8).grid(row=2, column=1, sticky="w", padx=5)

        botones = ttk.Frame(form)
        botones.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Registrar arriendo", command=self.registrar).pack(side="left", padx=3)
        ttk.Button(botones, text="Devolver arriendo seleccionado", command=self.devolver).pack(side="left", padx=3)

        filtro = ttk.Frame(self)
        filtro.pack(fill="x", pady=(10, 0))
        ttk.Label(filtro, text="Mostrar:").pack(side="left")
        combo_filtro = ttk.Combobox(filtro, textvariable=self.var_filtro, values=["Activos", "Todos"],
                                    state="readonly", width=10)
        combo_filtro.pack(side="left", padx=5)
        combo_filtro.bind("<<ComboboxSelected>>", lambda _e: self.refrescar_tabla())

        columnas = [("id", "N°", 45), ("equipo", "Equipo", 170), ("cliente", "Cliente", 150),
                    ("cantidad", "Cant.", 50), ("fecha_inicio", "Inicio", 90),
                    ("fecha_fin_prevista", "Término prev.", 95), ("fecha_devolucion", "Devuelto", 90),
                    ("estado", "Estado", 80), ("costo", "Costo total", 90)]
        marco, self.tabla = crear_tabla(self, columnas)
        marco.pack(fill="both", expand=True, pady=(5, 0))
        self.refrescar()

    def refrescar(self):
        self.mapa_equipos = {}
        etiquetas = []
        for e in equipo_service.listar_equipos():
            etiqueta = f"{e['id']} - {e['nombre']} (disp: {e['stock_disponible']})"
            self.mapa_equipos[etiqueta] = e["id"]
            etiquetas.append(etiqueta)
        self.combo_equipo["values"] = etiquetas
        if self.var_equipo.get() not in self.mapa_equipos:
            self.var_equipo.set("")

        self.mapa_clientes = {}
        etiquetas = []
        for c in cliente_service.listar_clientes():
            etiqueta = f"{c['id']} - {c['nombre']} ({c['correo']})"
            self.mapa_clientes[etiqueta] = c["id"]
            etiquetas.append(etiqueta)
        self.combo_cliente["values"] = etiquetas
        if self.var_cliente.get() not in self.mapa_clientes:
            self.var_cliente.set("")
        self.refrescar_tabla()

    def refrescar_tabla(self):
        if self.var_filtro.get() == "Activos":
            arriendos = consulta_service.arriendos_activos()
        else:
            arriendos = consulta_service.historial_arriendos()
        filas = [dict(a, costo=formato_pesos(a["costo_total"])) for a in arriendos]
        llenar_tabla(self.tabla, filas, ["id", "equipo", "cliente", "cantidad", "fecha_inicio",
                                         "fecha_fin_prevista", "fecha_devolucion", "estado", "costo"])

    def registrar(self):
        try:
            equipo_id = self.mapa_equipos.get(self.var_equipo.get())
            cliente_id = self.mapa_clientes.get(self.var_cliente.get())
            if equipo_id is None:
                raise ErrorNegocio("Seleccione un equipo.")
            if cliente_id is None:
                raise ErrorNegocio("Seleccione un cliente.")
            arriendo = arriendo_service.registrar_arriendo(equipo_id, cliente_id, self.var_inicio.get(),
                                                           self.var_fin.get(), self.var_cantidad.get())
            self.var_cantidad.set("1")
            self.refrescar()
            mostrar_info(f"Arriendo N° {arriendo['id']} registrado.\nCosto total: {formato_pesos(arriendo['costo_total'])}")
        except Exception as error:
            mostrar_error(error)

    def devolver(self):
        arriendo_id = id_seleccionado(self.tabla)
        if arriendo_id is None:
            return mostrar_error(ErrorNegocio("Seleccione un arriendo de la tabla."))
        if not confirmar(f"¿Registrar la devolución del arriendo N° {arriendo_id}?"):
            return
        try:
            arriendo_service.devolver_arriendo(arriendo_id)
            self.refrescar()
            mostrar_info(f"Arriendo N° {arriendo_id} devuelto. El stock fue restituido.")
        except Exception as error:
            mostrar_error(error)
            self.refrescar()
