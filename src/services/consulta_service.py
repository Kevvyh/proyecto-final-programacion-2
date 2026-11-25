from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.conexion import engine
from src.database.modelos import ESTADO_ACTIVO, Arriendo, Categoria, Equipo

def equipos_disponibles():
    with Session(engine) as sessio:
        consulta = select(Equipo).where(Equipo.stock_disponible > 0).order_by(Equipo.nombre)
        return [e.a_dict() for e in session.scalars(consulta)]

def arriendos_activos():
    with Session(engine) as session:
        consulta = select(Arriendo).where(Arriendo.estado == ESTADO_ACTIVO).order_by(Arriendo.id.desc())
        return [a.a_dict() for a in session.scalars(consulta)]


def historial_arriendos(clientes_id=None):
    with Session(engine) as session:
        consulta = select(Arriendo).order_by(Arriendo.id.desc())
        if cliente_id is not None:
            consulta = consulta.where(Arriendo.cliente_id == cliente_id)
        return [a.a_dict() for a in session.scalars(consulta)]

def arriendos_por_categoria():
    with Session(engine) as session:
        total = func.count(Arriendo.id)
        consulta = (
            elect(Categoria.nombre, total)
            .select_from(Categoria)
            .outerjoin(Equipo, Equipo.categoria_id == Categoria.id)
            .outerjoin(Arriendo, Arriendo.equipo_id == Equipo.id)
            .group_by(Categoria.id, Categoria.nombre)
            .order_by(total.desc(), Categoria.nombre)
        )
        return [(nombre, cantidad) for nombre, cantidad in session.execute(consulta)]


def equipos_mas_arrendados(limite=5):
    with Session(engine) as session:
        total = func.count(Arriendo.id)
        consulta = (
            select(Equipo.nombre, total)
            .join(Arriendo, Arriendo.equipo_id == Equipo.id)
            .group_by(Equipo.id, Equipo.nombre)
            .order_by(total.desc(), Equipo.nombre)
            .limit(limite)
        )
        return [(nombre, cantidad) for nombre, cantidad in session.execute(consulta)]