import os
import threading

from django.apps import AppConfig


class AptDjangoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "APT_Django"

    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            return

        print("Autorefresh starting...")
        from .background import full_update_and_refresh
        thread = threading.Thread(target=full_update_and_refresh, daemon=True)
        thread.start()
        print("Autorefresh active.")
