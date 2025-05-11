from django.apps import AppConfig
import threading
from .views import mqtt_client

class SensorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensors'

    def ready(self):
        thread = threading.Thread(target=mqtt_client.loop_forever)
        thread.daemon = True
        thread.start()
