from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_client', 'get_autoservice', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['client__user__username', 'autoservice__user__username']

    def get_client(self, obj):
        return f"👤 {obj.client.user.username}"

    get_client.short_description = 'Клиент'
    get_client.admin_order_field = 'client__user__username'

    def get_autoservice(self, obj):
        return f"🏢 {obj.autoservice.user.username}"

    get_autoservice.short_description = 'Автосервис'
    get_autoservice.admin_order_field = 'autoservice__user__username'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_chat', 'get_sender', 'short_content', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['content', 'sender__username']

    def get_chat(self, obj):
        return f"💬 Чат #{obj.chat_room.id}"

    get_chat.short_description = 'Чат'
    get_chat.admin_order_field = 'chat_room__id'

    def get_sender(self, obj):
        return obj.get_sender_display_name()

    get_sender.short_description = 'Отправитель'
    get_sender.admin_order_field = 'sender__username'

    def short_content(self, obj):
        if len(obj.content) > 30:
            return f"{obj.content[:30]}..."
        return obj.content

    short_content.short_description = 'Сообщение'