from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications_app', '0005_loginverification'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeleteVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, verbose_name='Code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(verbose_name='Expiration')),
                ('used', models.BooleanField(default=False)),
                ('project', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='delete_verifications',
                    to='projects.project',
                    verbose_name='Projet',
                )),
                ('expertise', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='delete_verifications',
                    to='projects.expertise',
                    verbose_name='Expertise',
                )),
                ('requested_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='delete_verifications',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Demandé par',
                )),
            ],
            options={
                'verbose_name': 'Vérification de suppression',
                'verbose_name_plural': 'Vérifications de suppression',
                'ordering': ['-created_at'],
            },
        ),
    ]
