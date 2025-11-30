from django.db import models
from django.contrib.auth.models import User
from autoservices.models import Autoservice


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(max_length=128, verbose_name='Пароль')
    location = models.CharField(max_length=255, verbose_name='Местоположение')

    # Поля для автомобиля
    car_brand = models.CharField(max_length=100, verbose_name='Марка автомобиля', blank=True)
    car_model = models.CharField(max_length=100, verbose_name='Модель автомобиля', blank=True)
    car_year = models.PositiveIntegerField(verbose_name='Год выпуска', null=True, blank=True)
    car_vin = models.CharField(max_length=17, verbose_name='VIN код', blank=True)
    car_license_plate = models.CharField(max_length=15, verbose_name='Госномер', blank=True)




    def __str__(self):
        return f"Клиент: {self.user.username}"

    def get_car_info(self):
        info_parts = []
        if self.car_brand:
            info_parts.append(self.car_brand)
        if self.car_model:
            info_parts.append(self.car_model)
        if self.car_year:
            info_parts.append(str(self.car_year))
        if self.car_license_plate:
            info_parts.append(f"({self.car_license_plate})")
        return " ".join(info_parts) if info_parts else "Не указан"





class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]

    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='repair_requests')
    # Убираем выбор автосервиса, заявка публичная
    title = models.CharField(max_length=200, verbose_name='Заголовок заявки')
    description = models.TextField(verbose_name='Описание проблемы')
    desired_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                        verbose_name='Желаемая стоимость')
    photo = models.ImageField(upload_to='repair_photos/', null=True, blank=True, verbose_name='Фото проблемы')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"Заявка #{self.id} - {self.title}"


    def get_photo_url(self):
        """Возвращает URL фотографии или None если фото нет"""
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return None


class Meta:
    verbose_name = 'Заявка на ремонт'
    verbose_name_plural = 'Заявки на ремонт'
    ordering = ['-created_at']