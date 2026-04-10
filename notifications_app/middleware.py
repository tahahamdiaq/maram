from django.conf import settings
from django.utils import timezone


class NotificationCheckMiddleware:
    """
    Throttled middleware: runs notification checks at most every
    NOTIFICATION_CHECK_INTERVAL minutes (default 5) per server process.
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
                pass  # Never crash a request due to notification check failure
