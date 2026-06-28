import threading

from django.conf import settings
from django.utils import timezone


def _send_emails_background():
    try:
        from .email_service import send_pending_emails
        send_pending_emails()
    except Exception:
        pass


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


class NotificationCheckMiddleware:
    """
    Per-request middleware that:
      1. Enforces a single active session per user (kicks out stale sessions).
      2. Periodically runs notification checks and sends pending emails.
    """
    _last_check = None

    def __init__(self, get_response):
        self.get_response = get_response
        self.interval_minutes = getattr(settings, 'NOTIFICATION_CHECK_INTERVAL', 5)

    def __call__(self, request):
        self._maybe_check()
        return self.get_response(request)

    def _maybe_check(self):
        now = timezone.now()
        cls = NotificationCheckMiddleware
        if cls._last_check is None or (now - cls._last_check).total_seconds() >= self.interval_minutes * 60:
            cls._last_check = now
            try:
                from .services import check_all_notifications
                check_all_notifications()
            except Exception:
                pass
            threading.Thread(target=_send_emails_background, daemon=True).start()
