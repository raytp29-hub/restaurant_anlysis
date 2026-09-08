import os
from pathlib import Path
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env nella root del progetto
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'restaurants'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}
