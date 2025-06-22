from django.core.management.base import BaseCommand
from core.models import Subject, Evaluation
from core.utils.selenium_setup import iniciar_sesion, ir_a_url
from core.utils.parser_evaluations import parse_evaluation_text
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import urllib.parse
import os
import requests
import time
import re

def remove_time_param(url):
    """
    Remueve el parámetro 'time' de la URL, si existe.
    """
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'time' in query_params:
        del query_params['time']
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    return urllib.parse.urlunparse(parsed_url._replace(query=new_query))

class Command(BaseCommand):
    help = "Sincroniza las evaluaciones desde Moodle y descarga imágenes localmente"

    def handle(self, *args, **options):
        print("🔄 Iniciando sincronización de evaluaciones...")

        BASE_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/"
        driver = iniciar_sesion()

        # Creamos una sesión de requests y agregamos las cookies de Selenium para mantener la autenticación.
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        subjects = Subject.objects.all()

        for subject in subjects:
            course_url = f"{BASE_URL}course/view.php?id={subject.codigo}"
            ir_a_url(driver, course_url)
            time.sleep(2)

            evaluaciones = driver.find_elements(By.CSS_SELECTOR, 'li.activity.assign a.aalink')

            for i in range(len(evaluaciones)):
                # Actualizamos la lista en cada iteración
                evaluaciones = driver.find_elements(By.CSS_SELECTOR, 'li.activity.assign a.aalink')
                enlace = evaluaciones[i]

                try:
                    href = enlace.get_attribute('href')
                    moodle_id = href.split("id=")[-1]

                    try:
                        span = enlace.find_element(By.CLASS_NAME, 'instancename')
                        titulo_raw = span.text.strip()
                    except NoSuchElementException:
                        titulo_raw = enlace.text.strip()

                    datos = parse_evaluation_text(titulo_raw)

                    # Ir a la página del contenido
                    ir_a_url(driver, href)
                    time.sleep(2)

                    try:
                        div_contenido = driver.find_element(By.CSS_SELECTOR, ".box.generalbox")
                        contenido_html = div_contenido.get_attribute("innerHTML")

                        # Procesamos el HTML con BeautifulSoup
                        soup = BeautifulSoup(contenido_html, "html.parser")

                        # --- PROCESAMIENTO DE BLOQUES DE VIDEO ---
                        # Buscamos todos los bloques cuyo atributo class contenga "mediaplugin_videojs"
                        video_blocks = soup.find_all("div", class_=lambda x: x and "mediaplugin_videojs" in x)
                        for video in video_blocks:
                            # Extraemos todos los iframes en este bloque
                            iframes = video.find_all("iframe")
                            if iframes:
                                # Creamos un contenedor nuevo para los iframes
                                new_container = soup.new_tag("div", **{"class": "video-embed-group"})
                                for iframe in iframes:
                                    src = iframe.get("src")
                                    if src:
                                        # Creamos un nuevo iframe limpio, sin gran cantidad de atributos adicionales,
                                        # con styling inline para limitar el tamaño (puedes ajustar los valores según necesites)
                                        new_iframe = soup.new_tag("iframe",
                                                                src=src,
                                                                frameborder="0",
                                                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
                                                                allowfullscreen="true",
                                                                style="width:100%; max-width:600px; height:350px;")
                                        new_container.append(new_iframe)
                                # Reemplazamos el bloque completo por nuestro contenedor limpio
                                video.replace_with(new_container)
                            else:
                                # Si no se detectan iframes, eliminamos el bloque para no dejar información inútil
                                video.decompose()
                        # --- FIN BLOQUES DE VIDEO ---
                        
                        # Procesamos imágenes
                        images_found = soup.find_all("img")
                        print(f"Encontradas {len(images_found)} imágenes en la evaluación: {titulo_raw}")

                        for j, img in enumerate(images_found):
                            src = img.get("src", "")
                            if src.startswith("/"):
                                src = urljoin(BASE_URL, src)
                            src_clean = remove_time_param(src)

                            try:
                                response = session.get(src_clean, stream=True)
                                response.raise_for_status()
                                content_type = response.headers.get("Content-Type", "").lower()
                                if not content_type.startswith("image/"):
                                    print(f"El recurso en {src_clean} no es una imagen (Content-Type: {content_type}). Se omite.")
                                    continue

                                # Obtenemos el nombre original y la extensión
                                original_filename = os.path.basename(urllib.parse.urlparse(src_clean).path)
                                base_filename, ext = os.path.splitext(original_filename)
                                if not ext:
                                    if content_type == "image/png":
                                        ext = ".png"
                                    elif content_type in ("image/jpeg", "image/jpg"):
                                        ext = ".jpg"
                                    elif content_type == "image/gif":
                                        ext = ".gif"
                                    else:
                                        ext = ".png"
                                    original_filename = base_filename + ext

                                # Sanitizamos el nombre para que no tenga espacios ni caracteres extraños.
                                safe_base_filename = re.sub(r'\s+', '_', base_filename)
                                safe_base_filename = re.sub(r'[^\w\-]', '', safe_base_filename)

                                new_filename = f"evaluation_{moodle_id}_{j}_{safe_base_filename}{ext}"

                                local_dir = os.path.join("media", "evaluaciones")
                                if not os.path.exists(local_dir):
                                    os.makedirs(local_dir)

                                local_path = os.path.join(local_dir, new_filename)
                                with open(local_path, "wb") as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        f.write(chunk)

                                local_url = f"/media/evaluaciones/{new_filename}"
                                img["src"] = local_url
                                print("Imagen descargada y procesada:", img["src"])

                            except Exception as img_ex:
                                print(f"❌ Error al descargar la imagen {src_clean}: {img_ex}")

                        # Reconstruimos el HTML con los cambios (videos limpios e imágenes actualizadas)
                        contenido_html = str(soup)
                    except NoSuchElementException:
                        contenido_html = ""

                    evaluacion, creada = Evaluation.objects.update_or_create(
                        moodle_id=moodle_id,
                        defaults={
                            "titulo": titulo_raw,
                            "subject": subject,
                            "numero": datos.get("numero"),
                            "unidad": datos.get("unidad"),
                            "tipo": datos.get("tipo"),
                            "seccion": datos.get("seccion"),
                            "profesor": datos.get("profesor"),
                            "porcentaje": datos.get("porcentaje"),
                            "fecha_inicio": datos.get("fecha_inicio"),
                            "fecha_cierre": datos.get("fecha_cierre"),
                            "contenido_html": contenido_html,
                        }
                    )

                    estado = "✔ Creada" if creada else "⏩ Actualizada"
                    print(f"{estado}: {titulo_raw} (ID {moodle_id})")

                    ir_a_url(driver, course_url)
                    time.sleep(2)

                except Exception as e:
                    print(f"❌ Error con evaluación #{i + 1}: {e}")

        driver.quit()
        print("✅ Sincronización de evaluaciones completada.")