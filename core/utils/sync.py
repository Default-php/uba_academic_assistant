import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"

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

    if "dashboard" in login_response.url or "my" in login_response.url:
        print("Inicio de sesión exitoso ✔")
    elif "login" in login_response.url:
        print("❌ Inicio de sesión fallido. Revisa tus credenciales.")
        return None
    else:
        print("Inicio de sesión realizado, pero no se pudo verificar completamente.")

    return session  # Se puede usar luego para navegar páginas internas


if __name__ == "__main__":
    sesion = iniciar_sesion_uba()
    if sesion:
        print("Sesión iniciada, puedes continuar extrayendo contenido...")
    #    dashboard_url = "https://pregrado.campusvirtualuba.net.ve/trimestre/my/"  # probable
    #    res = sesion.get(dashboard_url)
    #    print(res.text)  # esto imprimirá el HTML del panel
        
        