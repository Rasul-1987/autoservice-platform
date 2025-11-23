from django.contrib import admin
from .models import Autoservice


@admin.register(Autoservice)
class AutoserviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'cat_branch', 'type_of_verificating', 'is_verified', 'has_geolocation_display')
    list_filter = ('type_of_verificating', 'cat_branch', 'is_verified')
    search_fields = ('user__username', 'phone', 'email')

    def has_geolocation_display(self, obj):
        return obj.has_geolocation()

    has_geolocation_display.boolean = True
    has_geolocation_display.short_description = 'Есть геолокация'