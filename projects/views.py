import re
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Project, Invoice, ProjectObservation, Engineer, Expertise, ExpertiseInvoice, ExpertiseObservation
from .forms import ProjectForm, InvoiceForm, ObservationForm, EngineerForm, ProjectFilterForm, ExpertiseForm, ExpertiseInvoiceForm, ExpertiseFilterForm
from notifications_app.services import check_project_notifications, check_expertise_notifications


# ─── Dashboard / Project List ─────────────────────────────────────────────────

@login_required
def project_list(request):
    form = ProjectFilterForm(request.GET or None)
    projects = Project.objects.prefetch_related('engineers', 'invoices', 'notifications').all()

    if form.is_valid():
        search = form.cleaned_data.get('search')
        gouvernorat = form.cleaned_data.get('gouvernorat')
        specialty = form.cleaned_data.get('specialty')
        maitre_ouvrage = form.cleaned_data.get('maitre_ouvrage')
        notif_filter = form.cleaned_data.get('notification_filter')

        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(bon_commande_number__icontains=search) |
                Q(maitre_ouvrage__icontains=search)
            )
        if gouvernorat:
            projects = projects.filter(gouvernorat=gouvernorat)
        if specialty == 'structure':
            projects = projects.filter(has_structure=True)
        elif specialty == 'electricite':
            projects = projects.filter(has_electricite=True)
        elif specialty == 'fluide':
            projects = projects.filter(has_fluide=True)
        elif specialty == 'securite_incendie':
            projects = projects.filter(has_securite_incendie=True)
        if maitre_ouvrage:
            projects = projects.filter(maitre_ouvrage__icontains=maitre_ouvrage)
        if notif_filter:
            projects = _apply_notification_filter(projects, notif_filter)

    # Stats for dashboard cards
    total = projects.count()
    from notifications_app.models import Notification
    critical_count = Notification.objects.filter(priority='critique', status='unread').count()

    return render(request, 'projects/list.html', {
        'projects': projects,
        'filter_form': form,
        'total': total,
        'critical_count': critical_count,
    })


