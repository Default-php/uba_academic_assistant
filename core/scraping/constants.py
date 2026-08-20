# Constantes de scraping del campus virtual UBA (Moodle).
# Los selectores CSS están atados al DOM del campus en vivo y pueden
# romperse si el campus cambia. Verificar contra el sitio antes de asumir
# que el scraping funciona.

# URLs
BASE_URL   = "https://pregrado.campusvirtualuba.net.ve/trimestre/"
LOGIN_URL  = BASE_URL + "login/index.php"
COURSES_URL = BASE_URL + "my/courses.php"

# Selectores CSS
COURSE_LINK_SELECTOR = "a.coursename[href*='course/view.php?id=']"
ACTIVITY_LINK_SELECTOR = "li.activity.assign a.aalink"
INSTANCENAME_CLASS = "instancename"
CONTENT_BOX_SELECTOR = ".box.generalbox"
TEACHER_LINK_SELECTOR = "a.messageteacher_link span"

# Campos del formulario de login
USERNAME_FIELD_ID = "username"
PASSWORD_FIELD_ID = "password"

# Números romanos usados para el trimestre
ROMAN_NUMS = {
    'I': 1,   'II': 2,  'III': 3, 'IV': 4,
    'V': 5,   'VI': 6,  'VII': 7, 'VIII': 8,
    'IX': 9,  'X': 10,  'XI': 11, 'XII': 12
}
