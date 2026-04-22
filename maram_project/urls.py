from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from notifications_app.views import custom_login, login_verify

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', custom_login, name='login'),
    path('login/verify/', login_verify, name='login_verify'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('projects.urls')),
    path('notifications/', include('notifications_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
