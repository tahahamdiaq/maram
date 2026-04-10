"""
Business logic for generating and managing notifications.
Called by the management command `check_notifications` and the middleware.
"""
from datetime import date
from django.utils import timezone

from projects.models import Project, ProjectObservation
from .models import Notification, NotificationSettings, CHANNEL_CHOICES


# ─── helpers ──────────────────────────────────────────────────────────────────

def _active_types(project):
    """Return the set of notification_type values that are currently active (unread/read)."""
    return set(
        project.notifications
        .filter(status__in=['unread', 'read'])
        .values_list('notification_type', flat=True)
    )


def _resolve_notifications(project, types):
    """Mark notifications of the given types as 'processed' (action done)."""
    project.notifications.filter(
        notification_type__in=types,
        status__in=['unread', 'read']
    ).update(status='processed')


def _create(project, notif_type, priority, message):
    """Create a notification and log an automatic observation on the project."""
    n = Notification.objects.create(
        project=project,
        notification_type=notif_type,
        priority=priority,
        message=message,
    )
    ProjectObservation.objects.create(
        project=project,
        date=date.today(),
        text=f"[Auto] {message}",
        is_auto=True,
    )
    return n


# ─── per-project checks ───────────────────────────────────────────────────────

def check_facture1(project, today, active):
    invoice1 = project.invoice1
    facture1_types = ['facture1_ready', 'facture1_j7', 'facture1_j2', 'facture1_overdue']

    # Invoice already established → resolve all pending alerts
    if invoice1 and invoice1.establishment_date:
        _resolve_notifications(project, facture1_types)
        return

    # DAO not yet complete → nothing to do
    if not project.dao_completed:
        return

    due_date = project.invoice1_due_date
    if not due_date:
        return

    days = (due_date - today).days

    if days < 0:
        # Overdue
        if 'facture1_overdue' not in active:
            _resolve_notifications(project, ['facture1_ready', 'facture1_j7', 'facture1_j2'])
            _create(project, 'facture1_overdue', 'critique',
                    f'RETARD – Facture N°1 en retard de {-days} jour(s) pour le projet "{project.name}".')

    elif days <= 2:
        # J-2 critical
        if 'facture1_j2' not in active:
            _resolve_notifications(project, ['facture1_ready', 'facture1_j7'])
            _create(project, 'facture1_j2', 'critique',
                    f'URGENT – Il ne reste que {days} jour(s) pour établir la Facture N°1 du projet "{project.name}" (échéance : {due_date.strftime("%d/%m/%Y")}).')

    elif days <= 7:
        # J-7 reminder
        if 'facture1_j7' not in active:
            _resolve_notifications(project, ['facture1_ready'])
            _create(project, 'facture1_j7', 'important',
                    f'Rappel – Il vous reste {days} jour(s) pour établir la Facture N°1 du projet "{project.name}" (échéance : {due_date.strftime("%d/%m/%Y")}).')

    else:
        # Initial notification
        if 'facture1_ready' not in active:
            _create(project, 'facture1_ready', 'important',
                    f'Facture N°1 à établir pour le projet "{project.name}" (avant le {due_date.strftime("%d/%m/%Y")}).')


def check_d0(project, active):
    # D0 already done → resolve
    if project.d0_done:
        _resolve_notifications(project, ['d0_reminder'])
        return

    # Trigger if DAO is complete but D0 not yet done
    if project.dao_completed and 'd0_reminder' not in active:
        _create(project, 'd0_reminder', 'normal',
                f'Rappel – Le dossier D0 doit être réalisé avant le lancement de la phase EXE pour le projet "{project.name}".')


def check_facture2(project, active):
    invoice2 = project.invoice2

    if invoice2 and invoice2.establishment_date:
        _resolve_notifications(project, ['facture2_ready'])
        return

    if project.invoice2_condition and 'facture2_ready' not in active:
        _create(project, 'facture2_ready', 'normal',
                f'Facture N°2 à établir – 50 % des visites prévues sont réalisées pour le projet "{project.name}" ({project.completed_visits}/{project.planned_visits} visites).')


def check_d6(project, active):
    if project.d6_done:
        _resolve_notifications(project, ['d6_reminder'])
        return

    # Remind about D6 when facture3 condition is nearly met or met
    if project.invoice3_condition and 'd6_reminder' not in active:
        _create(project, 'd6_reminder', 'normal',
                f'Rappel – Le dossier D6 doit être réalisé avec la Facture N°3 pour le projet "{project.name}".')


def check_facture3(project, active):
    invoice3 = project.invoice3

    if invoice3 and invoice3.establishment_date:
        _resolve_notifications(project, ['facture3_ready'])
        return

    if project.invoice3_condition and 'facture3_ready' not in active:
        _create(project, 'facture3_ready', 'important',
                f'Facture N°3 à établir – toutes les conditions sont remplies pour le projet "{project.name}" (100 % visites, RPRO et RDEF validées).')


# ─── main entry points ────────────────────────────────────────────────────────

def check_project_notifications(project):
    today = date.today()
    active = _active_types(project)

    check_facture1(project, today, active)
    check_d0(project, active)
    check_facture2(project, active)
    check_d6(project, active)
    check_facture3(project, active)


def check_all_notifications():
    """Run all notification checks for every project. Called by cron/management command."""
    for project in Project.objects.prefetch_related('invoices', 'notifications').all():
        try:
            check_project_notifications(project)
        except Exception as exc:
            # Log but don't crash the whole run
            print(f"[notification check] Error on project {project.pk}: {exc}")
