import datetime
from os import listdir, remove
import threading
from pathlib import Path
from io import StringIO

from django.core.management import call_command
from django.conf import settings
from django.db import models
from django.utils import timezone


class Backup(models.Model):
    timestamp = models.DateTimeField(unique=True)
    backup_file = models.FileField(blank=True)
    error = models.CharField(max_length=255, blank=True)

    def __str__(self):
        time = timezone.make_aware(
            datetime.datetime.fromisoformat(self.timestamp))
        return f"Backup on {str(time.date())} at {str(time.time()).split('.')[0]}"

    def backup(self):
        try:
            out = StringIO()
            call_command("dbbackup", stdout=out)
            self.error = out.getvalue()
            if settings.DBBACKUP_STORAGE == \
                    'django.core.files.storage.FileSystemStorage':
                self.backup_file = sorted(
                    {
                        file: Path(
                            settings.DBBACKUP_STORAGE_OPTIONS['location'],
                            file).stat().st_mtime
                        for file in listdir(
                            settings.DBBACKUP_STORAGE_OPTIONS['location'])
                    },
                    reverse=True)[0]
                self.timestamp = timezone.make_aware(datetime.datetime.fromtimestamp(
                    Path(settings.DBBACKUP_STORAGE_OPTIONS['location'],
                         str(self.backup_file)).stat().st_ctime)).isoformat()
            else:
                pass
            super(Backup, self).save()
        except Exception as e:
            print(e)
            self.error = str(e)
        # finally:
        #     # self.save()

    def save(self, loadbackup=False, *args, **kwargs):
        try:
            if not self.timestamp:
                self.timestamp = timezone.now()
            if not self.backup_file:
                th = threading.Thread(target=self.backup, daemon=True)
                th.start()
                self.backup_file = ""
        except Exception as e:
            print(str(timezone.now().isoformat()) + "\n")
            print('\tcreate_backup errors: ' + str(e) + "\n")
        if loadbackup:
            super(Backup, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if settings.DBBACKUP_STORAGE == 'django.core.files.storage.FileSystemStorage':
            try:
                if Path.is_file(Path(
                        settings.DBBACKUP_STORAGE_OPTIONS['location'],
                        str(self.backup_file))):
                    remove(Path(
                        settings.DBBACKUP_STORAGE_OPTIONS['location'],
                        str(self.backup_file)))
            except Exception as e:
                print(e)
        return super().delete(*args, **kwargs)


class Restore(models.Model):
    timestamp = models.DateTimeField()
    backup = models.CharField(max_length=255)
    error = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Restore at {str(self.timestamp.date())} on \
            {str(self.timestamp.time()).split('.')[0]} from file {self.backup}"

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)
