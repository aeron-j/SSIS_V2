import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dale2259863',  # Change this to your MySQL password
    'database': 'student_management_db',  # Added missing database name
    'raise_on_warnings': True
}

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# GUI settings
WINDOW_TITLE = "Student Management System"
WINDOW_SIZE = "1250x500"
THEME_COLOR = "#800000"
ACCENT_COLOR = "#7d6a69"