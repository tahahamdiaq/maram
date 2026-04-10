from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('projets/nouveau/', views.project_create, name='project_create'),
    path('projets/<int:pk>/', views.project_detail, name='project_detail'),
    path('projets/<int:pk>/modifier/', views.project_edit, name='project_edit'),
    path('projets/<int:pk>/supprimer/', views.project_delete, name='project_delete'),

    # Factures
    path('projets/<int:project_pk>/facture/<int:invoice_number>/', views.invoice_edit, name='invoice_edit'),

    # Observations
    path('projets/<int:project_pk>/observations/ajouter/', views.observation_add, name='observation_add'),
    path('observations/<int:pk>/supprimer/', views.observation_delete, name='observation_delete'),

    # Engineers
    path('ingenieurs/', views.engineer_list, name='engineer_list'),
    path('ingenieurs/nouveau/', views.engineer_create, name='engineer_create'),
    path('ingenieurs/<int:pk>/modifier/', views.engineer_edit, name='engineer_edit'),

    # API
    path('api/notifications/count/', views.notification_count_api, name='notification_count_api'),
]
