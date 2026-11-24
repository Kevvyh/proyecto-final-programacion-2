from datetime import date, timedelta

from src.database.conexion import crear_tablas
from src.services import arriendo_service, categoria_service, cliente_service, equipo_service


def main():
    crear_tablas()
    if categoria_service.listar_categorias():
        print("La base de datos ya tiene datos; no se cargó nada.")
        return

    acuaticos = categoria_service.crear_categoria("Acuáticos", "Equipos para agua")["id"]
    montana = categoria_service.crear_categoria("Montaña", "Trekking y camping")["id"]
    ciclismo = categoria_service.crear_categoria("Ciclismo", "Bicicletas y accesorios")["id"]

    kayak = equipo_service.crear_equipo("Kayak doble", acuaticos, 15000, 5, "ACUATICO")["id"]
    tabla = equipo_service.crear_equipo("Tabla de paddle surf", acuaticos, 12000, 4, "ACUATICO")["id"]
    carpa = equipo_service.crear_equipo("Carpa 4 personas", montana, 9000, 6, "MONTANA")["id"]
    mochila = equipo_service.crear_equipo("Mochila 60L", montana, 5000, 8, "MONTANA")["id"]
    bici = equipo_service.crear_equipo("Bicicleta MTB", ciclismo, 10000, 7, "CICLISMO")["id"]
    equipo_service.crear_equipo("Casco", ciclismo, 2000, 10, "GENERAL")

    ana = cliente_service.crear_cliente("Ana Pérez", "ana@correo.cl", "+56 9 1111 2222")["id"]
    luis = cliente_service.crear_cliente("Luis Soto", "luis@correo.cl", "+56 9 3333 4444")["id"]
    marta = cliente_service.crear_cliente("Marta Rojas", "marta@correo.cl")["id"]

    hoy = date.today()
    en = lambda dias: hoy + timedelta(days=dias)
    a1 = arriendo_service.registrar_arriendo(kayak, ana, hoy, en(3), 2)["id"]
    arriendo_service.registrar_arriendo(kayak, luis, hoy, en(2), 1)
    arriendo_service.registrar_arriendo(carpa, marta, hoy, en(5), 2)
    arriendo_service.registrar_arriendo(bici, ana, hoy, en(1), 3)
    arriendo_service.registrar_arriendo(bici, luis, hoy, en(2), 1)
    arriendo_service.registrar_arriendo(mochila, marta, hoy, en(4), 2)
    arriendo_service.registrar_arriendo(tabla, luis, hoy, en(1), 1)
    arriendo_service.devolver_arriendo(a1)
    print("Datos de ejemplo cargados.")


if __name__ == "__main__":
    main()
