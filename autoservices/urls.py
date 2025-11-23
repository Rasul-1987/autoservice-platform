from django.urls import path
from . import views

app_name = 'autoservices'

urlpatterns = [
    path('', views.autoservice_list, name='autoservice_list'),
    path('dashboard/', views.autoservice_dashboard, name='dashboard'),
    path('profile/edit/', views.edit_autoservice_profile, name='edit_profile'),  # НОВЫЙ ПУТЬ
    path('register/', views.autoservice_register, name='register'),
    path('login/', views.autoservice_login, name='login'),
    path('logout/', views.autoservice_logout, name='logout'),
    path('verify/', views.verify_autoservice, name='verify'),
    path('map-data/', views.autoservices_map_data, name='map_data'),
    path('<int:autoservice_id>/', views.autoservice_detail, name='autoservice_detail'),
]