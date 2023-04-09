from pathlib import Path
from os import listdir
import threading
import datetime
from io import StringIO

from django.core.management import call_command
from django.conf import settings
from django.utils import timezone

from .models import Backup, Restore


def backup_wrapper():
    try:
        b = Backup()
        b.save()
    except Exception as e:
        print(str(timezone.now().isoformat()) + "\n")
        print(str(e) + "\n")


def load_backups():
    if settings.DBBACKUP_STORAGE == 'django.core.files.storage.FileSystemStorage':
        files = listdir(settings.DBBACKUP_STORAGE_OPTIONS['location'])
        files.sort(reverse=True)
        backups = []
        for f in files:
            # print("\n\t", f, "\n")
            timestamp = Path(
                settings.DBBACKUP_STORAGE_OPTIONS['location'], f).stat().st_ctime
            timestamp = timezone.make_aware(datetime.datetime.fromtimestamp(timestamp)).isoformat()
            b = Backup(backup_file=f, timestamp=timestamp)
            b_exists = Backup.objects.filter(timestamp=timestamp)
            # print("\t", b, "\n")
            # print("\t", b_exists, "\n")
            if len(b_exists) == 0:
                backups.append(b)
                b.save(loadbackup=True)
            elif len(b_exists):
                if b_exists[0].backup_file == None or "":
                    b_exists[0].backup_file = f
                    b_exists[0].save()
        return backups
    else:
        pass


def restore(backup=None):
    if settings.DBBACKUP_STORAGE == 'django.core.files.storage.FileSystemStorage':
        try:
            f = ""
            if backup is None:
                f = sorted(
                    {
                        file: Path(
                            settings.DBBACKUP_STORAGE_OPTIONS['location'],
                            file).stat().st_ctime
                        for file in listdir(
                            settings.DBBACKUP_STORAGE_OPTIONS['location'])
                    },
                    reverse=True)[0]
                backup = Backup.objects.get(backup_file=f)
            else:
                f = str(backup.backup_file)
            th = threading.Thread(
                target=restore_th, args=[backup, ], daemon=True)
            th.start()
            return [f, None]
        except Exception as e:
            print(str(timezone.now().isoformat()) + "\n")
            print('\trestore errors:\n')
            print('\t' + str(e) + '\n')
            return [f, str(e)]


def restore_th(backup):
    out = StringIO()
    call_command("reset_db", "--no-input", stdout=out)
    error = out.getvalue()
    out.flush()
    call_command(
        "dbrestore",
        "--noinput",
        "-I" +
        str(Path(settings.DBBACKUP_STORAGE_OPTIONS['location'],
                 str(backup.backup_file))),
        stdout=out
    )
    restore = Restore.objects.all().first()
    if not restore:
        restore = Restore()
    restore.timestamp = timezone.now()
    restore.backup = backup.backup_file
    restore.error = error + "\n" + out.getvalue()
    restore.save()
    load_backups()
