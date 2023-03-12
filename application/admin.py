from django.contrib import admin

from application.models import Computer, Profile, Software

# Register your models here.
admin.site.register(Profile)
admin.site.register(Software)


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__last_name', 'user__first_name', 'user__last_name']
