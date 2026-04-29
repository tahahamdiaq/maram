from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


GOUVERNORAT_CHOICES = [
    ('ariana', 'Ariana'),
    ('beja', 'Béja'),
    ('ben_arous', 'Ben Arous'),
    ('bizerte', 'Bizerte'),
    ('gabes', 'Gabès'),
    ('gafsa', 'Gafsa'),
    ('jendouba', 'Jendouba'),
    ('kairouan', 'Kairouan'),
    ('kasserine', 'Kasserine'),
    ('kebili', 'Kébili'),
    ('kef', 'Kef'),
    ('mahdia', 'Mahdia'),
    ('manouba', 'Manouba'),
    ('medenine', 'Médenine'),
    ('monastir', 'Monastir'),
    ('nabeul', 'Nabeul'),
    ('sfax', 'Sfax'),
    ('sidi_bouzid', 'Sidi Bouzid'),
    ('siliana', 'Siliana'),
    ('sousse', 'Sousse'),
    ('tataouine', 'Tataouine'),
    ('tozeur', 'Tozeur'),
    ('tunis', 'Tunis'),
    ('zaghouan', 'Zaghouan'),
]

STATUS_CHOICES = [
    ('non_prevu', 'Non prévu'),
    ('non_recu', 'Dossier non reçu'),
    ('non_approuve', 'Dossier non approuvé'),
    ('en_cours', 'En cours de vérification'),
    ('approuve', 'Approuvé'),
]

DOSSIER_STATUS_CHOICES = [
    ('non_recu', 'Dossier non reçu'),
    ('non_approuve', 'Dossier non approuvé'),
    ('en_cours', 'En cours de vérification'),
    ('approuve', 'Approuvé'),
]


class Engineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name='Nom complet')
    email = models.EmailField(verbose_name='Email')
    specialties = models.CharField(max_length=200, blank=True, verbose_name='Spécialités')

    class Meta:
        verbose_name = 'Ingénieur'
        verbose_name_plural = 'Ingénieurs'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    # --- Identité ---
    name = models.CharField(max_length=300, verbose_name='Nom du projet')
    bon_commande_number = models.CharField(max_length=100, verbose_name='N° Bon de commande')
    bon_commande_date = models.DateField(verbose_name='Date de réception du bon de commande')
    gouvernorat = models.CharField(max_length=50, choices=GOUVERNORAT_CHOICES, verbose_name='Gouvernorat')
    maitre_ouvrage = models.CharField(max_length=200, verbose_name="Maître d'ouvrage")

    # --- Spécialités ---
    has_structure = models.BooleanField(default=False, verbose_name='Structure')
    has_electricite = models.BooleanField(default=False, verbose_name='Électricité')
    has_fluide = models.BooleanField(default=False, verbose_name='Fluide')
    has_securite_incendie = models.BooleanField(default=False, verbose_name='Sécurité incendie')

    # --- Ingénieurs ---
    engineers = models.ManyToManyField(Engineer, blank=True, verbose_name='Ingénieurs')

    # --- Visites ---
    planned_visits = models.PositiveIntegerField(default=0, verbose_name='Visites prévues')
    completed_visits = models.PositiveIntegerField(default=0, verbose_name='Visites réalisées')

    # --- DAO status par spécialité ---
    dao_structure = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='DAO Structure'
    )
    dao_electricite = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='DAO Électricité'
    )
    dao_fluide = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='DAO Fluide'
    )
    dao_securite_incendie = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='DAO Sécurité incendie'
    )

    # --- DAO dates de réception / décision par spécialité ---
    dao_structure_received_date = models.DateField(null=True, blank=True, verbose_name='DAO STR – Date réception')
    dao_structure_decision_date = models.DateField(null=True, blank=True, verbose_name='DAO STR – Date décision')
    dao_electricite_received_date = models.DateField(null=True, blank=True, verbose_name='DAO ELEC – Date réception')
    dao_electricite_decision_date = models.DateField(null=True, blank=True, verbose_name='DAO ELEC – Date décision')
    dao_fluide_received_date = models.DateField(null=True, blank=True, verbose_name='DAO FL – Date réception')
    dao_fluide_decision_date = models.DateField(null=True, blank=True, verbose_name='DAO FL – Date décision')
    dao_securite_incendie_received_date = models.DateField(null=True, blank=True, verbose_name='DAO SI – Date réception')
    dao_securite_incendie_decision_date = models.DateField(null=True, blank=True, verbose_name='DAO SI – Date décision')

    dao_completed_date = models.DateField(
        null=True, blank=True,
        verbose_name='Date de complétion DAO'
    )

    # --- D0 ---
    d0_done = models.BooleanField(default=False, verbose_name='D0 réalisé')
    d0_date = models.DateField(null=True, blank=True, verbose_name='Date D0')

    # --- EXE status par spécialité ---
    exe_structure = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='EXE Structure'
    )
    exe_electricite = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='EXE Électricité'
    )
    exe_fluide = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='EXE Fluide'
    )
    exe_securite_incendie = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='EXE Sécurité incendie'
    )

    # --- EXE dates de réception / décision par spécialité ---
    exe_structure_received_date = models.DateField(null=True, blank=True, verbose_name='EXE STR – Date réception')
    exe_structure_decision_date = models.DateField(null=True, blank=True, verbose_name='EXE STR – Date décision')
    exe_electricite_received_date = models.DateField(null=True, blank=True, verbose_name='EXE ELEC – Date réception')
    exe_electricite_decision_date = models.DateField(null=True, blank=True, verbose_name='EXE ELEC – Date décision')
    exe_fluide_received_date = models.DateField(null=True, blank=True, verbose_name='EXE FL – Date réception')
    exe_fluide_decision_date = models.DateField(null=True, blank=True, verbose_name='EXE FL – Date décision')
    exe_securite_incendie_received_date = models.DateField(null=True, blank=True, verbose_name='EXE SI – Date réception')
    exe_securite_incendie_decision_date = models.DateField(null=True, blank=True, verbose_name='EXE SI – Date décision')

    exe_started_date = models.DateField(null=True, blank=True, verbose_name='Date début EXE')

    # --- D6 ---
    d6_done = models.BooleanField(default=False, verbose_name='D6 réalisé')
    d6_date = models.DateField(null=True, blank=True, verbose_name='Date D6')

    # --- Réceptions ---
    rpro = models.BooleanField(default=False, verbose_name='RPRO (Réception provisoire)')
    rpro_date = models.DateField(null=True, blank=True, verbose_name='Date RPRO')
    rdef = models.BooleanField(default=False, verbose_name='RDEF (Réception définitive)')
    rdef_date = models.DateField(null=True, blank=True, verbose_name='Date RDEF')

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_projects'
    )

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bon_commande_number} – {self.name}"

    @property
    def visit_percentage(self):
        if self.planned_visits == 0:
            return 0
        return round((self.completed_visits / self.planned_visits) * 100, 1)

    @property
    def dao_completed(self):
        if not (self.has_structure or self.has_electricite or self.has_fluide or self.has_securite_incendie):
            return False
        if self.has_structure and self.dao_structure != 'approuve':
            return False
        if self.has_electricite and self.dao_electricite != 'approuve':
            return False
        if self.has_fluide and self.dao_fluide != 'approuve':
            return False
        if self.has_securite_incendie and self.dao_securite_incendie != 'approuve':
            return False
        return True

    @property
    def exe_completed(self):
        if not (self.has_structure or self.has_electricite or self.has_fluide or self.has_securite_incendie):
            return False
        if self.has_structure and self.exe_structure != 'approuve':
            return False
        if self.has_electricite and self.exe_electricite != 'approuve':
            return False
        if self.has_fluide and self.exe_fluide != 'approuve':
            return False
        if self.has_securite_incendie and self.exe_securite_incendie != 'approuve':
            return False
        return True

    @property
    def invoice1_due_date(self):
        if self.dao_completed_date:
            return self.dao_completed_date + timedelta(days=21)
        return None

    @property
    def invoice1_days_remaining(self):
        due = self.invoice1_due_date
        if due:
            return (due - date.today()).days
        return None

    @property
    def invoice1(self):
        return self.invoices.filter(invoice_number=1).first()

    @property
    def invoice2(self):
        return self.invoices.filter(invoice_number=2).first()

    @property
    def invoice3(self):
        return self.invoices.filter(invoice_number=3).first()

    @property
    def invoice1_established(self):
        inv = self.invoice1
        return bool(inv and inv.establishment_date)

    @property
    def invoice2_established(self):
        inv = self.invoice2
        return bool(inv and inv.establishment_date)

    @property
    def invoice3_established(self):
        inv = self.invoice3
        return bool(inv and inv.establishment_date)

    @property
    def invoice2_condition(self):
        return self.planned_visits > 0 and self.visit_percentage >= 50

    @property
    def invoice3_condition(self):
        return (
            self.planned_visits > 0
            and self.completed_visits >= self.planned_visits
            and self.d6_done
            and self.rpro
            and self.rdef
        )

    @property
    def specialties_display(self):
        parts = []
        if self.has_structure:
            parts.append('STR')
        if self.has_electricite:
            parts.append('ELEC')
        if self.has_fluide:
            parts.append('FL')
        if self.has_securite_incendie:
            parts.append('SI')
        return ' / '.join(parts) if parts else '–'

    def save(self, *args, **kwargs):
        if self.dao_completed and not self.dao_completed_date:
            decision_dates = [
                d for d in [
                    self.dao_structure_decision_date if self.has_structure else None,
                    self.dao_electricite_decision_date if self.has_electricite else None,
                    self.dao_fluide_decision_date if self.has_fluide else None,
                    self.dao_securite_incendie_decision_date if self.has_securite_incendie else None,
                ] if d is not None
            ]
            self.dao_completed_date = max(decision_dates) if decision_dates else date.today()
        super().save(*args, **kwargs)

    def _days_remaining(self, status_field):
        status = getattr(self, status_field)
        received = getattr(self, f'{status_field}_received_date', None)
        if status == 'en_cours' and received:
            return (received + timedelta(days=21) - date.today()).days
        return None

    @property
    def dao_structure_days_remaining(self):
        return self._days_remaining('dao_structure')

    @property
    def dao_electricite_days_remaining(self):
        return self._days_remaining('dao_electricite')

    @property
    def dao_fluide_days_remaining(self):
        return self._days_remaining('dao_fluide')

    @property
    def dao_securite_incendie_days_remaining(self):
        return self._days_remaining('dao_securite_incendie')

    @property
    def exe_structure_days_remaining(self):
        return self._days_remaining('exe_structure')

    @property
    def exe_electricite_days_remaining(self):
        return self._days_remaining('exe_electricite')

    @property
    def exe_fluide_days_remaining(self):
        return self._days_remaining('exe_fluide')

    @property
    def exe_securite_incendie_days_remaining(self):
        return self._days_remaining('exe_securite_incendie')


