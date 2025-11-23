from django.contrib import admin
from .models import Client, RepairRequest


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email', 'location', 'car_info_display')
    search_fields = ('user__username', 'phone', 'email', 'car_brand', 'car_model')
    list_filter = ('car_brand', 'car_year')

    def car_info_display(self, obj):
        return obj.get_car_info()

    car_info_display.short_description = 'Автомобиль'


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'client', 'status', 'created_at', 'desired_price', 'has_photo')
    list_filter = ('status', 'created_at')  # Убрали 'autoservice'
    search_fields = ('title', 'client__user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')

    def has_photo(self, obj):
        return bool(obj.photo)

    has_photo.boolean = True
    has_photo.short_description = 'Есть фото'