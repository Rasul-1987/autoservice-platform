from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from autoservices.models import Autoservice
from .models import Client, RepairRequest
from .forms import ClientRegistrationForm, RepairRequestForm, ClientProfileForm


def client_list(request):
    """Список клиентов - теперь недоступен"""
    messages.error(request, 'Доступ запрещен')
    return redirect('home')


def client_detail(request, client_id):
    """Детальная страница клиента - теперь недоступна"""
    messages.error(request, 'Доступ запрещен')
    return redirect('home')


@login_required
def client_dashboard(request):
    """Личный кабинет клиента"""
    try:
        client = Client.objects.get(user=request.user)

        # Получаем последние заявки клиента
        recent_requests = RepairRequest.objects.filter(client=client).order_by('-created_at')[:5]

        return render(request, 'clients/dashboard.html', {
            'client': client,
            'recent_requests': recent_requests
        })
    except Client.DoesNotExist:
        messages.error(request, 'Профиль клиента не найден')
        return redirect('home')


def client_register(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientRegistrationForm()

    return render(request, 'clients/register.html', {'form': form})


def client_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                client = Client.objects.get(user=user)
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
            except Client.DoesNotExist:
                # Проверяем, может это автосервис
                try:
                    autoservice = Autoservice.objects.get(user=user)
                    login(request, user)
                    messages.success(request, f'Добро пожаловать, {username}!')
                    return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
                except Autoservice.DoesNotExist:
                    messages.error(request, 'Пользователь не найден')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'clients/login.html')


def client_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')


def autoservices_map(request):
    """Карта автосервисов - доступна всем"""
    return render(request, 'clients/autoservices_map.html')


@login_required
def create_repair_request(request):
    """Создание заявки на ремонт"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    if request.method == 'POST':
        form = RepairRequestForm(request.POST, request.FILES)
        if form.is_valid():
            repair_request = form.save(commit=False)
            repair_request.client = client
            repair_request.save()
            messages.success(request, 'Заявка успешно создана и опубликована!')
            return redirect('clients:public_repair_requests')  # Редирект на публичные заявки
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RepairRequestForm()

    return render(request, 'clients/create_repair_request.html', {
        'form': form,
        'client': client
    })


@login_required
def repair_requests_list(request):
    """Список заявок клиента (только его заявки)"""
    try:
        client = Client.objects.get(user=request.user)
        requests_list = RepairRequest.objects.filter(client=client).order_by('-created_at')

        # Пагинация - 15 заявок на страницу
        paginator = Paginator(requests_list, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'clients/repair_requests.html', {
            'client': client,
            'page_obj': page_obj,
            'requests': page_obj
        })
    except Client.DoesNotExist:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')


@login_required
def repair_request_detail(request, request_id):
    """Детальная страница заявки"""
    try:
        client = Client.objects.get(user=request.user)
        repair_request = get_object_or_404(RepairRequest, id=request_id, client=client)

        return render(request, 'clients/repair_request_detail.html', {
            'client': client,
            'repair_request': repair_request
        })
    except Client.DoesNotExist:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')


def public_repair_requests(request):
    """Публичные заявки для всех"""
    repair_requests = RepairRequest.objects.filter(status='new').order_by('-created_at')
    return render(request, 'clients/public_repair_requests.html', {
        'repair_requests': repair_requests
    })


@login_required
def edit_profile(request):
    """Редактирование профиля клиента"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, 'Профиль клиента не найден')
        return redirect('home')

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('clients:dashboard')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ClientProfileForm(instance=client)

    return render(request, 'clients/edit_profile.html', {
        'form': form,
        'client': client
    })