class Expertise(models.Model):
    name = models.CharField(max_length=300, verbose_name="Intitulé de l'expertise")
    bon_commande_number = models.CharField(max_length=100, verbose_name='N° Bon de commande')
    bon_commande_date = models.DateField(verbose_name='Date de réception du bon de commande')
    gouvernorat = models.CharField(max_length=50, choices=GOUVERNORAT_CHOICES, verbose_name='Gouvernorat')
    maitre_ouvrage = models.CharField(max_length=200, verbose_name="Maître d'ouvrage")
    has_structure = models.BooleanField(default=False, verbose_name='Structure')
    has_electricite = models.BooleanField(default=False, verbose_name='Électricité')
    has_fluide = models.BooleanField(default=False, verbose_name='Fluide')
    has_securite_incendie = models.BooleanField(default=False, verbose_name='Sécurité incendie')
    engineers = models.ManyToManyField(Engineer, blank=True, verbose_name='Ingénieurs')

    # --- Statut du dossier par spécialité ---
    dossier_structure = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='Dossier Structure'
    )
    dossier_electricite = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='Dossier Électricité'
    )
    dossier_fluide = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='Dossier Fluide'
    )
    dossier_securite_incendie = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='non_prevu',
        verbose_name='Dossier Sécurité incendie'
    )

    # --- Dates de réception / décision par spécialité ---
    dossier_structure_received_date = models.DateField(null=True, blank=True, verbose_name='STR – Date réception')
    dossier_structure_decision_date = models.DateField(null=True, blank=True, verbose_name='STR – Date décision')
    dossier_electricite_received_date = models.DateField(null=True, blank=True, verbose_name='ELEC – Date réception')
    dossier_electricite_decision_date = models.DateField(null=True, blank=True, verbose_name='ELEC – Date décision')
    dossier_fluide_received_date = models.DateField(null=True, blank=True, verbose_name='FL – Date réception')
    dossier_fluide_decision_date = models.DateField(null=True, blank=True, verbose_name='FL – Date décision')
    dossier_securite_incendie_received_date = models.DateField(null=True, blank=True, verbose_name='SI – Date réception')
    dossier_securite_incendie_decision_date = models.DateField(null=True, blank=True, verbose_name='SI – Date décision')

    dossier_completed_date = models.DateField(null=True, blank=True, verbose_name='Date de complétion du dossier')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_expertises'
    )

    class Meta:
        verbose_name = 'Expertise'
        verbose_name_plural = 'Expertises'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bon_commande_number} – {self.name}"

    @property
    def dossier_complete(self):
        if not any([self.has_structure, self.has_electricite, self.has_fluide, self.has_securite_incendie]):
            return False
        if self.has_structure and self.dossier_structure != 'approuve':
            return False
        if self.has_electricite and self.dossier_electricite != 'approuve':
            return False
        if self.has_fluide and self.dossier_fluide != 'approuve':
            return False
        if self.has_securite_incendie and self.dossier_securite_incendie != 'approuve':
            return False
        return True

    def _dossier_days_remaining(self, status_field):
        status = getattr(self, status_field)
        received = getattr(self, f'{status_field}_received_date', None)
        if status == 'en_cours' and received:
            return (received + timedelta(days=21) - date.today()).days
        return None

    @property
    def dossier_structure_days_remaining(self):
        return self._dossier_days_remaining('dossier_structure')

    @property
    def dossier_electricite_days_remaining(self):
        return self._dossier_days_remaining('dossier_electricite')

    @property
    def dossier_fluide_days_remaining(self):
        return self._dossier_days_remaining('dossier_fluide')

    @property
    def dossier_securite_incendie_days_remaining(self):
        return self._dossier_days_remaining('dossier_securite_incendie')

    @property
    def invoice_due_date(self):
        if self.dossier_completed_date:
            return self.dossier_completed_date + timedelta(days=60)
        return None

    @property
    def invoice_days_remaining(self):
        due = self.invoice_due_date
        if due:
            return (due - date.today()).days
        return None

    @property
    def get_invoice(self):
        return self.invoices.first()

    def save(self, *args, **kwargs):
        if self.dossier_complete and not self.dossier_completed_date:
            self.dossier_completed_date = date.today()
        super().save(*args, **kwargs)


