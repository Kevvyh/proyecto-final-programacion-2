import os 
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase

from src.utils.validaciones import ErrorNegocio

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_DB = os.environ.get("ARRIENDOS_DB", str(RAIZ_PROYECTO / "arriendos.db"))

engine= create_engine(f"sqlite:///{RUTA_DB}")

def _activar_claves_foraneas(conexion, registro):
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

event.listen(engine, "connect", _activar_claves_foraneas)

class Base(DeclarativeBase):
    pass

def crear_tablas():
    from src.database import modelos  # noqa: F401
    Base.metadata.create_all(engine)

def confirmar_cambios(session):
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ErrorNegocio(
            "No se pudo guardar: los datos chocan con una restricción de la base de datos"
            "(dato duplicado o registro vinculado)"
        ) from error
    
