"""
Email notification sender.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Notification, NotificationSettings


def get_recipients_for_notification(notification):
    """Collect all email addresses to notify for a given notification."""
    emails = set()
    project = notification.project

    try:
        cfg = NotificationSettings.objects.get(notification_type=notification.notification_type)
    except NotificationSettings.DoesNotExist:
        cfg = None

    if cfg:
        if cfg.send_to_project_engineers:
            for eng in project.engineers.all():
                if eng.email:
                    emails.add(eng.email)
        if cfg.send_to_admin:
            from django.contrib.auth.models import User
            for user in User.objects.filter(is_staff=True):
                if user.email:
                    emails.add(user.email)
        for extra in cfg.get_extra_email_list():
            emails.add(extra)
    else:
        # Default: send to project engineers
        for eng in project.engineers.all():
            if eng.email:
                emails.add(eng.email)

    return list(emails)


def send_notification_email(notification):
    """Send email for a single notification. Returns True on success."""
    recipients = get_recipients_for_notification(notification)
    if not recipients:
        return False

    subject = f"[Maram] {notification.get_notification_type_display()} – {notification.project.name}"
    body = (
        f"Bonjour,\n\n"
        f"{notification.message}\n\n"
        f"Projet : {notification.project.name}\n"
        f"N° BC : {notification.project.bon_commande_number}\n"
        f"Gouvernorat : {notification.project.get_gouvernorat_display()}\n\n"
        f"Accédez à l'application pour gérer ce projet.\n\n"
        f"---\nMaram – Gestion de projets"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.email_error = ''
        notification.save(update_fields=['email_sent', 'email_sent_at', 'email_error'])
        return True
    except Exception as exc:
        notification.email_error = str(exc)
        notification.save(update_fields=['email_error'])
        return False


def send_pending_emails():
    """Send emails for all unread notifications that haven't been emailed yet."""
    qs = Notification.objects.filter(
        status__in=['unread', 'read'],
        email_sent=False
    ).select_related('project')

    sent = 0
    for notif in qs:
        if send_notification_email(notif):
            sent += 1
    return sent
