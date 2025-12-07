from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import ChatRoom, Message
from clients.models import Client, RepairRequest
from autoservices.models import Autoservice


@login_required
def start_chat(request, client_id=None, repair_request_id=None):
    """Начать новый чат или перейти к существующему"""
    try:
        # Получаем текущего пользователя (автосервис)
        autoservice = Autoservice.objects.get(user=request.user)

        # Получаем клиента
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            repair_request = None
        elif repair_request_id:
            repair_request = get_object_or_404(RepairRequest, id=repair_request_id)
            client = repair_request.client
        else:
            messages.error(request, 'Не указан клиент или заявка')
            return redirect('clients:public_repair_requests')

        # Проверяем, есть ли уже чат
        chat_room = ChatRoom.objects.filter(
            client=client,
            autoservice=autoservice,
            repair_request=repair_request
        ).first()

        # Если чата нет - создаем
        if not chat_room:
            chat_room = ChatRoom.objects.create(
                client=client,
                autoservice=autoservice,
                repair_request=repair_request
            )

        return redirect('chat:chat_detail', chat_id=chat_room.id)

    except Autoservice.DoesNotExist:
        messages.error(request, 'Доступно только для автосервисов')
        return redirect('clients:public_repair_requests')


@login_required
def chat_list(request):
    """Список чатов пользователя"""
    user = request.user

    if hasattr(user, 'client'):
        # Для клиента
        chat_rooms = ChatRoom.objects.filter(client=user.client).select_related(
            'autoservice', 'autoservice__user', 'repair_request'
        )
        user_type = 'client'
    elif hasattr(user, 'autoservice'):
        # Для автосервиса
        chat_rooms = ChatRoom.objects.filter(autoservice=user.autoservice).select_related(
            'client', 'client__user', 'repair_request'
        )
        user_type = 'autoservice'
    else:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    # Подсчитываем непрочитанные сообщения для каждого чата
    for chat in chat_rooms:
        chat.unread_count = chat.get_unread_count(user)

    # Общее количество непрочитанных сообщений
    total_unread = sum(chat.unread_count for chat in chat_rooms)

    return render(request, 'chat/list.html', {
        'chat_rooms': chat_rooms,
        'user_type': user_type,
        'total_unread': total_unread
    })


@login_required
def chat_detail(request, chat_id):
    """Детальная страница чата"""
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

    # Проверяем доступ к чату
    user = request.user
    if hasattr(user, 'client'):
        if chat_room.client.user != user:
            messages.error(request, 'Доступ запрещен')
            return redirect('chat:chat_list')
    elif hasattr(user, 'autoservice'):
        if chat_room.autoservice.user != user:
            messages.error(request, 'Доступ запрещен')
            return redirect('chat:chat_list')
    else:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    # Получаем сообщения
    messages_list = Message.objects.filter(chat_room=chat_room).select_related('sender')

    # Помечаем сообщения как прочитанные
    Message.objects.filter(
        chat_room=chat_room,
        is_read=False
    ).exclude(sender=user).update(is_read=True)

    # Определяем собеседника и тип пользователя
    if hasattr(user, 'client'):
        interlocutor = chat_room.autoservice.user
        user_type = 'client'
    else:
        interlocutor = chat_room.client.user
        user_type = 'autoservice'

    # Получаем последний ID сообщения
    last_message_id = messages_list.last().id if messages_list else 0

    return render(request, 'chat/detail.html', {
        'chat_room': chat_room,
        'messages': messages_list,
        'interlocutor': interlocutor,
        'last_message_id': last_message_id,
        'user_type': user_type  # Добавляем тип пользователя в контекст
    })

@login_required
def send_message(request, chat_id):
    """Отправка сообщения (AJAX)"""
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        content = request.POST.get('content', '').strip()

        if content:
            # Проверяем доступ
            user = request.user
            if hasattr(user, 'client'):
                if chat_room.client.user != user:
                    return JsonResponse({'error': 'Доступ запрещен'}, status=403)
            elif hasattr(user, 'autoservice'):
                if chat_room.autoservice.user != user:
                    return JsonResponse({'error': 'Доступ запрещен'}, status=403)
            else:
                return JsonResponse({'error': 'Доступ запрещен'}, status=403)

            # Создаем сообщение
            message = Message.objects.create(
                chat_room=chat_room,
                sender=user,
                content=content
            )

            # Обновляем время последнего сообщения в чате
            chat_room.updated_at = timezone.now()
            chat_room.save()

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'content': content
            })

    return JsonResponse({'error': 'Ошибка отправки'}, status=400)


@login_required
def get_new_messages(request, chat_id, last_message_id):
    """Получение новых сообщений (AJAX)"""
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

    # Проверяем доступ
    user = request.user
    if hasattr(user, 'client'):
        if chat_room.client.user != user:
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    elif hasattr(user, 'autoservice'):
        if chat_room.autoservice.user != user:
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    # Получаем новые сообщения
    new_messages = Message.objects.filter(
        chat_room=chat_room,
        id__gt=last_message_id
    ).select_related('sender').order_by('timestamp')

    # Помечаем как прочитанные
    new_messages.exclude(sender=user).update(is_read=True)

    messages_data = []
    for msg in new_messages:
        # Определяем тип отправителя
        is_client = hasattr(msg.sender, 'client')

        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'is_client': is_client,  # Передаем флаг, является ли отправитель клиентом
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_own': msg.sender == user
        })

    # Возвращаем также общее количество непрочитанных сообщений
    total_unread = 0
    if hasattr(user, 'client'):
        chat_rooms = ChatRoom.objects.filter(client=user.client)
    elif hasattr(user, 'autoservice'):
        chat_rooms = ChatRoom.objects.filter(autoservice=user.autoservice)

    for chat in chat_rooms:
        total_unread += chat.get_unread_count(user)

    return JsonResponse({
        'messages': messages_data,
        'count': len(messages_data),
        'total_unread': total_unread
    })