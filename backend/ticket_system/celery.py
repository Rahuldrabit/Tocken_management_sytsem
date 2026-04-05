import os
from celery import Celery
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')

app = Celery('ticket_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
