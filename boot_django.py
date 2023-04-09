import os
import django
from django.conf import settings
from pathlib import Path
import environ


env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(Path(__file__).parent, "backup_admin")


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,

        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
            }
        },

        INSTALLED_APPS=(
            "backup_admin",
            "dbbackup",
            "django_extensions",
        ),

        TIME_ZONE="UTC",
        USE_TZ=True,

        # django-dbbackup
        DBBACKUP_STORAGE=env("DBBACKUP_STORAGE"),
        DBBACKUP_STORAGE_OPTIONS={'location': env("DBBACKUP_STORAGE_OPTIONS")},
        EXCLUDE=["backup_admin_backup", ]
    )

    django.setup()
