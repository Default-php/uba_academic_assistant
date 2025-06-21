from django.core.management.base import BaseCommand
from core.models import Subject, Evaluation
from core.utils.selenium_setup import iniciar_sesion, ir_a_url
from core.utils.parser_evaluations import parse_evaluation_text

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


class Command(BaseCommand):
    help = "Sincroniza las evaluaciones desde Moodle"

    def handle(self, *args, **options):
        print("🔄 Iniciando sincronización de evaluaciones...")

        driver = iniciar_sesion()
        subjects = Subject.objects.all()

        for subject in subjects:
            course_url = f"https://pregrado.campusvirtualuba.net.ve/trimestre/course/view.php?id={subject.codigo}"
            ir_a_url(driver, course_url)
            time.sleep(2)

            evaluaciones = driver.find_elements(By.CSS_SELECTOR, 'li.activity.assign a.aalink')

            for i in range(len(evaluaciones)):
                # Capturar el elemento nuevamente para evitar stale reference
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

                    # Ir a la página de contenido
                    ir_a_url(driver, href)
                    time.sleep(2)
                    try:
                        div_contenido = driver.find_element(By.CLASS_NAME, "box.generalbox")
                        contenido_html = div_contenido.get_attribute("outerHTML")
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

                    # Volver a la lista de evaluaciones para el siguiente enlace
                    ir_a_url(driver, course_url)
                    time.sleep(2)

                except Exception as e:
                    print(f"❌ Error con evaluación #{i + 1}: {e}")

        driver.quit()
        print("✅ Sincronización de evaluaciones completada.")
