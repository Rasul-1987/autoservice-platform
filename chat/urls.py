from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('start/<int:client_id>/', views.start_chat, name='start_chat'),
    path('start/from-request/<int:repair_request_id>/', views.start_chat, name='start_chat_from_request'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('<int:chat_id>/send/', views.send_message, name='send_message'),
    path('<int:chat_id>/get-new/<int:last_message_id>/', views.get_new_messages, name='get_new_messages'),
]