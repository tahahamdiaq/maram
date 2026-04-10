from .models import Notification


def notifications_context(request):
    """Inject notification counts into every template context."""
    unread_count = 0
    critical_count = 0
    recent_notifications = []

    try:
        qs = Notification.objects.filter(status='unread').select_related('project').order_by('-created_at')
        unread_count = qs.count()
        critical_count = qs.filter(priority='critique').count()
        recent_notifications = qs[:8]
    except Exception:
        pass

    return {
        'notif_unread_count': unread_count,
        'notif_critical_count': critical_count,
        'notif_recent': recent_notifications,
    }
