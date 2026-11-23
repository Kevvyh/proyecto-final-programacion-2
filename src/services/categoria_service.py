from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.conexion import engine, confirmar_cambios
from src.database.modelos import Categoria, Equipo
from src.utils.validaciones import ErrorNegocio, texto_obligatorio

def existe_nombre(session, nombre, ignorar_id=None):
    consulta = select(Categoria).where(func.lower(Categoria.nombre) == nombre.lower())
    if ignorar_id is not None:
        consulta = consulta.where(Categoria.id != ignorar_id)
    return session.scalars(consulta).first() is not None

def listar_categorias():
    with Session(engine) as session:
        categorias = session.scalars(select(Categoria).order_by(Categoria.nombre))
        return [c.a_dict() for c in categorias]

def actualizar_categoria(categoria_id, nombre, descripcion=""):
    nombre = texto_obligatorio(nombre, "Nombre")
    with Session(engine) as session:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None:
            raise ErrorNegocio("La categoria seleccionada no existe")
        if existe_nombre(session, nombre, ignorar_id=categoria_id):
            raise ErrorNegocio(f"Ya existe otra categoria llamada: {nombre}.")
        categoria.nombre = nombre
        categoria.descripcion = (descripcion or "").strip()
        confirmar_cambios(session)
        return categoria.a_dict()

def eliminar_categoria(categoria_id):
    with Session(engine) as session:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None:
            raise ErrorNegocio("La categoria seleccionada ya no existe")
        cantidad = session.scalar(select(func.count(Equipo.id)).where(Equipo.categoria_id == categoria_id))
        if cantidad > 0:
            raise ErrorNegocio(
                f"No se puede eliminar {categoria.nombre}: tiene {cantidad} equipo(s) asociado(s)."
                "Elimine o cambie de categoria esos equipos primero"
            )
        session.delete(categoria)
        confirmar_cambios(session)