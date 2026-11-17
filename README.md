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