def _apply_notification_filter(qs, notif_filter):
    from notifications_app.models import Notification
    if notif_filter == 'facture1':
        ids = Notification.objects.filter(
            notification_type__in=['facture1_ready', 'facture1_j7', 'facture1_j2', 'facture1_overdue'],
            status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    elif notif_filter == 'facture2':
        ids = Notification.objects.filter(
            notification_type='facture2_ready', status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    elif notif_filter == 'facture3':
        ids = Notification.objects.filter(
            notification_type='facture3_ready', status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    elif notif_filter == 'd0':
        ids = Notification.objects.filter(
            notification_type='d0_reminder', status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    elif notif_filter == 'd6':
        ids = Notification.objects.filter(
            notification_type='d6_reminder', status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    elif notif_filter == 'critique':
        ids = Notification.objects.filter(
            priority='critique', status__in=['unread', 'read']
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=ids)
    return qs


# ─── Project Detail ───────────────────────────────────────────────────────────

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('engineers', 'invoices', 'observations', 'notifications'),
        pk=pk
    )
    obs_form = ObservationForm()
    return render(request, 'projects/detail.html', {
        'project': project,
        'obs_form': obs_form,
        'invoices': {inv.invoice_number: inv for inv in project.invoices.all()},
        'observations': project.observations.all(),
        'notifications': project.notifications.filter(status__in=['unread', 'read']).order_by('-created_at'),
    })


# ─── Create / Edit Project ────────────────────────────────────────────────────

_SPEC_META = [
    ('structure',         'STR',  'spec-str'),
    ('electricite',       'ELEC', 'spec-elec'),
    ('fluide',            'FL',   'spec-fl'),
    ('securite_incendie', 'SI',   'spec-si'),
]

def _project_form_context(form):
    dao_specs, exe_specs = [], []
    for key, label, css in _SPEC_META:
        dao_specs.append((
            key, label, css,
            form[f'dao_{key}'],
            form[f'dao_{key}_received_date'],
            form[f'dao_{key}_decision_date'],
        ))
        exe_specs.append((
            key, label, css,
            form[f'exe_{key}'],
            form[f'exe_{key}_received_date'],
            form[f'exe_{key}_decision_date'],
        ))
    return {'dao_specs': dao_specs, 'exe_specs': exe_specs}


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()
            for n in [1, 2, 3]:
                Invoice.objects.get_or_create(project=project, invoice_number=n)
            check_project_notifications(project)
            messages.success(request, f'Projet "{project.name}" créé avec succès.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/form.html', {'form': form, 'action': 'Créer', **_project_form_context(form)})


_DOSSIER_FIELDS = [
    ('dao_structure',         'DAO Structure'),
    ('dao_electricite',       'DAO Électricité'),
    ('dao_fluide',            'DAO Fluide'),
    ('dao_securite_incendie', 'DAO Sécurité incendie'),
    ('exe_structure',         'EXE Structure'),
    ('exe_electricite',       'EXE Électricité'),
    ('exe_fluide',            'EXE Fluide'),
    ('exe_securite_incendie', 'EXE Sécurité incendie'),
]

_EXPERTISE_DOSSIER_FIELDS = [
    ('dossier_structure',         'Dossier Structure'),
    ('dossier_electricite',       'Dossier Électricité'),
    ('dossier_fluide',            'Dossier Fluide'),
    ('dossier_securite_incendie', 'Dossier Sécurité incendie'),
]

def _handle_dossier_changes(instance, old_statuses, field_pairs, observation_class, obs_kwargs, user):
    from .models import STATUS_CHOICES
    status_labels = dict(STATUS_CHOICES)
    date_updates = {}
    obs_list = []

    for field, label in field_pairs:
        new_status = getattr(instance, field)
        old_status = old_statuses.get(field)
        if new_status != old_status:
            obs_list.append(observation_class(
                **obs_kwargs,
                date=date.today(),
                text=f'{label} : {status_labels.get(old_status, old_status)} → {status_labels.get(new_status, new_status)}',
                is_auto=True,
                created_by=user,
            ))
            received_field = f'{field}_received_date'
            decision_field = f'{field}_decision_date'
            if new_status == 'en_cours' and not getattr(instance, received_field, None):
                date_updates[received_field] = date.today()
            elif new_status in ('approuve', 'non_approuve') and not getattr(instance, decision_field, None):
                date_updates[decision_field] = date.today()

    if obs_list:
        observation_class.objects.bulk_create(obs_list)
    if date_updates:
        for f, v in date_updates.items():
            setattr(instance, f, v)
        instance.save(update_fields=list(date_updates.keys()))


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        old_engineers = set(project.engineers.values_list('pk', flat=True))
        old_statuses = {f: getattr(project, f) for f, _ in _DOSSIER_FIELDS}
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            new_engineers = set(project.engineers.values_list('pk', flat=True))
            if new_engineers - old_engineers:
                project.notifications.filter(
                    status__in=['unread', 'read'], email_sent=True
                ).update(email_sent=False)
            _handle_dossier_changes(
                project, old_statuses, _DOSSIER_FIELDS,
                ProjectObservation, {'project': project}, request.user
            )
            check_project_notifications(project)
            messages.success(request, 'Projet mis à jour avec succès.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/form.html', {'form': form, 'project': project, 'action': 'Modifier', **_project_form_context(form)})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        from notifications_app.models import DeleteVerification
        from notifications_app.views import _generate_code
        from notifications_app.pdf_utils import build_project_pdf
        from django.conf import settings
        from django.core.mail import EmailMessage
        from django.utils import timezone

        code = _generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=15)

        DeleteVerification.objects.filter(project=project, used=False).update(used=True)
        verification = DeleteVerification.objects.create(
            project=project,
            code=code,
            expires_at=expires_at,
            requested_by=request.user,
        )

        boss_email = getattr(settings, 'BOSS_EMAIL', '')
        if boss_email:
            try:
                pdf_bytes = build_project_pdf(project)
                email = EmailMessage(
                    subject=f'[WTI-GC] Suppression projet – {project.bon_commande_number} {project.name}',
                    body=(
                        f'L\'utilisateur « {request.user.username} » demande la suppression du projet :\n\n'
                        f'  Nom       : {project.name}\n'
                        f'  N° BC     : {project.bon_commande_number}\n'
                        f'  Gouvernorat: {project.get_gouvernorat_display()}\n\n'
                        f'Code de confirmation : {code}\n\n'
                        f'Ce code est valable 15 minutes.\n'
                        f'Communiquez ce code uniquement si vous autorisez cette suppression.\n'
                        f'La fiche complète du projet est jointe en PDF.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[boss_email],
                )
                email.attach(
                    f'projet_{project.bon_commande_number}.pdf',
                    pdf_bytes,
                    'application/pdf',
                )
                email.send(fail_silently=True)
            except Exception:
                pass

        request.session['pending_delete_id'] = verification.pk
        return redirect('project_delete_verify', pk=pk)

    return render(request, 'projects/confirm_delete.html', {'project': project})


@login_required
def project_delete_verify(request, pk):
    from notifications_app.models import DeleteVerification
    project = get_object_or_404(Project, pk=pk)
    verification_id = request.session.get('pending_delete_id')
    if not verification_id:
        messages.error(request, 'Session expirée. Recommencez la suppression.')
        return redirect('project_delete', pk=pk)

    try:
        verification = DeleteVerification.objects.get(pk=verification_id, project=project)
    except DeleteVerification.DoesNotExist:
        messages.error(request, 'Vérification introuvable. Recommencez.')
        return redirect('project_delete', pk=pk)

    if not verification.is_valid():
        messages.error(request, 'Le code a expiré. Recommencez la suppression.')
        return redirect('project_delete', pk=pk)

    if request.method == 'POST':
        entered = request.POST.get('code', '').strip()
        if entered == verification.code:
            verification.used = True
            verification.save(update_fields=['used'])
            request.session.pop('pending_delete_id', None)
            name = project.name
            project.delete()
            messages.success(request, f'Projet "{name}" supprimé.')
            return redirect('project_list')
        else:
            messages.error(request, 'Code incorrect. Réessayez.')

    return render(request, 'projects/delete_verify.html', {
        'project': project,
        'expires_at': verification.expires_at,
    })


# ─── Invoice management ───────────────────────────────────────────────────────

@login_required
def invoice_edit(request, project_pk, invoice_number):
    project = get_object_or_404(Project, pk=project_pk)
    invoice, _ = Invoice.objects.get_or_create(project=project, invoice_number=invoice_number)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            check_project_notifications(project)
            messages.success(request, f'Facture N°{invoice_number} mise à jour.')
            return redirect('project_detail', pk=project_pk)
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'projects/invoice_form.html', {
        'form': form,
        'project': project,
        'invoice_number': invoice_number,
    })


# ─── Observations ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def observation_add(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    form = ObservationForm(request.POST)
    if form.is_valid():
        obs = form.save(commit=False)
        obs.project = project
        obs.created_by = request.user
        obs.save()
        messages.success(request, 'Observation ajoutée.')
    else:
        messages.error(request, 'Erreur lors de l\'ajout de l\'observation.')
    return redirect('project_detail', pk=project_pk)


@login_required
def observation_delete(request, pk):
    obs = get_object_or_404(ProjectObservation, pk=pk, is_auto=False)
    project_pk = obs.project_id
    obs.delete()
    messages.success(request, 'Observation supprimée.')
    return redirect('project_detail', pk=project_pk)


# ─── Engineers ────────────────────────────────────────────────────────────────

@login_required
def engineer_list(request):
    engineers = Engineer.objects.all()
    return render(request, 'projects/engineers.html', {'engineers': engineers})


@login_required
def engineer_create(request):
    if request.method == 'POST':
        form = EngineerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingénieur créé.')
            return redirect('engineer_list')
    else:
        form = EngineerForm()
    return render(request, 'projects/engineer_form.html', {'form': form, 'action': 'Créer'})


@login_required
def engineer_edit(request, pk):
    engineer = get_object_or_404(Engineer, pk=pk)
    if request.method == 'POST':
        form = EngineerForm(request.POST, instance=engineer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingénieur mis à jour.')
            return redirect('engineer_list')
    else:
        form = EngineerForm(instance=engineer)
    return render(request, 'projects/engineer_form.html', {'form': form, 'engineer': engineer, 'action': 'Modifier'})


@login_required
@require_POST
def engineer_delete(request, pk):
    engineer = get_object_or_404(Engineer, pk=pk)
    name = engineer.name
    engineer.delete()
    messages.success(request, f'Ingénieur "{name}" supprimé.')
    return redirect('engineer_list')


# ─── Expertises ───────────────────────────────────────────────────────────────

@login_required
def expertise_list(request):
    form = ExpertiseFilterForm(request.GET or None)
    expertises = Expertise.objects.prefetch_related('engineers', 'invoices', 'notifications').all()

    if form.is_valid():
        search = form.cleaned_data.get('search')
        gouvernorat = form.cleaned_data.get('gouvernorat')
        dossier_status = form.cleaned_data.get('dossier_status')
        if search:
            from django.db.models import Q
            expertises = expertises.filter(
                Q(name__icontains=search) |
                Q(bon_commande_number__icontains=search) |
                Q(maitre_ouvrage__icontains=search)
            )
        if gouvernorat:
            expertises = expertises.filter(gouvernorat=gouvernorat)
        if dossier_status:
            from django.db.models import Q as _Q; expertises = expertises.filter(_Q(dossier_structure=dossier_status) | _Q(dossier_electricite=dossier_status) | _Q(dossier_fluide=dossier_status) | _Q(dossier_securite_incendie=dossier_status))

    from notifications_app.models import Notification
    critical_count = Notification.objects.filter(
        expertise__isnull=False, priority='critique', status='unread'
    ).count()

    return render(request, 'projects/expertise_list.html', {
        'expertises': expertises,
        'filter_form': form,
        'total': expertises.count(),
        'critical_count': critical_count,
    })


@login_required
def expertise_detail(request, pk):
    expertise = get_object_or_404(
        Expertise.objects.prefetch_related('engineers', 'invoices', 'observations', 'notifications'),
        pk=pk
    )
    invoice = expertise.get_invoice
    notifications = expertise.notifications.filter(status__in=['unread', 'read']).order_by('-created_at')
    return render(request, 'projects/expertise_detail.html', {
        'expertise': expertise,
        'invoice': invoice,
        'observations': expertise.observations.all(),
        'notifications': notifications,
    })


@login_required
def expertise_create(request):
    if request.method == 'POST':
        form = ExpertiseForm(request.POST)
        if form.is_valid():
            expertise = form.save(commit=False)
            expertise.created_by = request.user
            expertise.save()
            form.save_m2m()
            ExpertiseInvoice.objects.create(expertise=expertise)
            check_expertise_notifications(expertise)
            messages.success(request, f'Expertise "{expertise.name}" créée avec succès.')
            return redirect('expertise_detail', pk=expertise.pk)
    else:
        form = ExpertiseForm()
    return render(request, 'projects/expertise_form.html', {'form': form, 'action': 'Créer'})


@login_required
def expertise_edit(request, pk):
    expertise = get_object_or_404(Expertise, pk=pk)
    if request.method == 'POST':
        old_engineers = set(expertise.engineers.values_list('pk', flat=True))
        old_statuses = {f: getattr(expertise, f) for f, _ in _EXPERTISE_DOSSIER_FIELDS}
        form = ExpertiseForm(request.POST, instance=expertise)
        if form.is_valid():
            form.save()
            new_engineers = set(expertise.engineers.values_list('pk', flat=True))
            if new_engineers - old_engineers:
                expertise.notifications.filter(
                    status__in=['unread', 'read'], email_sent=True
                ).update(email_sent=False)
            _handle_dossier_changes(
                expertise, old_statuses, _EXPERTISE_DOSSIER_FIELDS,
                ExpertiseObservation, {'expertise': expertise}, request.user
            )
            check_expertise_notifications(expertise)
            messages.success(request, 'Expertise mise à jour.')
            return redirect('expertise_detail', pk=expertise.pk)
    else:
        form = ExpertiseForm(instance=expertise)
    return render(request, 'projects/expertise_form.html', {'form': form, 'expertise': expertise, 'action': 'Modifier'})


@login_required
def expertise_delete(request, pk):
    expertise = get_object_or_404(Expertise, pk=pk)
    if request.method == 'POST':
        name = expertise.name
        expertise.delete()
        messages.success(request, f'Expertise "{name}" supprimée.')
        return redirect('expertise_list')
    return render(request, 'projects/expertise_confirm_delete.html', {'expertise': expertise})


@login_required
def expertise_invoice_edit(request, expertise_pk):
    expertise = get_object_or_404(Expertise, pk=expertise_pk)
    invoice, _ = ExpertiseInvoice.objects.get_or_create(expertise=expertise)
    if request.method == 'POST':
        form = ExpertiseInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            check_expertise_notifications(expertise)
            messages.success(request, 'Facture mise à jour.')
            return redirect('expertise_detail', pk=expertise_pk)
    else:
        form = ExpertiseInvoiceForm(instance=invoice)
    return render(request, 'projects/expertise_invoice_form.html', {
        'form': form,
        'expertise': expertise,
    })


@login_required
@require_POST
def expertise_observation_add(request, expertise_pk):
    expertise = get_object_or_404(Expertise, pk=expertise_pk)
    text = request.POST.get('text', '').strip()
    obs_date = request.POST.get('date', '')
    if text and obs_date:
        ExpertiseObservation.objects.create(
            expertise=expertise,
            date=obs_date,
            text=text,
            created_by=request.user,
        )
        messages.success(request, 'Observation ajoutée.')
    return redirect('expertise_detail', pk=expertise_pk)


@login_required
def expertise_observation_delete(request, pk):
    obs = get_object_or_404(ExpertiseObservation, pk=pk, is_auto=False)
    expertise_pk = obs.expertise_id
    obs.delete()
    messages.success(request, 'Observation supprimée.')
    return redirect('expertise_detail', pk=expertise_pk)


# ─── PDF export ──────────────────────────────────────────────────────────────

@login_required
def expertise_list_export_pdf(request):
    from django.http import HttpResponse
    from notifications_app.pdf_utils import build_expertise_list_pdf

    expertises = Expertise.objects.prefetch_related('engineers', 'invoices').all()
    form = ExpertiseFilterForm(request.GET or None)
    if form.is_valid():
        search         = form.cleaned_data.get('search')
        gouvernorat    = form.cleaned_data.get('gouvernorat')
        dossier_status = form.cleaned_data.get('dossier_status')
        if search:
            expertises = expertises.filter(
                Q(name__icontains=search) |
                Q(bon_commande_number__icontains=search) |
                Q(maitre_ouvrage__icontains=search)
            )
        if gouvernorat:
            expertises = expertises.filter(gouvernorat=gouvernorat)
        if dossier_status:
            from django.db.models import Q as _Q; expertises = expertises.filter(_Q(dossier_structure=dossier_status) | _Q(dossier_electricite=dossier_status) | _Q(dossier_fluide=dossier_status) | _Q(dossier_securite_incendie=dossier_status))

    pdf_bytes = build_expertise_list_pdf(expertises)
    filename = f'{date.today().isoformat()}-WTI-GC.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def project_list_export_pdf(request):
    from django.http import HttpResponse
    from notifications_app.pdf_utils import build_project_list_pdf

    projects = Project.objects.prefetch_related('engineers').all()
    form = ProjectFilterForm(request.GET or None)
    if form.is_valid():
        search        = form.cleaned_data.get('search')
        gouvernorat   = form.cleaned_data.get('gouvernorat')
        specialty     = form.cleaned_data.get('specialty')
        maitre_ouvrage = form.cleaned_data.get('maitre_ouvrage')
        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(bon_commande_number__icontains=search) |
                Q(maitre_ouvrage__icontains=search)
            )
        if gouvernorat:
            projects = projects.filter(gouvernorat=gouvernorat)
        if specialty == 'structure':
            projects = projects.filter(has_structure=True)
        elif specialty == 'electricite':
            projects = projects.filter(has_electricite=True)
        elif specialty == 'fluide':
            projects = projects.filter(has_fluide=True)
        elif specialty == 'securite_incendie':
            projects = projects.filter(has_securite_incendie=True)
        if maitre_ouvrage:
            projects = projects.filter(maitre_ouvrage__icontains=maitre_ouvrage)

    pdf_bytes = build_project_list_pdf(projects)
    filename = f'{date.today().isoformat()}-WTI-GC.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def project_export_pdf(request, pk):
    from django.http import HttpResponse
    from notifications_app.pdf_utils import build_project_pdf
    project = get_object_or_404(
        Project.objects.prefetch_related('engineers', 'invoices', 'observations'),
        pk=pk,
    )
    pdf_bytes = build_project_pdf(project)
    safe_name = re.sub(r'[^\w\-]', '_', project.name)[:80]
    filename = f'{date.today().isoformat()}-{safe_name}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def expertise_export_pdf(request, pk):
    from django.http import HttpResponse
    from notifications_app.pdf_utils import build_expertise_pdf
    expertise = get_object_or_404(
        Expertise.objects.prefetch_related('engineers', 'invoices', 'observations'),
        pk=pk,
    )
    pdf_bytes = build_expertise_pdf(expertise)
    safe_name = re.sub(r'[^\w\-]', '_', expertise.name)[:80]
    filename = f'{date.today().isoformat()}-{safe_name}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ─── AJAX endpoint for notification count ─────────────────────────────────────

@login_required
def notification_count_api(request):
    from notifications_app.models import Notification
    unread = Notification.objects.filter(status='unread').count()
    critical = Notification.objects.filter(status='unread', priority='critique').count()
    return JsonResponse({'unread': unread, 'critical': critical})
