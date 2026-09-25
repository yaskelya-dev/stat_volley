from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by")
    list_filter = ("created_by",)
    search_fields = ("name", "created_by__username")
    readonly_fields = ("created_by",)

    def save_model(self, request, obj, form, change):
        """Автоматически подставляет текущего пользователя в поле created_by"""
        if not change or not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
