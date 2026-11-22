from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.conexion import Base

ESTADO_ACTIVO = "ACTIVO"
ESTADO_DEVUELTO = "DEVUELTO"


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), default="")
    
    equipos: Mapped[list["Equipo"]] = relationship(back_populates="categoria")

    def a_dict(self):
        return {"id": self.id, 
                "nombre": self.nombre, 
                "descripcion": self.descripcion}


class Equipo(Base):
    __tablename__ = "equipos"
    __table_args__ = (
        CheckConstraint("precio_diario > 0", name="ck_equipo_precio"),
        CheckConstraint("stock_total >= 0", name="ck_equipo_stock_total"),
        CheckConstraint("stock_disponible >= 0", name="ck_equipo_stock_disponible"),
        CheckConstraint("stock_disponible <= stock_total", name="ck_equipo_stock_coherente"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    precio_diario: Mapped[float]
    stock_total: Mapped[int]
    stock_disponible: Mapped[int]
    tipo: Mapped[str] = mapped_column(String(30), default="GENERAL")

    categoria: Mapped["Categoria"] = relationship(back_populates="equipos")
    arriendos: Mapped[list["Arriendo"]] = relationship(back_populates="equipo")

    def a_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria_id": self.categoria_id,
            "categoria": self.categoria.nombre,
            "tipo": self.tipo,
            "precio_diario": self.precio_diario,
            "stock_total": self.stock_total,
            "stock_disponible": self.stock_disponible,
        }


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    telefono: Mapped[str] = mapped_column(String(30), default="")

    arriendos: Mapped[list["Arriendo"]] = relationship(back_populates="cliente")

    def a_dict(self):
        return {"id": self.id, 
                "nombre": self.nombre, 
                "correo": self.correo, 
                "telefono": self.telefono}


class Arriendo(Base):
    __tablename__ = "arriendos"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_arriendo_cantidad"),
        CheckConstraint("estado IN ('ACTIVO', 'DEVUELTO')", name="ck_arriendo_estado"),
        CheckConstraint("fecha_fin_prevista >= fecha_inicio", name="ck_arriendo_fechas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    fecha_inicio: Mapped[date]
    fecha_fin_prevista: Mapped[date]
    cantidad: Mapped[int]
    estado: Mapped[str] = mapped_column(String(10), default=ESTADO_ACTIVO)
    costo_total: Mapped[float] = mapped_column(default=0)
    fecha_devolucion: Mapped[Optional[date]]

    equipo: Mapped["Equipo"] = relationship(back_populates="arriendos")
    cliente: Mapped["Cliente"] = relationship(back_populates="arriendos")

    def a_dict(self):
        return {
            "id": self.id,
            "equipo_id": self.equipo_id,
            "cliente_id": self.cliente_id,
            "equipo": self.equipo.nombre,
            "cliente": self.cliente.nombre,
            "cantidad": self.cantidad,
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin_prevista": self.fecha_fin_prevista.isoformat(),
            "fecha_devolucion": self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            "estado": self.estado,
            "costo_total": self.costo_total,
        }
