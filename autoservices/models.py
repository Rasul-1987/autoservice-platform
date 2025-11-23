from django.db import models
from django.contrib.auth.models import User


class Autoservice(models.Model):
    # Выборы для типа верификации
    VERIFICATION_TYPES = [
        ('basic', 'Базовая'),
        ('premium', 'Премиум'),
        ('verified', 'Верифицированный'),
    ]

    # Связь с пользователем Django (для логина)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Поля из вашей диаграммы
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(unique=True, verbose_name='Email')
    location = models.CharField(max_length=255, verbose_name='Местоположение')
    password = models.CharField(max_length=128, verbose_name='Пароль')  # На самом деле будет в User

    # Геолокация
    latitude = models.FloatField(verbose_name='Широта', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True, blank=True)


    type_of_verificating = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPES,
        default='basic',
        verbose_name='Тип верификации'
    )

    cat_branch = models.CharField(max_length=100, verbose_name='Категория услуг')
    is_verified = models.BooleanField(default=False, verbose_name='Прошел верификацию')
    verification_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата верификации')


    def __str__(self):
        return f"Автосервис: {self.user.username}"

    def has_geolocation(self):
        return self.latitude is not None and self.longitude is not None

    def get_active_requests_count(self):
        return self.repair_requests.filter(status__in=['new', 'in_progress']).count()

    # Методы из диаграммы
    def topo_cartoff(self):
        """Управление каталогом услуг"""
        # Здесь будет логика работы с каталогом
        pass



    def sulfonization(self):
        """Поддержка (вероятно опечатка в диаграмме)"""
        # Логика обращения в поддержку
        pass



    def registration(self):
        """Регистрация"""
        # Логика регистрации
        pass



    def verification(self):
        """Верификация"""
        # Логика верификации
        pass
