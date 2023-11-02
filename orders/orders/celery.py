import os
from celery import Celery

# Установите Django settings module для программы 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

app = Celery('orders')

# Загрузите модули задач из всех зарегистрированных конфигураций приложений Django.
app.autodiscover_tasks()
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')