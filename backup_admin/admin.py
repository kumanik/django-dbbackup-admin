from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Backup, Restore


class BackupAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp', 'backup_file', 'error')
    ordering = ('-timestamp',)
    list_display = ['timestamp', 'restore_action']

    def save_model(self, request, obj, form, change) -> None:
        b = Backup()
        return super().save_model(request, obj, form, change)

    def restore_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Restore</a>',
            reverse('restore_backup', args=[obj.id])
        )
    restore_action.short_description = "Restore The Backup"

    def has_error(self, obj) -> bool:
        return True if len(obj.error) != 0 else False
    has_error.short_description = "Errors in Backup"

    def has_add_permission(self, *args) -> bool:
        return True

    def has_change_permission(self, *args) -> bool:
        return False


class RestoreAdmin(admin.ModelAdmin):
    # readonly_fields = ()
    ordering = ('-timestamp',)

    def has_error(self, obj) -> bool:
        return True if (obj.error is not None) or (len(obj.error) != 0) else False
    has_error.short_description = "Errors in Backup"

    def has_add_permission(self, *args) -> bool:
        return False

    def has_change_permission(self, *args) -> bool:
        return False

    def has_delete_permission(self, *args) -> bool:
        return False


admin.site.register(Backup, BackupAdmin)
admin.site.register(Restore, RestoreAdmin)
