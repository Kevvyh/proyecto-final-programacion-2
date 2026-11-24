import tkinter as tk
from tkinter import ttk

from src.services import cliente_service, consulta_service
from src.ui.componentes import crear_tabla, formato_pesos, llenar_tabla


class TabConsultas(ttk.Frame):
    COLUMNAS_ARRIENDO = [("id", "N°", 45), ("equipo", "Equipo", 170), ("cliente", "Cliente", 150),
                         ("cantidad", "Cant.", 50), ("fecha_inicio", "Inicio", 90),
                         ("fecha_fin_prevista", "Término prev.", 95), ("fecha_devolucion", "Devuelto", 90),
                         ("estado", "Estado", 80), ("costo", "Costo total", 90)]
    CLAVES_ARRIENDO = [c[0] for c in COLUMNAS_ARRIENDO]

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.mapa_clientes = {"Todos": None}
        interno = ttk.Notebook(self)
        interno.pack(fill="both", expand=True)

        pag1 = ttk.Frame(interno, padding=8)
        interno.add(pag1, text="Equipos disponibles")
        columnas = [("id", "ID", 45), ("nombre", "Nombre", 200), ("categoria", "Categoría", 140),
                    ("tipo", "Tipo", 90), ("precio", "Precio diario", 100), ("stock_disponible", "Disponibles", 90)]
        marco, self.tabla_equipos = crear_tabla(pag1, columnas)
        marco.pack(fill="both", expand=True)

        pag2 = ttk.Frame(interno, padding=8)
        interno.add(pag2, text="Arriendos activos")
        marco, self.tabla_activos = crear_tabla(pag2, self.COLUMNAS_ARRIENDO)
        marco.pack(fill="both", expand=True)

        pag3 = ttk.Frame(interno, padding=8)
        interno.add(pag3, text="Historial de arriendos")
        barra = ttk.Frame(pag3)
        barra.pack(fill="x", pady=(0, 6))
        ttk.Label(barra, text="Cliente:").pack(side="left")
        self.var_cliente = tk.StringVar(value="Todos")
        self.combo_cliente = ttk.Combobox(barra, textvariable=self.var_cliente, state="readonly", width=40)
        self.combo_cliente.pack(side="left", padx=5)
        self.combo_cliente.bind("<<ComboboxSelected>>", lambda _e: self.refrescar_historial())
        marco, self.tabla_historial = crear_tabla(pag3, self.COLUMNAS_ARRIENDO)
        marco.pack(fill="both", expand=True)

        self.refrescar()

    def _con_costo(self, arriendos):
        return [dict(a, costo=formato_pesos(a["costo_total"])) for a in arriendos]

    def refrescar(self):
        equipos = [dict(e, precio=formato_pesos(e["precio_diario"])) for e in consulta_service.equipos_disponibles()]
        llenar_tabla(self.tabla_equipos, equipos, ["id", "nombre", "categoria", "tipo", "precio", "stock_disponible"])
        llenar_tabla(self.tabla_activos, self._con_costo(consulta_service.arriendos_activos()), self.CLAVES_ARRIENDO)

        self.mapa_clientes = {"Todos": None}
        for c in cliente_service.listar_clientes():
            self.mapa_clientes[f"{c['id']} - {c['nombre']}"] = c["id"]
        self.combo_cliente["values"] = list(self.mapa_clientes)
        if self.var_cliente.get() not in self.mapa_clientes:
            self.var_cliente.set("Todos")
        self.refrescar_historial()

    def refrescar_historial(self):
        cliente_id = self.mapa_clientes.get(self.var_cliente.get())
        historial = consulta_service.historial_arriendos(cliente_id)
        llenar_tabla(self.tabla_historial, self._con_costo(historial), self.CLAVES_ARRIENDO)
