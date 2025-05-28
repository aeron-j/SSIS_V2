import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dale2259863',  
    'database': 'student_management_db',  
    'raise_on_warnings': True
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

WINDOW_TITLE = "Student Management System"
WINDOW_SIZE = "1250x500"
THEME_COLOR = "#800000"
ACCENT_COLOR = "#7d6a69"