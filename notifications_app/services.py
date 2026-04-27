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
    return set(
        project.notifications
        .filter(status__in=['unread', 'read'])
        .values_list('notification_type', flat=True)
    )


def _resolve_notifications(project, types):
    project.notifications.filter(
        notification_type__in=types,
        status__in=['unread', 'read']
    ).update(status='processed')


def _create(project, notif_type, priority, message):
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


# ─── expertise helpers ────────────────────────────────────────────────────────

def _active_types_expertise(expertise):
    return set(
        expertise.notifications
        .filter(status__in=['unread', 'read'])
        .values_list('notification_type', flat=True)
    )


def _resolve_expertise_notifications(expertise, types):
    expertise.notifications.filter(
        notification_type__in=types,
        status__in=['unread', 'read']
    ).update(status='processed')


def _create_expertise(expertise, notif_type, priority, message):
    from projects.models import ExpertiseObservation
    n = Notification.objects.create(
        expertise=expertise,
        notification_type=notif_type,
        priority=priority,
        message=message,
    )
    ExpertiseObservation.objects.create(
        expertise=expertise,
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


# ─── dossier status alerts ────────────────────────────────────────────────────

_DOSSIER_ALERTS = {
    'non_recu':     ('important', 'Dossier non reçu'),
    'non_approuve': ('critique',  'Dossier non approuvé'),
    'en_cours':     ('normal',    'En cours de vérification'),
}

def _check_dossier(project, active, notif_type, status, phase_label, spec_label):
    if status in ('approuve', 'non_prevu'):
        _resolve_notifications(project, [notif_type])
        return

    if status not in _DOSSIER_ALERTS:
        return

    priority, status_label = _DOSSIER_ALERTS[status]

    if notif_type in active:
        existing = project.notifications.filter(
            notification_type=notif_type,
            status__in=['unread', 'read']
        ).first()
        if existing and existing.priority == priority:
            return  # already active with same priority
        # Priority changed (e.g. non_recu → non_approuve) → replace
        _resolve_notifications(project, [notif_type])

    _create(
        project, notif_type, priority,
        f'{phase_label} {spec_label} – {status_label} pour le projet "{project.name}".'
    )


def check_dossier_statuses(project, active):
    specs = [
        ('str',  project.has_structure,          project.dao_structure,          project.exe_structure),
        ('elec', project.has_electricite,         project.dao_electricite,        project.exe_electricite),
        ('fl',   project.has_fluide,              project.dao_fluide,             project.exe_fluide),
        ('si',   project.has_securite_incendie,   project.dao_securite_incendie,  project.exe_securite_incendie),
    ]
    labels = {'str': 'STR', 'elec': 'ELEC', 'fl': 'FL', 'si': 'SI'}

    for key, enabled, dao_status, exe_status in specs:
        lbl = labels[key]
        if enabled:
            _check_dossier(project, active, f'dao_{key}_alerte', dao_status, 'DAO', lbl)
            _check_dossier(project, active, f'exe_{key}_alerte', exe_status, 'EXE', lbl)
        else:
            _resolve_notifications(project, [f'dao_{key}_alerte', f'exe_{key}_alerte'])


# ─── main entry points ────────────────────────────────────────────────────────

def check_project_notifications(project):
    today = date.today()
    active = _active_types(project)

    check_dossier_statuses(project, active)
    check_facture1(project, today, active)
    check_d0(project, active)
    check_facture2(project, active)
    check_d6(project, active)
    check_facture3(project, active)


def check_expertise_notifications(expertise):
    today = date.today()
    active = _active_types_expertise(expertise)
    facture_types = [
        'expertise_facture_ready', 'expertise_facture_j10',
        'expertise_facture_j3', 'expertise_facture_overdue',
    ]

    invoice = expertise.get_invoice

    # Invoice established + transmitted → resolve all, nothing more to do
    if invoice and invoice.is_complete:
        _resolve_expertise_notifications(expertise, facture_types)
        return

    # Dossier not approved yet → nothing
    if not expertise.dossier_complete or not expertise.invoice_due_date:
        return

    due_date = expertise.invoice_due_date
    days = (due_date - today).days

    if days < 0:
        if 'expertise_facture_overdue' not in active:
            _resolve_expertise_notifications(expertise, [
                'expertise_facture_ready', 'expertise_facture_j10', 'expertise_facture_j3'
            ])
            _create_expertise(expertise, 'expertise_facture_overdue', 'critique',
                f'RETARD – Facture expertise en retard de {-days} jour(s) pour "{expertise.name}".')
    elif days <= 3:
        if 'expertise_facture_j3' not in active:
            _resolve_expertise_notifications(expertise, [
                'expertise_facture_ready', 'expertise_facture_j10'
            ])
            _create_expertise(expertise, 'expertise_facture_j3', 'critique',
                f'URGENT – Il reste {days} jour(s) pour établir la facture de l\'expertise '
                f'"{expertise.name}" (échéance : {due_date.strftime("%d/%m/%Y")}).')
    elif days <= 10:
        if 'expertise_facture_j10' not in active:
            _resolve_expertise_notifications(expertise, ['expertise_facture_ready'])
            _create_expertise(expertise, 'expertise_facture_j10', 'important',
                f'Rappel – {days} jour(s) restants pour la facture de l\'expertise '
                f'"{expertise.name}" (échéance : {due_date.strftime("%d/%m/%Y")}).')
    else:
        if 'expertise_facture_ready' not in active:
            _create_expertise(expertise, 'expertise_facture_ready', 'important',
                f'Facture expertise à établir pour "{expertise.name}" '
                f'(avant le {due_date.strftime("%d/%m/%Y")}).')


def check_all_notifications():
    """Run all notification checks for every project and expertise."""
    for project in Project.objects.prefetch_related('invoices', 'notifications').all():
        try:
            check_project_notifications(project)
        except Exception as exc:
            print(f"[notification check] Error on project {project.pk}: {exc}")

    from projects.models import Expertise
    for expertise in Expertise.objects.prefetch_related('invoices', 'notifications').all():
        try:
            check_expertise_notifications(expertise)
        except Exception as exc:
            print(f"[notification check] Error on expertise {expertise.pk}: {exc}")
