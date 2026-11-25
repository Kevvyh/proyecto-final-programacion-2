import os
import shutil
import tempfile
import unittest
from datetime import date, timedelta

_carpeta_temporal = tempfile.mkdtemp()
os.environ["ARRIENDOS_DB"] = os.path.join(_carpeta_temporal, "prueba.db")

from src.database import modelos  # noqa: E402,F401
from src.database.conexion import Base, crear_tablas, engine  # noqa: E402
from src.services import (arriendo_service, categoria_service, cliente_service,  # noqa: E402
                          consulta_service, equipo_service)
from src.utils.validaciones import ErrorNegocio  # noqa: E402

HOY = date.today()
EN_7_DIAS = HOY + timedelta(days=7)


def tearDownModule():
    engine.dispose()
    shutil.rmtree(_carpeta_temporal, ignore_errors=True)


class PruebasArriendos(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(engine)
        crear_tablas()
        self.cat = categoria_service.crear_categoria("Acuáticos", "Agua")
        self.equipo = equipo_service.crear_equipo("Kayak", self.cat["id"], 10000, 5, "ACUATICO")
        self.cliente = cliente_service.crear_cliente("Ana Pérez", "ana@correo.cl", "+56 9 1234 5678")

    def stock(self):
        return [e for e in equipo_service.listar_equipos() if e["id"] == self.equipo["id"]][0]["stock_disponible"]

    def test_flujo_de_demostracion(self):
        #1: equipo con stock total 5 -> disponible 5
        self.assertEqual(self.stock(), 5)
        #2: arriendo de 2 unidades -> disponible 3, ACTIVO
        arriendo = arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, 2)
        self.assertEqual(self.stock(), 3)
        self.assertEqual(arriendo["estado"], "ACTIVO")
        #3: intentar arrendar 4 más -> rechazado, stock sigue en 3
        with self.assertRaises(ErrorNegocio):
            arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, 4)
        self.assertEqual(self.stock(), 3)
        #4: devolver -> disponible 5, DEVUELTO
        devuelto = arriendo_service.devolver_arriendo(arriendo["id"])
        self.assertEqual(self.stock(), 5)
        self.assertEqual(devuelto["estado"], "DEVUELTO")
        #5: devolver otra vez -> rechazado, stock sigue en 5
        with self.assertRaises(ErrorNegocio):
            arriendo_service.devolver_arriendo(arriendo["id"])
        self.assertEqual(self.stock(), 5)
        #6: "cerrar y reabrir": se descartan las conexiones y se vuelve a leer desde el archivo
        engine.dispose()
        self.assertEqual(self.stock(), 5)
        self.assertEqual(consulta_service.arriendos_por_categoria(), [("Acuáticos", 1)])
        self.assertEqual(consulta_service.equipos_mas_arrendados(), [("Kayak", 1)])

    def test_cantidad_invalida(self):
        for cantidad in (0, -1, "abc"):
            with self.assertRaises(ErrorNegocio):
                arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, cantidad)
        self.assertEqual(self.stock(), 5)

    def test_fecha_fin_anterior_al_inicio(self):
        with self.assertRaises(ErrorNegocio):
            arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], EN_7_DIAS, HOY, 1)

    def test_equipo_o_cliente_inexistente(self):
        with self.assertRaises(ErrorNegocio):
            arriendo_service.registrar_arriendo(999, self.cliente["id"], HOY, EN_7_DIAS, 1)
        with self.assertRaises(ErrorNegocio):
            arriendo_service.registrar_arriendo(self.equipo["id"], 999, HOY, EN_7_DIAS, 1)

    def test_costo_usa_factory_method(self):
        # 10.000 x 7 días x 2 unidades = 140.000 + 10% (acuatico) = 154.000
        arriendo = arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, 2)
        self.assertEqual(arriendo["costo_total"], 154000)

    def test_no_eliminar_registros_con_arriendos(self):
        arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, 1)
        with self.assertRaises(ErrorNegocio):
            equipo_service.eliminar_equipo(self.equipo["id"])
        with self.assertRaises(ErrorNegocio):
            cliente_service.eliminar_cliente(self.cliente["id"])
        with self.assertRaises(ErrorNegocio):
            categoria_service.eliminar_categoria(self.cat["id"])

    def test_validaciones_de_equipo(self):
        with self.assertRaises(ErrorNegocio):
            equipo_service.crear_equipo("X", self.cat["id"], 0, 3)       # precio no positivo
        with self.assertRaises(ErrorNegocio):
            equipo_service.crear_equipo("X", self.cat["id"], 100, -1)    # stock negativo
        with self.assertRaises(ErrorNegocio):
            equipo_service.crear_equipo("X", 999, 100, 3)                # categoría inexistente
        with self.assertRaises(ErrorNegocio):
            equipo_service.crear_equipo("X", self.cat["id"], 100, 3, "RARO")  # tipo desconocido

    def test_no_bajar_stock_total_bajo_lo_arrendado(self):
        arriendo_service.registrar_arriendo(self.equipo["id"], self.cliente["id"], HOY, EN_7_DIAS, 3)
        with self.assertRaises(ErrorNegocio):
            equipo_service.actualizar_equipo(self.equipo["id"], "Kayak", self.cat["id"], 10000, 2, "ACUATICO")
        actualizado = equipo_service.actualizar_equipo(self.equipo["id"], "Kayak", self.cat["id"], 10000, 8, "ACUATICO")
        self.assertEqual(actualizado["stock_disponible"], 5)

    def test_unicos(self):
        with self.assertRaises(ErrorNegocio):
            categoria_service.crear_categoria("acuáticos")               # nombre repetido
        with self.assertRaises(ErrorNegocio):
            cliente_service.crear_cliente("Otra Ana", "ANA@correo.cl")   # correo repetido
        with self.assertRaises(ErrorNegocio):
            cliente_service.crear_cliente("Sin arroba", "correo-malo")


if __name__ == "__main__":
    unittest.main()
