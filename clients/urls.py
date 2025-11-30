from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('dashboard/', views.client_dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # НОВЫЙ ПУТЬ
    path('register/', views.client_register, name='register'),
    path('login/', views.client_login, name='login'),
    path('logout/', views.client_logout, name='logout'),
    path('map/', views.autoservices_map, name='autoservices_map'),
    path('repair-requests/', views.repair_requests_list, name='repair_requests'),
    path('repair-requests/create/', views.create_repair_request, name='create_repair_request'),
    path('repair-requests/<int:request_id>/', views.repair_request_detail, name='repair_request_detail'),
    path('public-requests/', views.public_repair_requests, name='public_repair_requests'),
    path('<int:client_id>/', views.client_detail, name='client_detail'),
    path('repair-requests/<int:request_id>/delete/', views.delete_repair_request, name='delete_repair_request'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)