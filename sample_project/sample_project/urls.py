from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("backup_admin/", include("backup_admin.urls"))
]
