import re
from datetime import datetime

def parse_evaluation_text(text):
    """
    Recibe un string que representa una evaluación y devuelve un diccionario con los campos extraídos.
    Campos posibles: numero, unidad, tipo, seccion, profesor, porcentaje, fecha_inicio, fecha_cierre
    """
    resultado = {
        "numero": None,
        "unidad": None,
        "tipo": None,
        "seccion": None,
        "profesor": None,
        "porcentaje": None,
        "fecha_inicio": None,
        "fecha_cierre": None
    }

    # Convertir a minúscula sin afectar nombres propios (evitar problemas con REGEX)
    texto = text.replace("\n", " ").strip()

    # Número de evaluación
    match = re.search(r"[Nn][\u00ba°]?[\s\-]*([\dIVX]+)", texto)
    if match:
        resultado["numero"] = match.group(1)

    # Unidad
    match = re.search(r"[Uu]nidad[\s:-]*([\dIVX]+)", texto)
    if match:
        resultado["unidad"] = match.group(1)

    # Porcentaje
    match = re.search(r"([\d]{1,2})\s*%", texto)
    if match:
        resultado["porcentaje"] = int(match.group(1))

    # Sección
    match = re.search(r"[Ss]ecci[oó]n[:\s]*(\w[\w\-\s]*)", texto)
    if match:
        resultado["seccion"] = match.group(1).strip()

    # Profesor
    match = re.search(r"(?:[Pp]rof(?:\.?)|[Tt]utor(?:a)?[:\s]*)\s*([A-Z][A-Za-zÁÉÍÓÚÑñ\s\.]+)", texto)
    if match:
        resultado["profesor"] = match.group(1).strip()

    # Tipo de evaluación: lo que está entre número/unidad y sección/profesor
    match = re.search(r"(?:Unidad\s*[\dIVX]+\s*\|?|\d\s*\||[\dIVX]+\s*\||\|)\s*([^|\n]{5,50}?)\s*\|\s*(?:[Ss]ecci[oó]n|[Pp]rof|[Tt]utor)", texto)
    if match:
        resultado["tipo"] = match.group(1).strip()

    # Fechas (inicio y cierre)
    fecha_inicio = None
    fecha_cierre = None

    # Manejar diferentes patrones de fechas con regex
    match_fechas = re.findall(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(a las)?\s*(\d{1,2}:\d{2})?", texto)
    if len(match_fechas) >= 2:
        try:
            f1 = match_fechas[0][0].replace("-", "/")
            f2 = match_fechas[1][0].replace("-", "/")
            resultado["fecha_inicio"] = datetime.strptime(f1, "%d/%m/%Y") if len(f1.split("/")) == 3 else None
            resultado["fecha_cierre"] = datetime.strptime(f2, "%d/%m/%Y") if len(f2.split("/")) == 3 else None
        except Exception:
            pass

    return resultado

# Ejemplo de uso:
if __name__ == "__main__":
    ejemplos = [
        "Actividad Sumativa N° 1 │ Unidad 1 │ Informe de Investigación │ Sección 1 │ Prof. Oswald Carvajal │ 25%│ Fecha de Inicio: 26/05/2025 │ Hora: 00:01 a.m. │ Fecha de Cierre: 30/05/2025 │ Hora: 23:59 p.m. │ Hora Venezuela │",
        "Actividad sumativa 3: Plan de acción | Sección 1 | Tutora: Adriana Miranda | 25% | Desde el 23/06/2025 a las 00:01 am hasta el 27/06/2025 a las 23:59 pm (Hora Venezuela)"
    ]
    for texto in ejemplos:
        print("\n---\nTexto:", texto)
        print("Resultado:", parse_evaluation_text(texto))
