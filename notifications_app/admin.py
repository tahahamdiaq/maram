from django.contrib import admin
from .models import Notification, NotificationSettings, EmailLog, AccessLog, UserSession


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


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['sent_at', 'success', 'subject', 'recipients', 'notification']
    list_filter = ['success']
    search_fields = ['subject', 'recipients', 'notification__project__name']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'event', 'ip_address', 'user_agent']
    list_filter = ['event']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
