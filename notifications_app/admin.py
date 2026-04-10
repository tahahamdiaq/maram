from django.contrib import admin
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['project', 'notification_type', 'priority', 'status', 'email_sent', 'created_at']
    list_filter = ['priority', 'status', 'notification_type', 'email_sent']
    search_fields = ['project__name', 'message']
    readonly_fields = ['created_at', 'updated_at', 'email_sent_at']
    ordering = ['-created_at']


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'channel', 'send_to_project_engineers', 'is_active']
    list_filter = ['channel', 'is_active']
