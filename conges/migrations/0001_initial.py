import decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Employe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_prenoms', models.CharField(max_length=200, verbose_name='Nom & prénoms')),
                ('matricule', models.CharField(blank=True, max_length=50, verbose_name='Matricule')),
                ('fonction', models.CharField(blank=True, max_length=150, verbose_name='Fonction')),
                ('direction', models.CharField(blank=True, max_length=150, verbose_name='Direction')),
                ('date_embauche', models.DateField(verbose_name="Date d'embauche")),
                ('droit_jours_par_mois', models.DecimalField(decimal_places=2, default=decimal.Decimal('2.2'), help_text='2,2 jours/mois = minimum légal ivoirien (26,4 jours/an). Modifiable si la convention ou le contrat prévoit mieux.', max_digits=4, verbose_name='Droit à congé (jours par mois)')),
                ('actif', models.BooleanField(default=True, verbose_name="Actif dans l'entreprise")),
            ],
            options={
                'verbose_name': 'Employé',
                'verbose_name_plural': 'Employés',
                'ordering': ['nom_prenoms'],
            },
        ),
        migrations.CreateModel(
            name='DemandeConge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_retour_dernier_conge', models.DateField(blank=True, null=True, verbose_name='Date de retour du dernier congé')),
                ('date_depart', models.DateField(verbose_name='Date de départ')),
                ('duree_conge', models.PositiveIntegerField(help_text='Nombre de jours calendaires, départ inclus.', verbose_name='Durée du congé (jours)')),
                ('date_reprise', models.DateField(blank=True, help_text='Calculée automatiquement si laissée vide (départ + durée).', null=True, verbose_name='Date de reprise')),
                ('contact', models.CharField(blank=True, max_length=200, verbose_name='Contact(s)')),
                ('statut', models.CharField(choices=[('attente', 'En attente'), ('validee', 'Validée'), ('refusee', 'Refusée')], default='attente', max_length=10, verbose_name='Statut')),
                ('avis_chef', models.CharField(blank=True, choices=[('oui', 'Oui'), ('non', 'Non')], max_length=3, verbose_name='Avis du chef hiérarchique direct')),
                ('commentaire', models.TextField(blank=True, verbose_name='Commentaire / observations')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_maj', models.DateTimeField(auto_now=True)),
                ('employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes', to='conges.employe', verbose_name='Employé')),
            ],
            options={
                'verbose_name': 'Demande de congé',
                'verbose_name_plural': 'Demandes de congé',
                'ordering': ['-date_depart'],
            },
        ),
    ]
