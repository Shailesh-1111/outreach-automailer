import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
PROCESSING_QUEUE_DIR = os.getenv("PROCESSING_QUEUE_DIR", "processing_queue")
PROCESSED_FILE = os.getenv("PROCESSED_FILE", os.path.join("history", "processed_records.xlsx"))
