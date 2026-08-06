from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_expertise_simplify_rapport_status'),
    ]

    operations = [
        # Expertise: rapport_final_date + cloturee choice
        migrations.AddField(
            model_name='expertise',
            name='rapport_final_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date rapport final'),
        ),
        migrations.AlterField(
            model_name='expertise',
            name='rapport_status',
            field=models.CharField(
                choices=[
                    ('non_effectue', 'Non encore effectué'),
                    ('en_cours', 'En cours'),
                    ('cloturee', 'Cloturée'),
                ],
                default='non_effectue',
                max_length=20,
                verbose_name='Statut du rapport',
            ),
        ),

        # Project: has_vrd + DAO VRD + EXE VRD
        migrations.AddField(
            model_name='project',
            name='has_vrd',
            field=models.BooleanField(default=False, verbose_name='VRD'),
        ),
        migrations.AddField(
            model_name='project',
            name='dao_vrd',
            field=models.CharField(
                choices=[
                    ('non_prevu', 'Non prévu'),
                    ('non_recu', 'Dossier non reçu'),
                    ('non_approuve', 'Dossier non approuvé'),
                    ('en_cours', 'En cours de vérification'),
                    ('approuve', 'Approuvé'),
                ],
                default='non_prevu',
                max_length=20,
                verbose_name='DAO VRD',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='dao_vrd_received_date',
            field=models.DateField(blank=True, null=True, verbose_name='DAO VRD – Date réception'),
        ),
        migrations.AddField(
            model_name='project',
            name='dao_vrd_decision_date',
            field=models.DateField(blank=True, null=True, verbose_name='DAO VRD – Date décision'),
        ),
        migrations.AddField(
            model_name='project',
            name='exe_vrd',
            field=models.CharField(
                choices=[
                    ('non_prevu', 'Non prévu'),
                    ('non_recu', 'Dossier non reçu'),
                    ('non_approuve', 'Dossier non approuvé'),
                    ('en_cours', 'En cours de vérification'),
                    ('approuve', 'Approuvé'),
                ],
                default='non_prevu',
                max_length=20,
                verbose_name='EXE VRD',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='exe_vrd_received_date',
            field=models.DateField(blank=True, null=True, verbose_name='EXE VRD – Date réception'),
        ),
        migrations.AddField(
            model_name='project',
            name='exe_vrd_decision_date',
            field=models.DateField(blank=True, null=True, verbose_name='EXE VRD – Date décision'),
        ),
    ]
