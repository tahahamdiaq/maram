from django.db import models


NOTIFICATION_TYPES = [
    ('facture1_ready',    'Facture N°1 à établir'),
    ('facture1_j7',       'Rappel Facture N°1 – J-7'),
    ('facture1_j2',       'Rappel Facture N°1 – J-2'),
    ('facture1_overdue',  'Facture N°1 en retard'),
    ('facture2_ready',    'Facture N°2 à établir'),
    ('facture3_ready',    'Facture N°3 à établir'),
    ('d0_reminder',       'Rappel D0'),
    ('d6_reminder',       'Rappel D6'),
]

PRIORITY_CHOICES = [
    ('critique',  'Critique'),
    ('important', 'Important'),
    ('normal',    'Normal'),
]

STATUS_CHOICES = [
    ('unread',    'Non lue'),
    ('read',      'Lue'),
    ('processed', 'Traitée'),
]

CHANNEL_CHOICES = [
    ('app',   'Application'),
    ('email', 'Email'),
    ('both',  'Application + Email'),
]


class Notification(models.Model):
    from projects.models import Project

    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE,
        related_name='notifications', verbose_name='Projet'
    )
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPES,
        verbose_name='Type'
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='normal',
        verbose_name='Priorité'
    )
    message = models.TextField(verbose_name='Message')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='unread',
        verbose_name='Statut'
    )

    # Email tracking
    email_sent = models.BooleanField(default=False, verbose_name='Email envoyé')
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Heure d'envoi email")
    email_error = models.TextField(blank=True, verbose_name="Erreur email")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.get_notification_type_display()} – {self.project.name}"

    @property
    def is_critical(self):
        return self.priority == 'critique'

    @property
    def priority_color(self):
        return {
            'critique':  'danger',
            'important': 'warning',
            'normal':    'info',
        }.get(self.priority, 'secondary')

    @property
    def priority_icon(self):
        return {
            'critique':  'bi-exclamation-triangle-fill',
            'important': 'bi-bell-fill',
            'normal':    'bi-info-circle-fill',
        }.get(self.priority, 'bi-bell')


class NotificationRecipient(models.Model):
    RECIPIENT_TYPE_CHOICES = [
        ('project_engineers', 'Ingénieurs du projet'),
        ('billing_manager',   'Responsable facturation'),
        ('admin',             'Administrateur'),
        ('chef_projet',       'Chef de projet'),
        ('free_email',        'Adresse email libre'),
    ]

    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE,
        related_name='recipients', verbose_name='Notification'
    )
    recipient_type = models.CharField(
        max_length=30, choices=RECIPIENT_TYPE_CHOICES,
        verbose_name='Type de destinataire'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    channel = models.CharField(
        max_length=10, choices=CHANNEL_CHOICES, default='both',
        verbose_name='Canal'
    )
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Destinataire'
        verbose_name_plural = 'Destinataires'


class NotificationSettings(models.Model):
    """Configuration globale des notifications."""
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPES,
        unique=True, verbose_name='Type de notification'
    )
    channel = models.CharField(
        max_length=10, choices=CHANNEL_CHOICES, default='both',
        verbose_name='Canal par défaut'
    )
    send_to_project_engineers = models.BooleanField(
        default=True, verbose_name='Envoyer aux ingénieurs du projet'
    )
    send_to_billing_manager = models.BooleanField(
        default=True, verbose_name='Envoyer au responsable facturation'
    )
    send_to_admin = models.BooleanField(
        default=False, verbose_name='Envoyer à l\'administrateur'
    )
    extra_emails = models.TextField(
        blank=True,
        verbose_name='Emails supplémentaires (un par ligne)',
        help_text='Entrez une adresse email par ligne'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Paramètre de notification'
        verbose_name_plural = 'Paramètres de notifications'

    def __str__(self):
        return f"Config: {self.get_notification_type_display()}"

    def get_extra_email_list(self):
        return [e.strip() for e in self.extra_emails.splitlines() if e.strip()]
