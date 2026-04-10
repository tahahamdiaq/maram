from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notification, NotificationSettings


@login_required
def notification_list(request):
    notifications = Notification.objects.select_related('project').order_by('-created_at')

    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    notif_type = request.GET.get('type', '')

    if priority:
        notifications = notifications.filter(priority=priority)
    if status:
        notifications = notifications.filter(status=status)
    if notif_type:
        notifications = notifications.filter(notification_type=notif_type)

    return render(request, 'notifications_app/list.html', {
        'notifications': notifications,
        'priority_filter': priority,
        'status_filter': status,
        'type_filter': notif_type,
    })


@login_required
@require_POST
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.status = 'read'
    notif.save(update_fields=['status'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))


@login_required
@require_POST
def notification_mark_processed(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.status = 'processed'
    notif.save(update_fields=['status'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(status='unread').update(status='read')
    messages.success(request, 'Toutes les notifications marquées comme lues.')
    return redirect('notification_list')


@login_required
def notification_settings(request):
    from .models import NOTIFICATION_TYPES
    settings_list = []
    for ntype, label in NOTIFICATION_TYPES:
        obj, _ = NotificationSettings.objects.get_or_create(notification_type=ntype)
        settings_list.append((obj, label))

    if request.method == 'POST':
        for obj, _ in settings_list:
            prefix = f'ns_{obj.notification_type}'
            obj.channel = request.POST.get(f'{prefix}_channel', 'both')
            obj.send_to_project_engineers = f'{prefix}_engineers' in request.POST
            obj.send_to_billing_manager = f'{prefix}_billing' in request.POST
            obj.send_to_admin = f'{prefix}_admin' in request.POST
            obj.extra_emails = request.POST.get(f'{prefix}_extra_emails', '')
            obj.is_active = f'{prefix}_active' in request.POST
            obj.save()
        messages.success(request, 'Paramètres de notifications enregistrés.')
        return redirect('notification_settings')

    return render(request, 'notifications_app/settings.html', {
        'settings_list': settings_list,
    })


@login_required
def notification_api(request):
    """AJAX: return current unread counts and recent notifications."""
    qs = Notification.objects.filter(status='unread').select_related('project').order_by('-created_at')
    unread = qs.count()
    critical = qs.filter(priority='critique').count()
    recent = [
        {
            'id': n.pk,
            'message': n.message,
            'priority': n.priority,
            'color': n.priority_color,
            'icon': n.priority_icon,
            'project_id': n.project_id,
            'project_name': n.project.name,
            'type_label': n.get_notification_type_display(),
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        for n in qs[:8]
    ]
    return JsonResponse({'unread': unread, 'critical': critical, 'recent': recent})
