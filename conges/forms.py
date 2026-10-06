from django import forms

from .models import DemandeConge, Employe


class DateInput(forms.DateInput):
    input_type = 'date'


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            'nom_prenoms', 'matricule', 'fonction', 'direction',
            'date_embauche', 'droit_jours_par_mois', 'actif',
        ]
        widgets = {
            'date_embauche': DateInput(),
        }


class DemandeCongeForm(forms.ModelForm):
    class Meta:
        model = DemandeConge
        fields = [
            'employe', 'date_retour_dernier_conge', 'date_depart',
            'duree_conge', 'date_reprise', 'contact', 'statut', 'avis_chef',
            'commentaire',
        ]
        widgets = {
            'date_retour_dernier_conge': DateInput(),
            'date_depart': DateInput(),
            'date_reprise': DateInput(),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'date_reprise': "Laisse vide : elle sera calculée à partir de la "
                             "date de départ et de la durée.",
        }

    def clean(self):
        cleaned = super().clean()
        duree = cleaned.get('duree_conge')
        reprise = cleaned.get('date_reprise')
        if not duree and not reprise:
            raise forms.ValidationError(
                "Indique soit la durée du congé, soit la date de reprise."
            )
        return cleaned


class SimulateurForm(forms.Form):
    """Simulateur rapide : date de départ + durée → date de retour."""
    date_depart = forms.DateField(label="Date de départ", widget=DateInput())
    duree_conge = forms.IntegerField(
        label="Durée du congé (jours)", min_value=1,
        help_text="Jours calendaires, jour de départ inclus.",
    )
