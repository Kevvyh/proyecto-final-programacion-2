import math
import re
from datetime import date, datetime

class ErrorNegocio(Exception):
    pass

def texto_obligatorio(valor, campo):
    valor = (valor or "").strip()
    if not valor:
        raise ErrorNegocio(f"El campo '{campo}' es obligatorio.")
    return valor

def a_entero(valor, campo):
    try:
        return int(str(valor).strip())
    except (ValueError, TypeError):
        raise ErrorNegocio(f"'{campo}' debe ser un número entero.")

def a_decimal(valor, campo):
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except (ValueError, TypeError):
        raise ErrorNegocio(f"'{campo}' debe ser un número.")
    if not math.isfinite(numero):
        raise ErrorNegocio(f"'{campo}' debe ser un número válido.")
    return numero

def a_fecha(valor, campo):
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ErrorNegocio(f"'{campo}' debe tener el formato AAAA-MM-DD (ejemplo: 2026-11-30)")

def validar_correo(valor):
    correo = texto_obligatorio(valor, "Correo").lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
        raise ErrorNegocio("El correo no tiene un formato válido (ejemplo: nombre@dominio.cl)")
    return correo

def validar_telefono(valor):
    telefono = (valor or "").strip()
    if telefono and not re.match(r"^[0-9+\-\s()]{7,20}$", telefono):
        raise ErrorNegocio("El teléfono solo puede tener números, +, -, parentesis y espacios (7 a 20 caracteres).")
    return telefono