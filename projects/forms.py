from django import forms
from django.utils.safestring import mark_safe
from .models import Project, Invoice, ProjectObservation, Engineer, STATUS_CHOICES, DOSSIER_STATUS_CHOICES, Expertise, ExpertiseInvoice


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            # Identité
            'name', 'bon_commande_number', 'bon_commande_date',
            'gouvernorat', 'maitre_ouvrage',
            # Spécialités
            'has_structure', 'has_electricite', 'has_fluide', 'has_securite_incendie',
            # Ingénieurs
            'engineers',
            # Visites
            'planned_visits', 'completed_visits',
            # DAO
            'dao_structure', 'dao_structure_received_date', 'dao_structure_decision_date',
            'dao_electricite', 'dao_electricite_received_date', 'dao_electricite_decision_date',
            'dao_fluide', 'dao_fluide_received_date', 'dao_fluide_decision_date',
            'dao_securite_incendie', 'dao_securite_incendie_received_date', 'dao_securite_incendie_decision_date',
            'dao_completed_date',
            # D0
            'd0_done', 'd0_date',
            # EXE
            'exe_structure', 'exe_structure_received_date', 'exe_structure_decision_date',
            'exe_electricite', 'exe_electricite_received_date', 'exe_electricite_decision_date',
            'exe_fluide', 'exe_fluide_received_date', 'exe_fluide_decision_date',
            'exe_securite_incendie', 'exe_securite_incendie_received_date', 'exe_securite_incendie_decision_date',
            # D6
            'd6_done', 'd6_date',
            # Réceptions
            'rpro', 'rpro_date', 'rdef', 'rdef_date',
        ]
        widgets = {
            'bon_commande_number': forms.TextInput(attrs={'maxlength': '5', 'pattern': '[0-9]{5}', 'inputmode': 'numeric', 'placeholder': '12345'}),
            'bon_commande_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_completed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_structure_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_structure_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_electricite_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_electricite_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_fluide_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_fluide_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_securite_incendie_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_securite_incendie_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_structure_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_structure_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_electricite_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_electricite_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_fluide_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_fluide_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_securite_incendie_received_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'exe_securite_incendie_decision_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'd0_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'd6_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rpro_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rdef_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'engineers': forms.CheckboxSelectMultiple(),
            'maitre_ouvrage': forms.TextInput(attrs={'list': 'maitre-ouvrage-list'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional_dates = [
            'dao_completed_date', 'd0_date', 'd6_date', 'rpro_date', 'rdef_date',
            'dao_structure_received_date', 'dao_structure_decision_date',
            'dao_electricite_received_date', 'dao_electricite_decision_date',
            'dao_fluide_received_date', 'dao_fluide_decision_date',
            'dao_securite_incendie_received_date', 'dao_securite_incendie_decision_date',
            'exe_structure_received_date', 'exe_structure_decision_date',
            'exe_electricite_received_date', 'exe_electricite_decision_date',
            'exe_fluide_received_date', 'exe_fluide_decision_date',
            'exe_securite_incendie_received_date', 'exe_securite_incendie_decision_date',
        ]
        for field_name in optional_dates:
            self.fields[field_name].required = False

        # DAO/EXE fields: not selectable manually as "non_prevu" — set automatically
        for f in ['dao_structure', 'dao_electricite', 'dao_fluide', 'dao_securite_incendie',
                  'exe_structure', 'exe_electricite', 'exe_fluide', 'exe_securite_incendie']:
            self.fields[f].required = False
            self.fields[f].choices = DOSSIER_STATUS_CHOICES

    def clean_bon_commande_number(self):
        value = self.cleaned_data.get('bon_commande_number', '')
        if not value.isdigit() or len(value) != 5:
            raise forms.ValidationError("Le numéro de bon de commande doit contenir exactement 5 chiffres.")
        return value

    def clean(self):
        cleaned = super().clean()
        # At least one specialty required
        if not any([cleaned.get('has_structure'), cleaned.get('has_electricite'), cleaned.get('has_fluide'), cleaned.get('has_securite_incendie')]):
            raise forms.ValidationError("Veuillez sélectionner au moins une spécialité.")

        # Auto-set non_prevu for specialties absent from this project
        for specialty, dao_field, exe_field in [
            ('has_structure',         'dao_structure',         'exe_structure'),
            ('has_electricite',       'dao_electricite',       'exe_electricite'),
            ('has_fluide',            'dao_fluide',            'exe_fluide'),
            ('has_securite_incendie', 'dao_securite_incendie', 'exe_securite_incendie'),
        ]:
            if not cleaned.get(specialty):
                cleaned[dao_field] = 'non_prevu'
                cleaned[exe_field] = 'non_prevu'

        # D0: if marked done, date is required
        if cleaned.get('d0_done') and not cleaned.get('d0_date'):
            self.add_error('d0_date', "La date de réalisation D0 est requise.")

        # D6: if marked done, date is required
        if cleaned.get('d6_done') and not cleaned.get('d6_date'):
            self.add_error('d6_date', "La date de réalisation D6 est requise.")

        # Visits sanity check
        planned = cleaned.get('planned_visits', 0)
        completed = cleaned.get('completed_visits', 0)
        if completed > planned:
            self.add_error('completed_visits', "Les visites réalisées ne peuvent pas dépasser les visites prévues.")

        return cleaned


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['establishment_date', 'transmission_date', 'notes']
        widgets = {
            'establishment_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'transmission_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['establishment_date'].required = False
        self.fields['transmission_date'].required = False
        self.fields['notes'].required = False


class ObservationForm(forms.ModelForm):
    class Meta:
        model = ProjectObservation
        fields = ['date', 'text']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Saisir une observation...'}),
        }


class EngineerForm(forms.ModelForm):
    SPECIALTY_CHOICES = [
        ('', '– Choisir une spécialité –'),
        ('Structure', 'Structure'),
        ('Électricité', 'Électricité'),
        ('Fluide', 'Fluide'),
        ('Sécurité incendie', 'Sécurité incendie'),
    ]
    specialties = forms.ChoiceField(choices=SPECIALTY_CHOICES, required=False, label='Spécialités')

    class Meta:
        model = Engineer
        fields = ['name', 'email', 'specialties']


class ProjectFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nom du projet', 'class': 'form-control'})
    )
    gouvernorat = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les gouvernorats')] + [
            ('ariana', 'Ariana'), ('beja', 'Béja'), ('ben_arous', 'Ben Arous'),
            ('bizerte', 'Bizerte'), ('gabes', 'Gabès'), ('gafsa', 'Gafsa'),
            ('jendouba', 'Jendouba'), ('kairouan', 'Kairouan'), ('kasserine', 'Kasserine'),
            ('kebili', 'Kébili'), ('kef', 'Kef'), ('mahdia', 'Mahdia'),
            ('manouba', 'Manouba'), ('medenine', 'Médenine'), ('monastir', 'Monastir'),
            ('nabeul', 'Nabeul'), ('sfax', 'Sfax'), ('sidi_bouzid', 'Sidi Bouzid'),
            ('siliana', 'Siliana'), ('sousse', 'Sousse'), ('tataouine', 'Tataouine'),
            ('tozeur', 'Tozeur'), ('tunis', 'Tunis'), ('zaghouan', 'Zaghouan'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    specialty = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Toutes les spécialités'),
            ('structure', 'Structure'),
            ('electricite', 'Électricité'),
            ('fluide', 'Fluide'),
            ('securite_incendie', 'Sécurité incendie'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    maitre_ouvrage = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Maître d\'ouvrage…', 'id': 'id_maitre_ouvrage_filter', 'autocomplete': 'off'})
    )
    notification_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Tous les projets'),
            ('facture1', 'Facture N°1 en attente / retard'),
            ('facture2', 'Facture N°2 à établir'),
            ('facture3', 'Facture N°3 à établir'),
            ('d0', 'D0 en attente'),
            ('d6', 'D6 en attente'),
            ('critique', 'Alertes critiques'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ExpertiseForm(forms.ModelForm):
    class Meta:
        model = Expertise
        fields = [
            'name', 'bon_commande_number', 'bon_commande_date',
            'gouvernorat', 'maitre_ouvrage',
            'has_structure', 'has_electricite', 'has_fluide', 'has_securite_incendie',
            'engineers',
            'dossier_structure', 'dossier_structure_received_date', 'dossier_structure_decision_date',
            'dossier_electricite', 'dossier_electricite_received_date', 'dossier_electricite_decision_date',
            'dossier_fluide', 'dossier_fluide_received_date', 'dossier_fluide_decision_date',
            'dossier_securite_incendie', 'dossier_securite_incendie_received_date', 'dossier_securite_incendie_decision_date',
            'dossier_completed_date',
        ]
        widgets = {
            'bon_commande_number':    forms.TextInput(attrs={'maxlength': '5', 'pattern': '[0-9]{5}', 'inputmode': 'numeric', 'placeholder': '12345'}),
            'bon_commande_date':      forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_completed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_structure_received_date':           forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_structure_decision_date':           forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_electricite_received_date':         forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_electricite_decision_date':         forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_fluide_received_date':              forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_fluide_decision_date':              forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_securite_incendie_received_date':   forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_securite_incendie_decision_date':   forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'engineers':              forms.CheckboxSelectMultiple(),
            'maitre_ouvrage':         forms.TextInput(attrs={'list': 'maitre-ouvrage-list'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional_dates = [
            'dossier_completed_date',
            'dossier_structure_received_date', 'dossier_structure_decision_date',
            'dossier_electricite_received_date', 'dossier_electricite_decision_date',
            'dossier_fluide_received_date', 'dossier_fluide_decision_date',
            'dossier_securite_incendie_received_date', 'dossier_securite_incendie_decision_date',
        ]
        for f in optional_dates:
            self.fields[f].required = False
        for f in ['dossier_structure', 'dossier_electricite', 'dossier_fluide', 'dossier_securite_incendie']:
            self.fields[f].required = False
            self.fields[f].choices = DOSSIER_STATUS_CHOICES

    def clean_bon_commande_number(self):
        value = self.cleaned_data.get('bon_commande_number', '')
        if not value.isdigit() or len(value) != 5:
            raise forms.ValidationError("Le numéro de bon de commande doit contenir exactement 5 chiffres.")
        return value

    def clean(self):
        cleaned = super().clean()
        if not any([cleaned.get('has_structure'), cleaned.get('has_electricite'), cleaned.get('has_fluide'), cleaned.get('has_securite_incendie')]):
            raise forms.ValidationError("Veuillez sélectionner au moins une spécialité.")
        for specialty, field in [
            ('has_structure',         'dossier_structure'),
            ('has_electricite',       'dossier_electricite'),
            ('has_fluide',            'dossier_fluide'),
            ('has_securite_incendie', 'dossier_securite_incendie'),
        ]:
            if not cleaned.get(specialty):
                cleaned[field] = 'non_prevu'
        return cleaned


class ExpertiseInvoiceForm(forms.ModelForm):
    class Meta:
        model = ExpertiseInvoice
        fields = ['establishment_date', 'transmission_date', 'notes']
        widgets = {
            'establishment_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'transmission_date':  forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes':              forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['establishment_date'].required = False
        self.fields['transmission_date'].required = False
        self.fields['notes'].required = False


class ExpertiseFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher…', 'class': 'form-control'})
    )
    gouvernorat = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les gouvernorats')] + [
            ('ariana', 'Ariana'), ('beja', 'Béja'), ('ben_arous', 'Ben Arous'),
            ('bizerte', 'Bizerte'), ('gabes', 'Gabès'), ('gafsa', 'Gafsa'),
            ('jendouba', 'Jendouba'), ('kairouan', 'Kairouan'), ('kasserine', 'Kasserine'),
            ('kebili', 'Kébili'), ('kef', 'Kef'), ('mahdia', 'Mahdia'),
            ('manouba', 'Manouba'), ('medenine', 'Médenine'), ('monastir', 'Monastir'),
            ('nabeul', 'Nabeul'), ('sfax', 'Sfax'), ('sidi_bouzid', 'Sidi Bouzid'),
            ('siliana', 'Siliana'), ('sousse', 'Sousse'), ('tataouine', 'Tataouine'),
            ('tozeur', 'Tozeur'), ('tunis', 'Tunis'), ('zaghouan', 'Zaghouan'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    dossier_status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les statuts')] + list(DOSSIER_STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
