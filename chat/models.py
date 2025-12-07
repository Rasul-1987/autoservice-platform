from django.db import models
from django.contrib.auth.models import User
from clients.models import Client, RepairRequest
from autoservices.models import Autoservice


class ChatRoom(models.Model):
    """Комната чата между клиентом и автосервисом"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='chat_rooms')
    autoservice = models.ForeignKey(Autoservice, on_delete=models.CASCADE, related_name='chat_rooms')
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['client', 'autoservice', 'repair_request']
        ordering = ['-updated_at']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return "\u200B"  # Zero-width space (невидимый символ)

    def get_unread_count(self, user):
        """Получить количество непрочитанных сообщений для пользователя"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Сообщение в чате"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return "\u200B"  # Zero-width space (невидимый символ)

    def get_sender_display_name(self):
        """Получить отображаемое имя отправителя в зависимости от типа пользователя"""
        try:
            if hasattr(self.sender, 'client'):
                return f"👤 {self.sender.username}"
            elif hasattr(self.sender, 'autoservice'):
                return f"🏢 {self.sender.username}"
            else:
                return self.sender.username
        except:
            return self.sender.username

    def is_sender_client(self):
        """Проверка, является ли отправитель клиентом"""
        return hasattr(self.sender, 'client')

    def is_sender_autoservice(self):
        """Проверка, является ли отправитель автосервисом"""
        return hasattr(self.sender, 'autoservice')