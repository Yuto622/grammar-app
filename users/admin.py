from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
         ),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
