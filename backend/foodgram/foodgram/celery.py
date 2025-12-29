import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

app = Celery("foodgram")
app.config_from_object("foodgram.celeryconfig")
app.autodiscover_tasks()
