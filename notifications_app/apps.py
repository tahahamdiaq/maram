from django.apps import AppConfig


class NotificationsAppConfig(AppConfig):
    name = 'notifications_app'

    def ready(self):
        import notifications_app.security  # noqa: F401 – connects login/logout signals
