"""
Management command to check and generate notifications.
Run via cron: python manage.py check_notifications [--send-emails]

Example crontab (every hour):
  0 * * * * /path/to/venv/bin/python /path/to/manage.py check_notifications --send-emails
"""
from django.core.management.base import BaseCommand
from notifications_app.services import check_all_notifications
from notifications_app.email_service import send_pending_emails


class Command(BaseCommand):
    help = 'Vérifie les conditions métier et génère les notifications nécessaires.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-emails',
            action='store_true',
            help='Envoyer les emails pour les notifications non encore envoyées.',
        )

    def handle(self, *args, **options):
        self.stdout.write('Vérification des notifications...')
        check_all_notifications()
        self.stdout.write(self.style.SUCCESS('Notifications mises à jour.'))

        if options['send_emails']:
            self.stdout.write('Envoi des emails...')
            sent = send_pending_emails()
            self.stdout.write(self.style.SUCCESS(f'{sent} email(s) envoyé(s).'))
