from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.conexion import engine, confirmar_cambios
from src.database.modelos import Arriendo, Categoria, Equipo
from src.factory.equipo_factory import obtener_creador
from src.utils.validaciones import ErrorNegocio, a_decimal, a_entero, texto_obligatorio

def validar_datos(session, nombre, categoria_id, precio_diario, stock_total):
    nombre = texto_obligatorio(nombre, "Nombre")
    if categoria_id in (None, ""):
        raise ErrorNegocio("Debe seleccionar una categoria")
    categoria_id = a_entero(categoria_id, "Categoria")
    if session.get(Categoria, categoria_id) is None:
        raise ErrorNegocio("La categoria seleccionada no existe")
    precio = a_decimal(precio_diario, "Precio diario")
    if precio <= 0:
        raise ErrorNegocio("El precio diario debe ser mayor que 0")
    total = a_entero(stock_total, "Stock total")
    if total < 0:
        raise ErrorNegocio("El stock total no puede ser negativo")
    return nombre, categoria_id, precio, total

def listar_equipos(solo_disponibles=False):
    with Session(engine) as session:
        consulta = select(Equipo).order_by(Equipo.nombre)
        if solo_disponibles:
            consulta = consulta.where(Equipo.stock_disponible > 0)
        return [e.a_dict() for e in session.scalars(consulta)]

def crear_equipo(nombre, categoria_id, precio_diario, stock_total, tipo="GENERAL"):
    with Session(engine) as session:
        nombre, categoria_id, precio, total, total = validar_datos(session, nombre, categoria_id, precio_diario, stock_total)
        equipo = obtener_creador(tipo).crear_modelo(nombre, categoria_id, precio, total)
        session.add(equipo)
        confirmar_cambios(session)
        return equipo.a_dict()

def actualizar_equipo(equipo_id, nombre, categoria_id, precio_diario, stock_total, tipo="GENERAL"):
    with Session(engine) as session:
        equipo = session.get(Equipo, equipo_id)
        if equipo is None:
            raise ErrorNegocio("El equipo seleccionado ya no existe")
        nombre, categoria_id, precio, total = validar_datos(session, nombre, categoria_id, precio_diario, stock_total)

        #unidades de arriendo activos, se conservan al cambiar el stocktotal
        en_arriendo = equipo.stock_total - equipo.stock_disponible
        if total < en_arriendo:
            raise ErrorNegocio(
                f"No se puede bajar el stock total a {total}, hay {en_arriendo} unidad(es) arrendada(s) activas"
            )
        equipo.nombre = nombre
        equipo.categoria_id = categoria_id
        equipo.precio_diario = precio
        equipo.stock_total = total
        equipo.stock_disponible = total - en_arriendo
        equipo.tipo = obtener_creador(tipo).crear_producto().tipo
        confirmar_cambios(session)
        return equipo.a_dict()

def eliminar_equipo(equipo_id):
    with Session(engine) as session:
        equipo = session.get(Equipo, equipo_id)
        if equipo is None:
            raise ErrorNegocio("El equipo seleccionado ya no existe")
        cantidad = session.scalar(select(func.count(Arriendo.id)).where(Arriendo.equipo_id == equipo_id))
        if cantidad > 0:
            raise ErrorNegocio(
                f"No se puede eliminar {equipo.nombre}, tiene {cantidad} arriendo(s) registrado(s)"
                "(activos o en el historial)"
            )
        session.delete(equipo)
        confirmar_cambios(session)
        