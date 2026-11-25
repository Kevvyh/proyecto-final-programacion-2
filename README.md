# Sistema de Gestión de Arriendo de Equipamiento Deportivo

Proyecto Final – Evaluación 3 · Programación II · Universidad Católica de Temuco

**Integrantes:** Kevin Inalaf · Joaquín Carrillo
**Entrega:** 1 de diciembre de 2026

Aplicación de escritorio para administrar categorías, equipos y clientes, registrar arriendos, controlar el stock disponible y procesar devoluciones. Los datos se guardan en una base SQLite mediante SQLAlchemy ORM.

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.10+ | Lenguaje |
| SQLAlchemy 2.x (ORM) | Modelo (DeclarativeBase, Mapped, mapped_column) y acceso a datos |
| SQLite | Base de datos (`arriendos.db`) |
| Tkinter / ttk | Interfaz gráfica |
| Matplotlib | Gráficos incrustados en Tkinter |
| Factory Method | Creación de tipos de equipamiento |

## Instalación y ejecución

```bash
# 1. (Opcional) crear un entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python main.py
```

- La base de datos `arriendos.db` **se crea automáticamente** la primera vez que se ejecuta la app. Si se cierra y se vuelve a abrir, los datos se conservan.
- Tkinter viene con Python en Windows y macOS. En Linux (Ubuntu/Debian): `sudo apt install python3-tk`.
- **Datos de ejemplo** (opcional, útil para ver los gráficos): `python datos_demo.py`

## Estructura del proyecto

```
proyecto_arriendos/
├── main.py                      # Punto de entrada
├── datos_demo.py                # Datos de ejemplo (opcional)
├── requirements.txt
├── README.md
├── src/
│   ├── database/
│   │   ├── conexion.py          # Engine, Base (DeclarativeBase), crear_tablas, confirmar_cambios
│   │   └── modelos.py           # Categoria, Equipo, Cliente, Arriendo (Mapped / mapped_column)
│   ├── factory/
│   │   └── equipo_factory.py    # Factory Method (tipos de equipamiento)
│   ├── services/                # Lógica de negocio (sin Tkinter)
│   │   ├── categoria_service.py
│   │   ├── equipo_service.py
│   │   ├── cliente_service.py
│   │   ├── arriendo_service.py  # Arriendos y devoluciones
│   │   └── consulta_service.py  # Consultas y datos para gráficos
│   ├── graficos/
│   │   └── graficos.py          # Gráficos Matplotlib
│   ├── utils/
│   │   └── validaciones.py      # ErrorNegocio y funciones de validación
│   └── ui/                      # Interfaz Tkinter (una pestaña por módulo)
│       ├── app.py, componentes.py
│       └── tab_categorias.py, tab_equipos.py, tab_clientes.py,
│           tab_arriendos.py, tab_consultas.py, tab_graficos.py
└── tests/
    └── test_demo.py             # Pruebas automáticas
```

La app tiene tres capas: **UI → services → database**. La interfaz nunca toca la base de datos directamente; solo llama a los servicios, que validan y lanzan `ErrorNegocio` con un mensaje claro que la interfaz muestra al usuario.

Los modelos usan el estilo de SQLAlchemy 2.x (`DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`) y cada servicio trabaja con `with Session(engine) as session:` y un `commit` explícito (una sola transacción por operación).

## Modelo de datos

| Entidad | Atributos | Relaciones |
|---|---|---|
| **Categoria** | id, nombre (único), descripcion | 1 categoría → N equipos |
| **Equipo** | id, nombre, categoria_id, precio_diario (>0), stock_total (>=0), stock_disponible (>=0, <= total), **tipo** | Pertenece a una categoría; 1 equipo → N arriendos |
| **Cliente** | id, nombre, correo (único), telefono | 1 cliente → N arriendos |
| **Arriendo** | id, equipo_id, cliente_id, fecha_inicio, fecha_fin_prevista, cantidad (>0), estado (ACTIVO/DEVUELTO), **costo_total**, **fecha_devolucion** | Pertenece a un equipo y a un cliente |

Atributos agregados: `Equipo.tipo` (lo define el Factory Method), `Arriendo.costo_total` y `Arriendo.fecha_devolucion`.
Las reglas numéricas y de fechas también están como `CheckConstraint` en la BD, y las claves foráneas se activan con `PRAGMA foreign_keys = ON`.

## Reglas de negocio implementadas

- Arriendo solo si la cantidad es positiva y no supera el stock disponible; el stock se descuenta **en la misma transacción** que crea el arriendo.
- Equipo y cliente deben existir. La fecha de término no puede ser anterior a la de inicio.
- Devolución solo de arriendos `ACTIVO`: pasa a `DEVUELTO` y restituye exactamente las unidades prestadas. Una segunda devolución se rechaza.
- No se puede eliminar una categoría con equipos, ni un equipo o cliente con arriendos: se informa al usuario con un mensaje.
- No se puede bajar el stock total de un equipo por debajo de las unidades que están arrendadas.
- Nombre de categoría y correo de cliente son únicos (sin distinguir mayúsculas).
- El costo se calcula con `precio_diario × días × cantidad` más el recargo del tipo de equipo (mínimo 1 día).

