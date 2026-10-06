"""
Modèles de l'application de gestion des congés.

Règle de calcul par défaut : un employé acquiert 2,2 jours ouvrables de congé
par mois de service effectif (soit 26,4 jours/an), ce qui correspond au
minimum légal usuel en Côte d'Ivoire. Ce taux est modifiable par employé.
"""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse

TWO_PLACES = Decimal('0.01')


class Employe(models.Model):
    nom_prenoms = models.CharField("Nom & prénoms", max_length=200)
    matricule = models.CharField("Matricule", max_length=50, blank=True)
    fonction = models.CharField("Fonction", max_length=150, blank=True)
    direction = models.CharField("Direction", max_length=150, blank=True)
    date_embauche = models.DateField("Date d'embauche")
    droit_jours_par_mois = models.DecimalField(
        "Droit à congé (jours par mois)",
        max_digits=4,
        decimal_places=2,
        default=Decimal(str(getattr(settings, 'DROIT_JOURS_PAR_MOIS_DEFAUT', 2.2))),
        help_text="2,2 jours/mois = minimum légal ivoirien (26,4 jours/an). "
                   "Modifiable si la convention ou le contrat prévoit mieux.",
    )
    actif = models.BooleanField("Actif dans l'entreprise", default=True)

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['nom_prenoms']

    def __str__(self):
        return self.nom_prenoms

    def get_absolute_url(self):
        return reverse('conges:employe-detail', args=[self.pk])

    # ------------------------------------------------------------------
    # Calculs de congés
    # ------------------------------------------------------------------
    def mois_service(self, a_date=None):
        """Nombre de mois complets de service entre la date d'embauche et a_date."""
        a_date = a_date or date.today()
        debut = self.date_embauche
        if not debut or a_date < debut:
            return 0
        mois = (a_date.year - debut.year) * 12 + (a_date.month - debut.month)
        if a_date.day < debut.day:
            mois -= 1
        return max(mois, 0)

    def droits_acquis(self, a_date=None):
        """Total des jours de congé acquis depuis l'embauche, à une date donnée."""
        mois = self.mois_service(a_date)
        total = Decimal(mois) * self.droit_jours_par_mois
        return total.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    def jours_pris(self, a_date=None):
        """Somme des jours de congé des demandes validées, déjà entamées à a_date."""
        a_date = a_date or date.today()
        total = self.demandes.filter(
            statut=DemandeConge.STATUT_VALIDEE,
            date_depart__lte=a_date,
        ).aggregate(total=Sum('duree_conge'))['total']
        return Decimal(total or 0)

    def jours_planifies_non_valides(self, a_date=None):
        """Jours des demandes encore en attente (pour information, non déduits du solde)."""
        total = self.demandes.filter(
            statut=DemandeConge.STATUT_ATTENTE,
        ).aggregate(total=Sum('duree_conge'))['total']
        return Decimal(total or 0)

    def solde(self, a_date=None):
        """Solde de congés = droits acquis - jours déjà pris (demandes validées)."""
        return self.droits_acquis(a_date) - self.jours_pris(a_date)

    def derniere_demande(self):
        return self.demandes.order_by('-date_depart').first()


class DemandeConge(models.Model):
    STATUT_ATTENTE = 'attente'
    STATUT_VALIDEE = 'validee'
    STATUT_REFUSEE = 'refusee'
    STATUT_CHOICES = [
        (STATUT_ATTENTE, 'En attente'),
        (STATUT_VALIDEE, 'Validée'),
        (STATUT_REFUSEE, 'Refusée'),
    ]

    AVIS_CHOICES = [
        ('oui', 'Oui'),
        ('non', 'Non'),
    ]

    employe = models.ForeignKey(
        Employe, on_delete=models.CASCADE, related_name='demandes',
        verbose_name="Employé",
    )
    date_retour_dernier_conge = models.DateField(
        "Date de retour du dernier congé", null=True, blank=True,
    )
    date_depart = models.DateField("Date de départ")
    duree_conge = models.PositiveIntegerField(
        "Durée du congé (jours)",
        help_text="Nombre de jours calendaires, départ inclus.",
    )
    date_reprise = models.DateField(
        "Date de reprise", null=True, blank=True,
        help_text="Calculée automatiquement si laissée vide (départ + durée).",
    )
    contact = models.CharField("Contact(s)", max_length=200, blank=True)

    statut = models.CharField(
        "Statut", max_length=10, choices=STATUT_CHOICES, default=STATUT_ATTENTE,
    )
    avis_chef = models.CharField(
        "Avis du chef hiérarchique direct", max_length=3,
        choices=AVIS_CHOICES, blank=True,
    )
    commentaire = models.TextField("Commentaire / observations", blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congé"
        ordering = ['-date_depart']

    def __str__(self):
        return f"{self.employe} — départ {self.date_depart:%d/%m/%Y}"

    def get_absolute_url(self):
        return reverse('conges:demande-detail', args=[self.pk])

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_depart and self.date_reprise and self.date_reprise <= self.date_depart:
            raise ValidationError(
                {'date_reprise': "La date de reprise doit être après la date de départ."}
            )

    def save(self, *args, **kwargs):
        # Calcule automatiquement la date de reprise si elle n'est pas fournie.
        if self.date_depart and self.duree_conge and not self.date_reprise:
            self.date_reprise = self.date_depart + timedelta(days=self.duree_conge)
        # Ou recalcule la durée si seule la date de reprise a été saisie.
        elif self.date_depart and self.date_reprise and not self.duree_conge:
            self.duree_conge = (self.date_reprise - self.date_depart).days
        # Pré-remplit la date de retour du dernier congé avec la dernière
        # reprise connue de l'employé, si elle n'est pas renseignée.
        if self.employe_id and not self.date_retour_dernier_conge:
            derniere = self.employe.demandes.exclude(pk=self.pk).order_by('-date_depart').first()
            if derniere and derniere.date_reprise:
                self.date_retour_dernier_conge = derniere.date_reprise
        super().save(*args, **kwargs)
