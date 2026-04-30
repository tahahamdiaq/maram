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
    # Dossier status alerts (DAO / EXE × STR / ELEC / FL)
    ('dao_str_alerte',    'DAO Structure – dossier en attente'),
    ('dao_elec_alerte',   'DAO Électricité – dossier en attente'),
    ('dao_fl_alerte',     'DAO Fluide – dossier en attente'),
    ('exe_str_alerte',    'EXE Structure – dossier en attente'),
    ('exe_elec_alerte',   'EXE Électricité – dossier en attente'),
    ('exe_fl_alerte',     'EXE Fluide – dossier en attente'),
    # Expertise rapport alerts
    ('expertise_facture_ready',   'Expertise – Rapport à établir'),
    ('expertise_facture_j10',     'Expertise – Rappel Rapport J-10'),
    ('expertise_facture_j3',      'Expertise – Rappel Rapport J-3'),
    ('expertise_facture_overdue', 'Expertise – Rapport en retard'),
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
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications', verbose_name='Projet'
    )
    expertise = models.ForeignKey(
        'projects.Expertise', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications', verbose_name='Expertise'
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
    def entity_name(self):
        if self.project_id:
            return self.project.name
        if self.expertise_id:
            return self.expertise.name
        return ''

    @property
    def entity_bc_number(self):
        if self.project_id:
            return self.project.bon_commande_number
        if self.expertise_id:
            return self.expertise.bon_commande_number
        return ''

    @property
    def entity_gouvernorat(self):
        if self.project_id:
            return self.project.get_gouvernorat_display()
        if self.expertise_id:
            return self.expertise.get_gouvernorat_display()
        return ''

    @property
    def entity_detail_url(self):
        from django.urls import reverse
        if self.project_id:
            return reverse('project_detail', args=[self.project_id])
        if self.expertise_id:
            return reverse('expertise_detail', args=[self.expertise_id])
        return '#'

    @property
    def is_expertise(self):
        return bool(self.expertise_id)

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


class EmailLog(models.Model):
    notification = models.ForeignKey(
        Notification, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='email_logs', verbose_name='Notification'
    )
    recipients = models.TextField(verbose_name='Destinataires')
    subject = models.CharField(max_length=255, verbose_name='Objet')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Heure d'envoi")
    success = models.BooleanField(default=False, verbose_name='Succès')
    error = models.TextField(blank=True, verbose_name='Erreur')

    class Meta:
        verbose_name = 'Journal email'
        verbose_name_plural = 'Journal emails'
        ordering = ['-sent_at']

    def __str__(self):
        status = 'OK' if self.success else 'ERREUR'
        return f"[{status}] {self.subject} – {self.sent_at:%d/%m/%Y %H:%M}"

    @property
    def recipient_list(self):
        return [r.strip() for r in self.recipients.split(',') if r.strip()]


class UserSession(models.Model):
    """Tracks the single valid session per user for single-session enforcement."""
    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE,
        related_name='active_session', verbose_name='Utilisateur'
    )
    session_key = models.CharField(max_length=40, verbose_name='Clé de session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session active'
        verbose_name_plural = 'Sessions actives'

    def __str__(self):
        return f"Session de {self.user.username}"


class AccessLog(models.Model):
    EVENT_LOGIN = 'login'
    EVENT_LOGOUT = 'logout'
    EVENT_FORCED = 'forced_logout'
    EVENT_CHOICES = [
        (EVENT_LOGIN,  'Connexion'),
        (EVENT_LOGOUT, 'Déconnexion'),
        (EVENT_FORCED, 'Déconnexion forcée'),
    ]

    user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='access_logs', verbose_name='Utilisateur'
    )
    username = models.CharField(max_length=150, verbose_name="Nom d'utilisateur")
    event = models.CharField(max_length=20, choices=EVENT_CHOICES, verbose_name='Événement')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Adresse IP')
    user_agent = models.TextField(blank=True, verbose_name='Navigateur')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Horodatage')

    class Meta:
        verbose_name = "Journal d'accès"
        verbose_name_plural = "Journal d'accès"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.get_event_display()}] {self.username} – {self.timestamp:%d/%m/%Y %H:%M}"

    @property
    def event_color(self):
        return {
            self.EVENT_LOGIN:  'success',
            self.EVENT_LOGOUT: 'secondary',
            self.EVENT_FORCED: 'danger',
        }.get(self.event, 'secondary')

    @property
    def event_icon(self):
        return {
            self.EVENT_LOGIN:  'bi-box-arrow-in-right',
            self.EVENT_LOGOUT: 'bi-box-arrow-right',
            self.EVENT_FORCED: 'bi-shield-exclamation',
        }.get(self.event, 'bi-question')


class DeleteVerification(models.Model):
    """One-time code required to confirm a project or expertise deletion."""
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='delete_verifications', verbose_name='Projet'
    )
    expertise = models.ForeignKey(
        'projects.Expertise', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='delete_verifications', verbose_name='Expertise'
    )
    code = models.CharField(max_length=6, verbose_name='Code')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='Expiration')
    used = models.BooleanField(default=False)
    requested_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='delete_verifications', verbose_name='Demandé par'
    )

    class Meta:
        verbose_name = 'Vérification de suppression'
        verbose_name_plural = 'Vérifications de suppression'
        ordering = ['-created_at']

    def is_valid(self):
        from django.utils import timezone
        return not self.used and timezone.now() < self.expires_at


class LoginVerification(models.Model):
    """Stores a one-time code sent to the boss on each login attempt."""
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name='login_verifications', verbose_name='Utilisateur'
    )
    code = models.CharField(max_length=6, verbose_name='Code')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='Expiration')
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Vérification de connexion'
        verbose_name_plural = 'Vérifications de connexion'
        ordering = ['-created_at']

    def is_valid(self):
        from django.utils import timezone
        return not self.used and timezone.now() < self.expires_at


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
