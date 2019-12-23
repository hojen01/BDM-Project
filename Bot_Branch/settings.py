import os

# stupid path def get absolute root dir

PROJECT_ROOT = os.path.abspath((os.path.dirname(__file__)))
DB_FILE = os.path.join(PROJECT_ROOT, "database.db")  # PASS THIS TO DB SO IT DOES NOT GET CONFUSED
LOG_FILE = os.path.join(PROJECT_ROOT, "events.log")
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "templates/")