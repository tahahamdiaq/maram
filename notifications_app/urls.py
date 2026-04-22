from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/lue/', views.notification_mark_read, name='notification_mark_read'),
    path('<int:pk>/traitee/', views.notification_mark_processed, name='notification_mark_processed'),
    path('tout-lire/', views.mark_all_read, name='mark_all_read'),
    path('parametres/', views.notification_settings, name='notification_settings'),
    path('api/', views.notification_api, name='notification_api'),
    path('emails/', views.email_log_list, name='email_log_list'),
    path('acces/', views.access_log_list, name='access_log_list'),
]
