"""Scraping de evaluaciones del campus UBA."""

import os
import re
import time
import urllib.parse
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from core.models import Subject
from core.scraping.constants import (
    ACTIVITY_LINK_SELECTOR,
    BASE_URL,
    CONTENT_BOX_SELECTOR,
    INSTANCENAME_CLASS,
)
from core.scraping.parsers import parse_evaluation_text


def remove_time_param(url: str) -> str:
    """Elimina el parámetro 'time' de la URL si existe."""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "time" in query:
        del query["time"]
    new_q = urllib.parse.urlencode(query, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_q))


def scrape_evaluations(client) -> list[dict]:
    """
    Asume que el cliente ya está autenticado (login hecho por el llamador).
    Itera sobre todas las materias en la BD y extrae sus evaluaciones.
    Descarga imágenes a media/evaluaciones y limpia videos.
    Devuelve lista de dicts con keys:
      subject_codigo, moodle_id, titulo, numero, unidad, tipo, seccion,
      profesor, porcentaje, fecha_inicio, fecha_cierre, contenido_html, url.
    """
    # Copiar cookies de Selenium a Requests
    session = client.cookies_to_requests()

    results = []
    subjects = Subject.objects.all()

    for subject in subjects:
        course_url = f"{BASE_URL}course/view.php?id={subject.codigo}"
        client.go(course_url)
        time.sleep(2)

        links = client.driver.find_elements(By.CSS_SELECTOR, ACTIVITY_LINK_SELECTOR)
        for idx in range(len(links)):
            # refresca la lista por si cambió
            links = client.driver.find_elements(By.CSS_SELECTOR, ACTIVITY_LINK_SELECTOR)
            enlace = links[idx]
            try:
                href = enlace.get_attribute("href")
                moodle_id = href.split("id=")[-1]

                # Título bruto
                try:
                    span = enlace.find_element(By.CLASS_NAME, INSTANCENAME_CLASS)
                    titulo_raw = span.text.strip()
                except NoSuchElementException:
                    titulo_raw = enlace.text.strip()

                datos = parse_evaluation_text(titulo_raw)

                # Ir a la página de la evaluación
                client.go(href)
                time.sleep(2)

                # Extraer y procesar el contenido
                try:
                    cont_div = client.driver.find_element(By.CSS_SELECTOR, CONTENT_BOX_SELECTOR)
                    html = cont_div.get_attribute("innerHTML")
                    soup = BeautifulSoup(html, "html.parser")

                    # --- limpiar videos ---
                    for video in soup.find_all(
                        "div", class_=lambda c: c and "mediaplugin_videojs" in c
                    ):
                        iframes = video.find_all("iframe")
                        if iframes:
                            new_c = soup.new_tag("div", **{"class": "video-embed-group"})
                            for ifr in iframes:
                                src = ifr.get("src")
                                if src:
                                    clean_iframe = soup.new_tag(
                                        "iframe",
                                        src=src,
                                        frameborder="0",
                                        allow=(
                                            "accelerometer; autoplay; clipboard-write; "
                                            "encrypted-media; gyroscope; picture-in-picture"
                                        ),
                                        allowfullscreen="true",
                                        style="width:100%; max-width:600px; height:350px;",
                                    )
                                    new_c.append(clean_iframe)
                            video.replace_with(new_c)
                        else:
                            video.decompose()

                    # --- descargar y reescribir imágenes ---
                    imgs = soup.find_all("img")
                    for j, img in enumerate(imgs):
                        src = img.get("src", "")
                        if src.startswith("/"):
                            src = urljoin(BASE_URL, src)
                        src = remove_time_param(src)

                        try:
                            r = session.get(src, stream=True)
                            r.raise_for_status()
                            ct = r.headers.get("Content-Type", "").lower()
                            if not ct.startswith("image/"):
                                continue

                            fname = os.path.basename(urllib.parse.urlparse(src).path)
                            base, ext = os.path.splitext(fname)
                            if not ext:
                                ext = ".png" if "png" in ct else ".jpg"
                                fname = base + ext

                            safe = re.sub(r"\s+", "_", base)
                            safe = re.sub(r"[^\w\-]", "", safe)
                            new_name = f"eval_{moodle_id}_{j}_{safe}{ext}"

                            media_dir = os.path.join(settings.MEDIA_ROOT, "evaluaciones")
                            os.makedirs(media_dir, exist_ok=True)
                            path = os.path.join(media_dir, new_name)
                            with open(path, "wb") as f:
                                for chunk in r.iter_content(8192):
                                    f.write(chunk)

                            img["src"] = f"/media/evaluaciones/{new_name}"
                        except Exception as e:
                            print(f"Error descargando imagen {src}: {e}")

                    contenido_html = str(soup)

                except NoSuchElementException:
                    contenido_html = ""

                # Fechas como date (el parser puede devolver datetime)
                fecha_inicio = datos.get("fecha_inicio")
                fecha_cierre = datos.get("fecha_cierre")
                if fecha_inicio is not None:
                    fecha_inicio = fecha_inicio.date()
                if fecha_cierre is not None:
                    fecha_cierre = fecha_cierre.date()

                # Acumula datos
                results.append(
                    {
                        "subject_codigo": subject.codigo,
                        "moodle_id": moodle_id,
                        "titulo": titulo_raw,
                        "numero": datos.get("numero"),
                        "unidad": datos.get("unidad"),
                        "tipo": datos.get("tipo"),
                        "seccion": datos.get("seccion"),
                        "profesor": datos.get("profesor"),
                        "porcentaje": datos.get("porcentaje"),
                        "fecha_inicio": fecha_inicio,
                        "fecha_cierre": fecha_cierre,
                        "contenido_html": contenido_html,
                        "url": href,
                    }
                )

                # Vuelve al listado de la materia
                client.go(course_url)
                time.sleep(1)

            except Exception as exc:
                print(f"Error evaluación #{idx + 1} en {subject.nombre}: {exc}")

    return results