class ExpertiseInvoice(models.Model):
    expertise = models.ForeignKey(
        Expertise, on_delete=models.CASCADE,
        related_name='invoices', verbose_name='Expertise'
    )
    establishment_date = models.DateField(null=True, blank=True, verbose_name="Date d'établissement")
    transmission_date = models.DateField(null=True, blank=True, verbose_name='Date de transmission')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Facture Expertise'
        verbose_name_plural = 'Factures Expertise'

    def __str__(self):
        return f"Facture – {self.expertise.name}"

    @property
    def is_established(self):
        return bool(self.establishment_date)

    @property
    def is_complete(self):
        return bool(self.establishment_date and self.transmission_date)


class ExpertiseObservation(models.Model):
    expertise = models.ForeignKey(
        Expertise, on_delete=models.CASCADE,
        related_name='observations', verbose_name='Expertise'
    )
    date = models.DateField(default=date.today, verbose_name='Date')
    text = models.TextField(verbose_name='Observation')
    is_auto = models.BooleanField(default=False, verbose_name='Automatique')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Créé par'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Observation Expertise'
        verbose_name_plural = 'Observations Expertise'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} – {self.expertise.name}"


class Invoice(models.Model):
    INVOICE_CHOICES = [
        (1, 'Facture N°1'),
        (2, 'Facture N°2'),
        (3, 'Facture N°3'),
    ]
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='invoices', verbose_name='Projet'
    )
    invoice_number = models.PositiveSmallIntegerField(
        choices=INVOICE_CHOICES, verbose_name='Numéro de facture'
    )
    establishment_date = models.DateField(
        null=True, blank=True, verbose_name="Date d'établissement"
    )
    transmission_date = models.DateField(
        null=True, blank=True, verbose_name='Date de transmission'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        unique_together = [('project', 'invoice_number')]
        ordering = ['invoice_number']

    def __str__(self):
        return f"Facture N°{self.invoice_number} – {self.project.name}"

    @property
    def is_established(self):
        return bool(self.establishment_date)

    @property
    def is_transmitted(self):
        return bool(self.transmission_date)


class ProjectObservation(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='observations', verbose_name='Projet'
    )
    date = models.DateField(default=date.today, verbose_name='Date')
    text = models.TextField(verbose_name='Observation')
    is_auto = models.BooleanField(default=False, verbose_name='Automatique')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Créé par'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} – {self.project.name}"
