from .models import ChatRoom, Message


def chat_notifications(request):
    """Контекстный процессор для отображения количества непрочитанных сообщений"""
    if request.user.is_authenticated:
        unread_count = 0

        if hasattr(request.user, 'client'):
            # Для клиента: получаем все чаты клиента
            chat_rooms = ChatRoom.objects.filter(client=request.user.client)
            for chat in chat_rooms:
                unread_count += Message.objects.filter(
                    chat_room=chat,
                    is_read=False
                ).exclude(sender=request.user).count()

        elif hasattr(request.user, 'autoservice'):
            # Для автосервиса: получаем все чаты автосервиса
            chat_rooms = ChatRoom.objects.filter(autoservice=request.user.autoservice)
            for chat in chat_rooms:
                unread_count += Message.objects.filter(
                    chat_room=chat,
                    is_read=False
                ).exclude(sender=request.user).count()

        return {
            'unread_chat_count': unread_count
        }

    return {'unread_chat_count': 0}