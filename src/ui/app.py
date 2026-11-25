import tkinter as tk
from tkinter import ttk

from src.ui.tab_arriendos import TabArriendos
from src.ui.tab_categorias import TabCategorias
from src.ui.tab_clientes import TabClientes
from src.ui.tab_consultas import TabConsultas
from src.ui.tab_equipos import TabEquipos
from src.ui.tab_graficos import TabGraficos


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arriendo de Equipamiento Deportivo")
        self.geometry("1050x650")
        self.minsize(900, 560)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)
        for titulo, clase in (("Categorías", TabCategorias), ("Equipos", TabEquipos),
                              ("Clientes", TabClientes), ("Arriendos", TabArriendos),
                              ("Consultas", TabConsultas), ("Gráficos", TabGraficos)):
            self.notebook.add(clase(self.notebook), text=titulo)

        # Al cambiar de pestaña se recargan sus datos (así siempre muestran lo último de la BD)
        self.notebook.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

    def al_cambiar_pestana(self, _evento=None):
        pestana = self.nametowidget(self.notebook.select())
        pestana.refrescar()
