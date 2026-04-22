from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('projets/nouveau/', views.project_create, name='project_create'),
    path('projets/<int:pk>/', views.project_detail, name='project_detail'),
    path('projets/<int:pk>/modifier/', views.project_edit, name='project_edit'),
    path('projets/<int:pk>/supprimer/', views.project_delete, name='project_delete'),
    path('projets/<int:pk>/supprimer/verifier/', views.project_delete_verify, name='project_delete_verify'),

    # Factures
    path('projets/<int:project_pk>/facture/<int:invoice_number>/', views.invoice_edit, name='invoice_edit'),

    # Observations
    path('projets/<int:project_pk>/observations/ajouter/', views.observation_add, name='observation_add'),
    path('observations/<int:pk>/supprimer/', views.observation_delete, name='observation_delete'),

    # Engineers
    path('ingenieurs/', views.engineer_list, name='engineer_list'),
    path('ingenieurs/nouveau/', views.engineer_create, name='engineer_create'),
    path('ingenieurs/<int:pk>/modifier/', views.engineer_edit, name='engineer_edit'),

    # Expertises
    path('expertises/', views.expertise_list, name='expertise_list'),
    path('expertises/nouvelle/', views.expertise_create, name='expertise_create'),
    path('expertises/<int:pk>/', views.expertise_detail, name='expertise_detail'),
    path('expertises/<int:pk>/modifier/', views.expertise_edit, name='expertise_edit'),
    path('expertises/<int:pk>/supprimer/', views.expertise_delete, name='expertise_delete'),
    path('expertises/<int:expertise_pk>/facture/', views.expertise_invoice_edit, name='expertise_invoice_edit'),
    path('expertises/<int:expertise_pk>/observations/ajouter/', views.expertise_observation_add, name='expertise_observation_add'),
    path('expertises/observations/<int:pk>/supprimer/', views.expertise_observation_delete, name='expertise_observation_delete'),

    # API
    path('api/notifications/count/', views.notification_count_api, name='notification_count_api'),
]
