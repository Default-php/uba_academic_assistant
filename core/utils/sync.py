import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"
COURSES_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/my/courses.php"

# Datos de login
USERNAME = os.getenv("UBA_USERNAME")
PASSWORD = os.getenv("UBA_PASSWORD")


def iniciar_sesion_uba():
    session = requests.Session()

    # Obtener la página de login para extraer el token CSRF
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    token_input = soup.find('input', {'name': 'logintoken'})
    logintoken = token_input['value'] if token_input else None

    if not logintoken:
        print("No se pudo encontrar el logintoken. Revisa la página de login.")
        return None

    # Preparar los datos del formulario
    payload = {
        'username': USERNAME,
        'password': PASSWORD,
        'logintoken': logintoken
    }

    # Enviar la solicitud de login (POST)
    login_response = session.post(LOGIN_URL, data=payload)

    if login_response.url.startswith("https://pregrado.campusvirtualuba.net.ve/trimestre/my/"):
        print("Inicio de sesión exitoso ✔")
        return session
    else:
        print("❌ Inicio de sesión fallido. Revisa tus credenciales.")
        return None


def obtener_materias(session):
    """
    Extrae la lista de materias inscritas desde la página de cursos.
    Devuelve una lista de diccionarios con 'id' y 'nombre'.
    """
    resp = session.get(COURSES_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')

    materias = []
    for a in soup.select('a.coursename[href*="course/view.php?id="]'):
        href = a.get('href', '')
        span = a.find('span', class_='multiline')
        nombre = span.get_text(strip=True) if span else "Sin nombre"
        if 'id=' in href:
            course_id = href.split('id=')[-1]
            materias.append({'id': course_id, 'nombre': nombre})

    return materias



if __name__ == "__main__":
    sesion = iniciar_sesion_uba()
    if sesion:
        materias = obtener_materias(sesion)
        print("Materias encontradas:")
        for m in materias:
            print(f"- {m['id']}: {m['nombre']}")
        # Aquí podrías llamar a tu ORM para guardar cada materia en tu modelo Subject
