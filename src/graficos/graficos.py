from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from src.services import consulta_service


def _sin_datos(ax, titulo):
    ax.set_title(titulo)
    ax.text(0.5, 0.5, "Sin datos todavía", ha="center", va="center", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])


def dibujar_arriendos_por_categoria(ax):
    ax.clear()
    datos = consulta_service.arriendos_por_categoria()
    titulo = "Cantidad de arriendos por categoría"
    if not datos or sum(cantidad for _, cantidad in datos) == 0:
        _sin_datos(ax, titulo)
    else:
        nombres = [nombre for nombre, _ in datos]
        cantidades = [cantidad for _, cantidad in datos]
        barras = ax.bar(nombres, cantidades, color="#2a7fba")
        ax.bar_label(barras)
        ax.set_title(titulo)
        ax.set_xlabel("Categoría")
        ax.set_ylabel("N° de arriendos")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis="x", labelrotation=25)
    ax.figure.tight_layout()


def dibujar_equipos_mas_arrendados(ax, limite=5):
    ax.clear()
    datos = consulta_service.equipos_mas_arrendados(limite)
    titulo = f"Equipos con más arriendos (top {limite})"
    if not datos:
        _sin_datos(ax, titulo)
    else:
        nombres = [nombre for nombre, _ in datos]
        cantidades = [cantidad for _, cantidad in datos]
        barras = ax.barh(nombres, cantidades, color="#e07b39")
        ax.bar_label(barras)
        ax.invert_yaxis()  
        ax.set_title(titulo)
        ax.set_xlabel("N° de arriendos")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.figure.tight_layout()


def guardar_graficos_png(carpeta="capturas"):
    Path(carpeta).mkdir(exist_ok=True)
    rutas = []
    for nombre, funcion in (
        ("grafico_arriendos_por_categoria.png", dibujar_arriendos_por_categoria),
        ("grafico_equipos_mas_arrendados.png", dibujar_equipos_mas_arrendados),
    ):
        figura = Figure(figsize=(6, 4), dpi=110)
        funcion(figura.add_subplot(111))
        ruta = Path(carpeta) / nombre
        figura.savefig(ruta)
        rutas.append(str(ruta))
    return rutas