## Factory Method

**Problema:** cada tipo de equipo (acuático, montaña, ciclismo, general) tiene reglas distintas; por ejemplo, un recargo diferente en el costo del arriendo. Sin el patrón, habría `if tipo == ...` repetidos por todo el código.

**Solución (`src/factory/equipo_factory.py`):**

- `EquipamientoDeportivo` (producto abstracto) con `calcular_costo()` y `describir()`.
- Productos concretos: `EquipoAcuatico` (10 %), `EquipoMontana` (15 %), `EquipoCiclismo` (5 %), `EquipoGeneral` (0 %).
- `CreadorEquipo` (creador abstracto) declara el **factory method** `crear_producto()` y un método `crear_modelo()` que construye el `Equipo` ORM usando ese producto.
- Creadores concretos (`CreadorAcuatico`, ...) deciden qué producto se crea.

**Integración con el modelo persistente:**

1. Al crear un equipo, `equipo_service.crear_equipo()` obtiene el creador según el tipo elegido y llama a `crear_modelo()`, que devuelve un `Equipo` con la columna `tipo` ya definida.
2. Al registrar un arriendo, `arriendo_service` lee `equipo.tipo` desde la BD, pide el producto con `producto_de(tipo)` y calcula el costo con su recargo.
3. Agregar un tipo nuevo solo requiere una clase producto, una clase creador y una línea en `CREADORES`, sin modificar los servicios.

## Pruebas de demostración

Las 6 pruebas del enunciado están automatizadas en `tests/test_demo.py` (usa una BD temporal):

```bash
python -m unittest discover -s tests -v
```

| Paso | Acción | Resultado esperado | Cubierto por |
|---|---|---|---|
| 1 | Crear categoría y equipo con stock 5 | Disponible 5 | `test_flujo_de_demostracion` |
| 2 | Crear cliente y arrendar 2 | Disponible 3; ACTIVO | `test_flujo_de_demostracion` |
| 3 | Intentar arrendar 4 más | Rechazado; sigue en 3 | `test_flujo_de_demostracion` |
| 4 | Devolver el arriendo | Disponible 5; DEVUELTO | `test_flujo_de_demostracion` |
| 5 | Devolver el mismo arriendo | Rechazado; sigue en 5 | `test_flujo_de_demostracion` |
| 6 | Cerrar, reabrir y ver gráficos | Datos persistentes | `test_flujo_de_demostracion` |

También hay pruebas de cantidad inválida, fechas, equipo/cliente inexistente, eliminaciones restringidas, unicidad y costo con Factory Method.

Para probarlo a mano en la interfaz: pestaña **Categorías** → **Equipos** (stock 5) → **Clientes** → **Arriendos** (registrar 2, intentar 4, devolver, devolver de nuevo) → cerrar la app, abrirla de nuevo y entrar a **Gráficos**.

## Capturas

> Reemplazar con las capturas reales (carpeta `capturas/`). Los gráficos se pueden exportar con
> `python -c "from src.graficos import graficos; graficos.guardar_graficos_png()"`.

- ![Categorías](capturas/categorias.png)
- ![Equipos](capturas/equipos.png)
- ![Clientes](capturas/clientes.png)
- ![Arriendos](capturas/arriendos.png)
- ![Consultas](capturas/consultas.png)
- ![Gráficos](capturas/graficos.png)

## Gráficos

1. **Cantidad de arriendos por categoría** (barras).
2. **Equipos con mayor número de arriendos** (barras horizontales, top 5).

Ambos se generan con consultas SQLAlchemy a la BD (`src/services/consulta_service.py`) y cuentan **operaciones de arriendo**, no unidades.

## Fuentes consultadas

> Dejar solo las que realmente se usaron.

- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/
- Python – tkinter: https://docs.python.org/3/library/tkinter.html
- Python – tkinter.ttk (Treeview, Combobox, Notebook): https://docs.python.org/3/library/tkinter.ttk.html
- Matplotlib – Embedding in Tk: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
- Refactoring Guru – Factory Method: https://refactoring.guru/es/design-patterns/factory-method

## Reparto del trabajo

| Integrante | Responsabilidad |
|---|---|
| **Kevin Inalaf** | `src/database/` (conexion, modelos), `src/factory/`, servicios de categorías, equipos y arriendos, pestañas Categorías, Equipos y Arriendos |
| **Joaquín Carrillo** | `src/utils/validaciones.py`, servicio de clientes y consultas, `src/graficos/`, `src/ui/app.py`, `componentes.py`, pestañas Clientes, Consultas y Gráficos, `main.py`, `datos_demo.py` |
| Ambos | Pruebas, README, capturas y preparación de la interrogación |
