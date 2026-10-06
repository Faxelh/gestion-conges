from django.contrib import admin

from .models import DemandeConge, Employe


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom_prenoms', 'fonction', 'direction', 'date_embauche', 'droit_jours_par_mois', 'actif')
    list_filter = ('actif', 'direction')
    search_fields = ('nom_prenoms', 'matricule', 'fonction')


@admin.register(DemandeConge)
class DemandeCongeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date_depart', 'duree_conge', 'date_reprise', 'statut')
    list_filter = ('statut', 'avis_chef')
    search_fields = ('employe__nom_prenoms',)
    date_hierarchy = 'date_depart'
