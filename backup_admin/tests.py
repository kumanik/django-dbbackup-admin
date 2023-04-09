from os import listdir
import time
from pathlib import Path

from django.test import TransactionTestCase
from django.conf import settings

from .models import Backup
from .jobs import backup_wrapper, load_backups, restore


class BakTest(TransactionTestCase):

    def load_baks(self):
        _ = load_backups()
        files = len(listdir(settings.DBBACKUP_STORAGE_OPTIONS["location"]))
        # print("\n\tLOAD_BACKS: N_BACKS: ", len(Backup.objects.all()))
        self.assertEqual(files, len(Backup.objects.all()))

    def bak(self):
        backup_wrapper()
        time.sleep(5)
        bac = Backup.objects.first()
        # print("\n\tBAK: N_BACKS: ", len(Backup.objects.all()))
        # print("\tBAK: N_FILES: ", len(listdir(settings.DBBACKUP_STORAGE_OPTIONS["location"])))
        if bac.backup_file != None or bac.backup_file != "":
            self.assertTrue(Path.is_file(
                Path(settings.DBBACKUP_STORAGE_OPTIONS["location"], str(bac.backup_file))))

    def rstr(self):
        res, _ = restore()
        time.sleep(5)
        # print("\n\tRES: N_BACKS: ", len(Backup.objects.all()))
        self.assertTrue(res != None)

    def delte(self):
        files = len(listdir(settings.DBBACKUP_STORAGE_OPTIONS["location"]))
        backs = Backup.objects.count()
        for b in Backup.objects.all():
            b.delete()
        filesD = len(listdir(settings.DBBACKUP_STORAGE_OPTIONS["location"]))
        # print("\n\tDEL: ", files, "\t", backs, "\t", filesD)
        self.assertEqual(filesD, files-backs)

    def test_backups(self):
        self.load_baks()
        self.bak()
        self.rstr()
        # self.delte()
