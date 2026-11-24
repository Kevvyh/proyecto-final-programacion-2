from tkinter import messagebox, ttk

from src.utils.validaciones import ErrorNegocio


def crear_tabla(padre, columnas, altura=10):
    marco = ttk.Frame(padre)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                         height=altura, selectmode="browse")
    for clave, titulo, ancho in columnas:
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, anchor="center")
    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return marco, tabla


def llenar_tabla(tabla, filas, claves):
    tabla.delete(*tabla.get_children())
    for fila in filas:
        valores = ["-" if fila[c] is None else fila[c] for c in claves]
        tabla.insert("", "end", iid=str(fila["id"]), values=valores)


def id_seleccionado(tabla):
    seleccion = tabla.selection()
    return int(seleccion[0]) if seleccion else None


def mostrar_error(error):
    if isinstance(error, ErrorNegocio):
        messagebox.showwarning("No se pudo completar", str(error))
    else:
        messagebox.showerror("Error inesperado", f"Ocurrió un error inesperado:\n{error}")


def mostrar_info(mensaje):
    messagebox.showinfo("Listo", mensaje)


def confirmar(mensaje):
    return messagebox.askyesno("Confirmar", mensaje)


def formato_pesos(valor):
    return "$" + f"{valor:,.0f}".replace(",", ".")
