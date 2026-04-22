from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications_app', '0004_accesslog_usersession'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, verbose_name='Code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(verbose_name='Expiration')),
                ('used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='login_verifications',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Vérification de connexion',
                'verbose_name_plural': 'Vérifications de connexion',
                'ordering': ['-created_at'],
            },
        ),
    ]
