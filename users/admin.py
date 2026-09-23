from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ('-date_joined',)

    # 2. Поля, которые будут отображаться в общей таблице
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')

    # 3. Поля, которые будут ссылками на страницу редактирования
    list_display_links = ('username', 'email')

    # 4. Боковые фильтры для быстрого поиска
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')

    # 5. Поля, по которым работает строка поиска (вверху страницы)
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # 6. Настройка кастомных полей внутри самой формы редактирования пользователя
    # Позволяет сгруппировать поля по блокам (Fieldsets)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'bio', 'avatar'), # Ваши кастомные поля из models.py
        }),
    )

    # Настройка полей для формы создания нового пользователя (в админке)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('birth_date', 'bio', 'avatar'),
        }),
    )
