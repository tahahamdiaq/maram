from django import forms
from django.utils.safestring import mark_safe
from .models import Project, Invoice, ProjectObservation, Engineer, STATUS_CHOICES, Expertise, ExpertiseInvoice


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            # Identité
            'name', 'bon_commande_number', 'bon_commande_date',
            'gouvernorat', 'maitre_ouvrage', 'maitre_ouvrage_type',
            # Spécialités
            'has_structure', 'has_electricite', 'has_fluide',
            # Ingénieurs
            'engineers',
            # Visites
            'planned_visits', 'completed_visits',
            # DAO
            'dao_structure', 'dao_electricite', 'dao_fluide', 'dao_completed_date',
            # D0
            'd0_done', 'd0_date',
            # EXE
            'exe_structure', 'exe_electricite', 'exe_fluide',
            # D6
            'd6_done', 'd6_date',
            # Réceptions
            'rpro', 'rpro_date', 'rdef', 'rdef_date',
        ]
        widgets = {
            'bon_commande_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dao_completed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'd0_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'd6_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rpro_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rdef_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'engineers': forms.CheckboxSelectMultiple(),
            'maitre_ouvrage': forms.TextInput(attrs={'list': 'maitre-ouvrage-list'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark date fields as not required by default
        for field_name in ['dao_completed_date', 'd0_date', 'd6_date', 'rpro_date', 'rdef_date']:
            self.fields[field_name].required = False

        # DAO fields: only required when specialty is selected (handled in JS)
        for f in ['dao_structure', 'dao_electricite', 'dao_fluide',
                  'exe_structure', 'exe_electricite', 'exe_fluide']:
            self.fields[f].required = False

    def clean(self):
        cleaned = super().clean()
        # At least one specialty required
        if not any([cleaned.get('has_structure'), cleaned.get('has_electricite'), cleaned.get('has_fluide')]):
            raise forms.ValidationError("Veuillez sélectionner au moins une spécialité.")

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
    class Meta:
        model = Engineer
        fields = ['name', 'email', 'phone', 'specialties']
        widgets = {
            'specialties': forms.TextInput(attrs={'placeholder': 'Ex: Structure, Électricité'}),
        }


class ProjectFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher un projet…', 'class': 'form-control'})
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
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    maitre_ouvrage = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Tous les maîtres d\'ouvrage'),
            ('DRE', 'DRE'),
            ('CRE', 'CRE'),
            ('autre', 'Autre'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
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
            'gouvernorat', 'maitre_ouvrage', 'maitre_ouvrage_type',
            'has_structure', 'has_electricite', 'has_fluide',
            'engineers',
            'dossier_status', 'dossier_completed_date',
        ]
        widgets = {
            'bon_commande_date':      forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'dossier_completed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'engineers':              forms.CheckboxSelectMultiple(),
            'maitre_ouvrage':         forms.TextInput(attrs={'list': 'maitre-ouvrage-list'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dossier_completed_date'].required = False
        self.fields['dossier_status'].required = False

    def clean(self):
        cleaned = super().clean()
        if not any([cleaned.get('has_structure'), cleaned.get('has_electricite'), cleaned.get('has_fluide')]):
            raise forms.ValidationError("Veuillez sélectionner au moins une spécialité.")
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
        choices=[('', 'Tous les statuts')] + list(STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
