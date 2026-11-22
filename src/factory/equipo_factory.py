from abc import ABC, abstractmethod

from src.database.modelos import Equipo
from src.utils.validaciones import ErrorNegocio

#productos
class EquipamientoDeportivo(ABC):
    tipo = "GENERAL"
    recargo = 0.0       # 0.10 = 10% extra sobre el valor base del arriendo
    cuidados = ""

    def calcular_costo(self, precio_diario, dias, cantidad):
        base = precio_diario * dias * cantidad
        return round(base * (1 + self.recargo), 2)

    def describir(self):
        recargo_texto = f"recargo del {round(self.recargo * 100)}%" if self.recargo else "sin recargo"
        return f"{self.tipo}: {recargo_texto}. {self.cuidados}"

class EquipoAcuatico(EquipamientoDeportivo):
    tipo = "ACUATICO"
    recargo = 0.10
    cuidados = "Se cobra recargo por lavado y secado."

class EquipoMontana(EquipamientoDeportivo):
    tipo = "MONTANA"
    recargo = 0.15
    cuidados = "Se cobra recargo por revisión y mantención posterior al uso."

class EquipoCiclismo(EquipamientoDeportivo):
    tipo = "CICLISMO"
    recargo = 0.05
    cuidados = "Se cobra recargo por ajuste y lubricación."

class EquipoGeneral(EquipamientoDeportivo):
    tipo = "GENERAL"
    recargo = 0.0
    cuidados = "Sin condiciones especiales."


#creadores
class CreadorEquipo(ABC):

    @abstractmethod
    def crear_producto(self):
        # FACTORY METHOD: cada creador concreto lo reemplaza y devuelve su tipo de producto
        pass

    def crear_modelo(self, nombre, categoria_id, precio_diario, stock_total):
        producto = self.crear_producto()
        return Equipo(
            nombre=nombre,
            categoria_id=categoria_id,
            precio_diario=precio_diario,
            stock_total=stock_total,
            stock_disponible=stock_total,
            tipo=producto.tipo,
        )

class CreadorAcuatico(CreadorEquipo):
    def crear_producto(self):
        return EquipoAcuatico()

class CreadorMontana(CreadorEquipo):
    def crear_producto(self):
        return EquipoMontana()

class CreadorCiclismo(CreadorEquipo):
    def crear_producto(self):
        return EquipoCiclismo()

class CreadorGeneral(CreadorEquipo):
    def crear_producto(self):
        return EquipoGeneral()


#Registro: relaciona el texto guardado en la BD con su creador
CREADORES = {
    "ACUATICO": CreadorAcuatico(),
    "MONTANA": CreadorMontana(),
    "CICLISMO": CreadorCiclismo(),
    "GENERAL": CreadorGeneral(),
}
TIPOS_EQUIPO = list(CREADORES)

def obtener_creador(tipo):
    creador = CREADORES.get((tipo or "").strip().upper())
    if creador is None:
        raise ErrorNegocio(f"Tipo de equipo desconocido: '{tipo}'. Opciones: {', '.join(TIPOS_EQUIPO)}.")
    return creador

def producto_de(tipo):
    return obtener_creador(tipo).crear_producto()
