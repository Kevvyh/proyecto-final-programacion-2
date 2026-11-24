from src.database.conexion import crear_tablas
from src.ui.app import VentanaPrincipal


def main():
    crear_tablas()
    VentanaPrincipal().mainloop()


if __name__ == "__main__":
    main()