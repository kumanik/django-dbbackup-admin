from django.shortcuts import render
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from .models import Backup
from . import jobs


@user_passes_test(lambda user: user.is_superuser)
def restore_backup(request, pk=None):
    if pk is not None:
        backup = Backup.objects.get(id=pk)
    else:
        backup = None
    context = {'backup': backup, 'restored': False}
    if request.method == 'POST':
        f, err = jobs.restore(backup)
        if err is None:
            context['restored'] = True
        context["errors"] = err
        context['backup_file'] = f
    return render(request, 'admin/backup_admin/backup/restore_confirm.html', context)


@user_passes_test(lambda user: user.is_superuser)
def get_backups(request):
    backups = jobs.load_backups()
    context = {'backups': backups}
    context['len'] = len(backups)
    return render(request, 'admin/backup_admin/backup/load_backups.html', context)


def create_backup(request):
    jobs.backup_wrapper()
    return redirect(reverse('admin:backup_admin_backup_changelist'))

