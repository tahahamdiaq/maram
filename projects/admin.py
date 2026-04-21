from django.contrib import admin
from .models import Project, Engineer, Invoice, ProjectObservation, Expertise, ExpertiseInvoice, ExpertiseObservation


@admin.register(Engineer)
class EngineerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'specialties']
    search_fields = ['name', 'email']


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0


class ObservationInline(admin.TabularInline):
    model = ProjectObservation
    extra = 0
    readonly_fields = ['created_at', 'created_by', 'is_auto']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'bon_commande_number', 'name', 'gouvernorat', 'maitre_ouvrage_type',
        'has_structure', 'has_electricite', 'has_fluide',
        'dao_completed', 'visit_percentage', 'created_at'
    ]
    list_filter = ['gouvernorat', 'maitre_ouvrage_type', 'has_structure', 'has_electricite', 'has_fluide']
    search_fields = ['name', 'bon_commande_number', 'maitre_ouvrage']
    filter_horizontal = ['engineers']
    inlines = [InvoiceInline, ObservationInline]
    readonly_fields = ['created_at', 'updated_at', 'dao_completed_date']

    fieldsets = [
        ('Identité', {
            'fields': ['name', 'bon_commande_number', 'bon_commande_date', 'gouvernorat', 'maitre_ouvrage', 'maitre_ouvrage_type']
        }),
        ('Spécialités & Ingénieurs', {
            'fields': ['has_structure', 'has_electricite', 'has_fluide', 'engineers']
        }),
        ('DAO', {
            'fields': ['dao_structure', 'dao_electricite', 'dao_fluide', 'dao_completed_date']
        }),
        ('D0', {
            'fields': ['d0_done', 'd0_date']
        }),
        ('EXE', {
            'fields': ['exe_structure', 'exe_electricite', 'exe_fluide', 'exe_started_date']
        }),
        ('Visites', {
            'fields': ['planned_visits', 'completed_visits']
        }),
        ('D6 & Réceptions', {
            'fields': ['d6_done', 'd6_date', 'rpro', 'rpro_date', 'rdef', 'rdef_date']
        }),
        ('Métadonnées', {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def dao_completed(self, obj):
        return obj.dao_completed
    dao_completed.boolean = True
    dao_completed.short_description = 'DAO complet'

    def visit_percentage(self, obj):
        return f"{obj.visit_percentage}%"
    visit_percentage.short_description = '% visites'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['project', 'invoice_number', 'establishment_date', 'transmission_date']
    list_filter = ['invoice_number']
    search_fields = ['project__name', 'project__bon_commande_number']


class ExpertiseInvoiceInline(admin.TabularInline):
    model = ExpertiseInvoice
    extra = 0


class ExpertiseObservationInline(admin.TabularInline):
    model = ExpertiseObservation
    extra = 0
    readonly_fields = ['created_at', 'created_by', 'is_auto']


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['bon_commande_number', 'name', 'gouvernorat', 'maitre_ouvrage_type', 'dossier_status', 'dossier_completed_date']
    list_filter = ['gouvernorat', 'maitre_ouvrage_type', 'dossier_status']
    search_fields = ['name', 'bon_commande_number', 'maitre_ouvrage']
    filter_horizontal = ['engineers']
    inlines = [ExpertiseInvoiceInline, ExpertiseObservationInline]
