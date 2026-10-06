from datetime import timedelta

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView,
)

from .forms import DemandeCongeForm, EmployeForm, SimulateurForm
from .models import DemandeConge, Employe


class SimulateurView(TemplateView):
    """Page d'accueil : simulateur rapide départ + durée -> date de retour."""
    template_name = 'conges/simulateur.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SimulateurForm(self.request.GET or None)
        context['form'] = form
        if form.is_valid():
            depart = form.cleaned_data['date_depart']
            duree = form.cleaned_data['duree_conge']
            date_retour = depart + timedelta(days=duree)
            context['date_retour'] = date_retour
            context['depart'] = depart
            context['duree'] = duree
            jour_fr = {
                0: 'lundi', 1: 'mardi', 2: 'mercredi', 3: 'jeudi',
                4: 'vendredi', 5: 'samedi', 6: 'dimanche',
            }
            context['jour_retour'] = jour_fr[date_retour.weekday()]
        context['employes'] = Employe.objects.filter(actif=True)
        return context


class EmployeListView(ListView):
    model = Employe
    template_name = 'conges/employe_list.html'
    context_object_name = 'employes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lignes = []
        for employe in context['employes']:
            lignes.append({
                'employe': employe,
                'mois_service': employe.mois_service(),
                'droits_acquis': employe.droits_acquis(),
                'jours_pris': employe.jours_pris(),
                'solde': employe.solde(),
            })
        context['lignes'] = lignes
        return context


class EmployeDetailView(DetailView):
    model = Employe
    template_name = 'conges/employe_detail.html'
    context_object_name = 'employe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employe = self.object
        context['mois_service'] = employe.mois_service()
        context['droits_acquis'] = employe.droits_acquis()
        context['jours_pris'] = employe.jours_pris()
        context['jours_planifies'] = employe.jours_planifies_non_valides()
        context['solde'] = employe.solde()
        context['demandes'] = employe.demandes.all()
        return context


class EmployeCreateView(CreateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'conges/employe_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Employé créé avec succès.")
        return super().form_valid(form)


class EmployeUpdateView(UpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'conges/employe_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Fiche employé mise à jour.")
        return super().form_valid(form)


class EmployeDeleteView(DeleteView):
    model = Employe
    template_name = 'conges/confirm_delete.html'
    success_url = reverse_lazy('conges:employe-list')

    def form_valid(self, form):
        messages.success(self.request, "Employé supprimé.")
        return super().form_valid(form)


class DemandeListView(ListView):
    model = DemandeConge
    template_name = 'conges/demande_list.html'
    context_object_name = 'demandes'

    def get_queryset(self):
        qs = DemandeConge.objects.select_related('employe').all()
        employe_id = self.request.GET.get('employe')
        if employe_id:
            qs = qs.filter(employe_id=employe_id)
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employes'] = Employe.objects.all()
        context['statut_choices'] = DemandeConge.STATUT_CHOICES
        context['employe_filtre'] = self.request.GET.get('employe', '')
        context['statut_filtre'] = self.request.GET.get('statut', '')
        return context


class DemandeDetailView(DetailView):
    model = DemandeConge
    template_name = 'conges/demande_detail.html'
    context_object_name = 'demande'


class DemandeCreateView(CreateView):
    model = DemandeConge
    form_class = DemandeCongeForm
    template_name = 'conges/demande_form.html'

    def get_initial(self):
        initial = super().get_initial()
        employe_id = self.request.GET.get('employe')
        if employe_id:
            initial['employe'] = employe_id
            employe = get_object_or_404(Employe, pk=employe_id)
            derniere = employe.derniere_demande()
            if derniere and derniere.date_reprise:
                initial['date_retour_dernier_conge'] = derniere.date_reprise
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Demande de congé enregistrée.")
        return super().form_valid(form)


class DemandeUpdateView(UpdateView):
    model = DemandeConge
    form_class = DemandeCongeForm
    template_name = 'conges/demande_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Demande de congé mise à jour.")
        return super().form_valid(form)


class DemandeDeleteView(DeleteView):
    model = DemandeConge
    template_name = 'conges/confirm_delete.html'
    success_url = reverse_lazy('conges:demande-list')

    def form_valid(self, form):
        messages.success(self.request, "Demande supprimée.")
        return super().form_valid(form)


def changer_statut(request, pk, statut):
    demande = get_object_or_404(DemandeConge, pk=pk)
    valeurs_valides = dict(DemandeConge.STATUT_CHOICES)
    if statut in valeurs_valides:
        demande.statut = statut
        demande.save(update_fields=['statut'])
        messages.success(request, f"Statut mis à jour : {valeurs_valides[statut]}.")
    return redirect('conges:demande-detail', pk=pk)
