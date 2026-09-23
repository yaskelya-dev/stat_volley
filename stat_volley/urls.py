from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('', include('home.urls')),
]
