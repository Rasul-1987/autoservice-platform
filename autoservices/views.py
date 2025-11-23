from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Autoservice
from .forms import AutoserviceRegistrationForm, AutoserviceProfileForm


def autoservice_list(request):
    """Список автосервисов - теперь недоступен"""
    messages.error(request, 'Доступ запрещен')
    return redirect('home')


def autoservice_detail(request, autoservice_id):
    """Детальная страница автосервиса - теперь недоступна"""
    messages.error(request, 'Доступ запрещен')
    return redirect('home')


@login_required
def autoservice_dashboard(request):
    """Личный кабинет автосервиса"""
    try:
        autoservice = Autoservice.objects.get(user=request.user)
        return render(request, 'autoservices/dashboard.html', {
            'autoservice': autoservice
        })
    except Autoservice.DoesNotExist:
        messages.error(request, 'Профиль автосервиса не найден')
        return redirect('home')


def autoservice_register(request):
    if request.method == 'POST':
        form = AutoserviceRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация автосервиса прошла успешно!')
            return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
    else:
        form = AutoserviceRegistrationForm()

    return render(request, 'autoservices/register.html', {'form': form})


def autoservice_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                autoservice = Autoservice.objects.get(user=user)
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
            except Autoservice.DoesNotExist:
                messages.error(request, 'Этот пользователь не является автосервисом')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'autoservices/login.html')


def autoservice_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')


@login_required
def verify_autoservice(request):
    """Верификация автосервиса"""
    if request.method == 'POST':
        autoservice = get_object_or_404(Autoservice, user=request.user)
        if autoservice.has_geolocation():
            autoservice.is_verified = True
            autoservice.verification_date = timezone.now()
            autoservice.save()
            messages.success(request, 'Поздравляем! Ваш автосервис прошел верификацию и появился на карте.')
        else:
            messages.error(request, 'Для верификации необходимо указать геолокацию.')

    return redirect('clients:public_repair_requests')


def autoservices_map_data(request):
    """API для получения данных автосервисов для карты"""
    verified_autoservices = Autoservice.objects.filter(
        is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False
    )

    autoservices_data = []
    for autoservice in verified_autoservices:
        autoservices_data.append({
            'id': autoservice.id,
            'name': autoservice.user.username,
            'services': autoservice.cat_branch,
            'phone': autoservice.phone,
            'address': autoservice.location,
            'lat': autoservice.latitude,
            'lon': autoservice.longitude,
            'verification_type': autoservice.get_type_of_verificating_display(),
            'verification_color': autoservice.type_of_verificating
        })

    return JsonResponse(autoservices_data, safe=False)

@login_required
def edit_autoservice_profile(request):
    """Редактирование профиля автосервиса"""
    try:
        autoservice = Autoservice.objects.get(user=request.user)
    except Autoservice.DoesNotExist:
        messages.error(request, 'Профиль автосервиса не найден')
        return redirect('home')

    if request.method == 'POST':
        form = AutoserviceProfileForm(request.POST, instance=autoservice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль автосервиса успешно обновлен!')
            return redirect('autoservices:dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AutoserviceProfileForm(instance=autoservice)

    return render(request, 'autoservices/edit_profile.html', {
        'form': form,
        'autoservice': autoservice
    })