from django.urls import path

from . import views

urlpatterns = [
    path(r'restore/', views.restore_backup, name="restore_last_backup"),
    path(r'restore/<pk>', views.restore_backup, name="restore_backup"),
    path(r'loadbackups', views.get_backups, name="load_backups"),
    path(r'newbackup', views.create_backup, name="newbackup"),
]
