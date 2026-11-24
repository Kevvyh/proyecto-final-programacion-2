from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.graficos import graficos


class TabGraficos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=10)
        ttk.Button(self, text="Actualizar gráficos", command=self.refrescar).pack(anchor="w")

        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True, pady=(8, 0))
        contenedor.columnconfigure((0, 1), weight=1)
        contenedor.rowconfigure(0, weight=1)

        self.fig1 = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=contenedor)
        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.fig2 = Figure(figsize=(5, 4), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=contenedor)
        self.canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.refrescar()

    def refrescar(self):
        graficos.dibujar_arriendos_por_categoria(self.ax1)
        graficos.dibujar_equipos_mas_arrendados(self.ax2)
        self.canvas1.draw()
        self.canvas2.draw()
