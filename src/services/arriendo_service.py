from datetime import date
from sqlalchemy.orm import Session

from src.database.conexion import engine, confirmar_cambios
from src.database.modelos import ESTADO_ACTIVO, ESTADO_DEVUELTO, Arriendo, Cliente, Equipo
from src.factory.equipo_factory import producto_de
from src.utils.validaciones import ErrorNegocio, a_entero, a_fecha

def registrar_arriendo(equipo_id, cliente_id, fecha_inicio, 
                       fecha_fin_prevista, cantidad):
    cantidad = a_entero(cantidad, "Cantidad")
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad debe ser mayir que 0")
    inicio = a_fecha(fecha_inicio, "Fecha de inicio")
    fin = a_fecha(fecha_fin_prevista, "Fecha de termino prevista")
    if fin < inicio:
        raise ErrorNegocio("La fecha de termino prevista no puede ser anterior a la fecha de inicio")

    with Session(engine) as session:
        equipo = session.get(Equipo, equipo_id) if equipo_id is not None else None
        if equipo is None:
            raise ErrorNegocio("El equipo seleccionado no existe")
        cliente = session.get(Cliente, cliente_id) if cliente_id is not None else None
        if cliente is None:
            raise ErrorNegocio("El cliente seleccionado no existe")
        if cantidad > equipo.stock_disponible:
            raise ErrorNegocio(
                f"Stock insuficiente: se piden {cantidad} unidad(es) de {equipo.nombre}."
                f"Solo hay {equipo.stock_disponible} disponible(s)"
            )

        #costo que depende del tipo de equipo. minimo de cobro 1 dia
        dias = max((fin-inicio).days, 1)
        costo = producto_de(equipo.tipo).calcular_costo(equipo.precio_diario, dias, cantidad)

        #descontar ejemplares y crear arriendo
        equipo.stock_disponible -= cantidad
        arriendo = Arriendo(
            equipo_id=equipo.id,
            cliente_id=cliente.id,
            fecha_inicio=inicio,
            fecha_fin_prevista=fin,
            cantidad=cantidad,
            estado=ESTADO_ACTIVO,
            costo_total=costo,
        )
        session.add(arriendo)
        confirmar_cambios(session)
        return arriendo.a_dict()

def devolver_arriendo(arriendo_id):
    with Session(engine) as session:
        arriendo = session.get(Arriendo, arriendo_id) if arriendo_id is not None else None
        if arriendo is None:
            raise ErrorNegocio("El arriendo seleccionado no existe")
        if arriendo.estado != ESTADO_ACTIVO:
            raise ErrorNegocio(
                f"El arriendo #{arriendo.id} ya fue devuelto."
                "No se puede devolver dos veces"
                )

        arriendo.estado = ESTADO_DEVUELTO
        arriendo.fecha_devolucion = date.today()
        arriendo.equipo.stock_disponible += arriendo.cantidad
        confirmar_cambios(session)
        return arriendo.a_dict()