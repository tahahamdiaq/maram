"""
Security: access audit logging.
Signal handlers are connected in NotificationsAppConfig.ready().
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    from .models import UserSession, AccessLog

    new_key = request.session.session_key
    UserSession.objects.update_or_create(user=user, defaults={'session_key': new_key})

    AccessLog.objects.create(
        user=user,
        username=user.username,
        event=AccessLog.EVENT_LOGIN,
        ip_address=_get_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )


@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    from .models import UserSession, AccessLog

    if not user:
        return
    UserSession.objects.filter(user=user).delete()
    AccessLog.objects.create(
        user=user,
        username=user.username,
        event=AccessLog.EVENT_LOGOUT,
        ip_address=_get_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
