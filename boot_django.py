import os
import django
from django.conf import settings
from pathlib import Path

BASE_DIR = Path(Path(__file__).parent, "backup_admin")

def backup_filename(databasename, servername, datetime, extension, content_type):
    return str(datetime) + "." + extension

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

            # "django.contrib.admin",
            # "django.contrib.auth",

            "dbbackup",
            "django_extensions",
        ),

        MIDDLEWARE = [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],

        TIME_ZONE="UTC",
        USE_TZ=True,

        # django-dbbackup
        DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage',
        DBBACKUP_STORAGE_OPTIONS = {'location': Path(BASE_DIR.parent, "backs")},
        DBBACKUP_FILENAME_TEMPLATE = backup_filename,
        EXCLUDE = ["backup_admin_backup",],

    )

    django.setup()
