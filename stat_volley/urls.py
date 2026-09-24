from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('', include('home.urls')),
    path('score/', include('score.urls')),
    path('users/', include('users.urls')),
]
