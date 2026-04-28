import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification, NotificationSettings, EmailLog, AccessLog, LoginVerification


def _generate_code():
    return ''.join(random.choices(string.digits, k=6))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', settings.LOGIN_REDIRECT_URL) or settings.LOGIN_REDIRECT_URL

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'auth/login.html', {
                'form': type('F', (), {'errors': True})(),
                'next': next_url,
            })

        # Credentials valid – generate OTP and email the boss
        code = _generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=10)

        # Invalidate any previous pending verifications for this user
        LoginVerification.objects.filter(user=user, used=False).update(used=True)

        verification = LoginVerification.objects.create(
            user=user,
            code=code,
            expires_at=expires_at,
        )

        boss_email = getattr(settings, 'BOSS_EMAIL', '')
        if boss_email:
            try:
                send_mail(
                    subject=f'[WTI-GC] Code de vérification – {user.username}',
                    message=(
                        f"L'utilisateur « {user.username} » tente de se connecter.\n\n"
                        f"Code de vérification : {code}\n\n"
                        f"Ce code est valable 10 minutes.\n"
                        f"Communiquez ce code uniquement si vous reconnaissez cet utilisateur."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[boss_email],
                    fail_silently=True,
                )
            except Exception:
                pass

        request.session['pending_verification_id'] = verification.pk
        request.session['pending_next'] = next_url
        return redirect('login_verify')

    next_url = request.GET.get('next', '')
    return render(request, 'auth/login.html', {'next': next_url})


def login_verify(request):
    verification_id = request.session.get('pending_verification_id')
    if not verification_id:
        return redirect(settings.LOGIN_URL)

    try:
        verification = LoginVerification.objects.select_related('user').get(pk=verification_id)
    except LoginVerification.DoesNotExist:
        return redirect(settings.LOGIN_URL)

    if not verification.is_valid():
        messages.error(request, 'Le code a expiré ou est déjà utilisé. Veuillez vous reconnecter.')
        return redirect(settings.LOGIN_URL)

    if request.method == 'POST':
        entered = request.POST.get('code', '').strip()
        if entered == verification.code:
            verification.used = True
            verification.save(update_fields=['used'])
            next_url = request.session.pop('pending_next', settings.LOGIN_REDIRECT_URL)
            request.session.pop('pending_verification_id', None)
            login(request, verification.user)
            return redirect(next_url)
        else:
            messages.error(request, 'Code incorrect. Réessayez.')

    return render(request, 'auth/verify.html', {
        'username': verification.user.username,
        'expires_at': verification.expires_at,
    })


@login_required
def notification_list(request):
    notifications = Notification.objects.select_related('project', 'expertise').order_by('-created_at')

    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    notif_type = request.GET.get('type', '')

    if priority:
        notifications = notifications.filter(priority=priority)
    if status:
        notifications = notifications.filter(status=status)
    if notif_type:
        notifications = notifications.filter(notification_type=notif_type)

    paginator = Paginator(notifications, 30)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'notifications_app/list.html', {
        'notifications': page,
        'page_obj': page,
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

    project_settings = [(o, l) for o, l in settings_list if not o.notification_type.startswith('expertise_')]
    expertise_settings = [(o, l) for o, l in settings_list if o.notification_type.startswith('expertise_')]

    return render(request, 'notifications_app/settings.html', {
        'settings_list': settings_list,
        'project_settings': project_settings,
        'expertise_settings': expertise_settings,
    })


@login_required
def email_log_list(request):
    logs = EmailLog.objects.select_related('notification__project', 'notification__expertise')

    success_filter = request.GET.get('success', '')
    if success_filter == '1':
        logs = logs.filter(success=True)
    elif success_filter == '0':
        logs = logs.filter(success=False)

    total = logs.count()
    success_count = logs.filter(success=True).count()
    error_count = logs.filter(success=False).count()

    return render(request, 'notifications_app/email_log.html', {
        'logs': logs[:200],
        'success_filter': success_filter,
        'total': total,
        'success_count': success_count,
        'error_count': error_count,
    })


@login_required
def access_log_list(request):
    logs = AccessLog.objects.select_related('user').order_by('-timestamp')
    event_filter = request.GET.get('event', '')
    if event_filter:
        logs = logs.filter(event=event_filter)
    return render(request, 'notifications_app/access_log.html', {
        'logs': logs[:300],
        'event_filter': event_filter,
        'event_choices': AccessLog.EVENT_CHOICES,
        'forced_count': AccessLog.objects.filter(event=AccessLog.EVENT_FORCED).count(),
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
            'entity_name': n.entity_name,
            'entity_url': n.entity_detail_url,
            'type_label': n.get_notification_type_display(),
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        for n in qs[:8]
    ]
    return JsonResponse({'unread': unread, 'critical': critical, 'recent': recent})
