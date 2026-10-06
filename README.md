# Gestion des congés

Petite application Django pour calculer et suivre tes congés annuels :
simulateur rapide (date de départ + durée → date de retour), fiches
employés avec solde de congés calculé automatiquement, et demandes de
congé imprimables.

## Fonctionnalités

- **Simulateur** (page d'accueil) : tu entres ta date de départ et le
  nombre de jours souhaités, l'appli calcule immédiatement ta date de
  reprise.
- **Fiches employés** : nom, fonction, direction, date d'embauche, et un
  taux d'acquisition personnalisable (2,2 jours/mois par défaut, le
  minimum légal usuel en Côte d'Ivoire = 26,4 jours/an).
- **Calcul automatique du solde** pour chaque employé :
  `droits acquis (mois de service × taux) − jours déjà pris (demandes validées)`.
- **Demandes de congé** reprenant les champs du formulaire papier
  (date de retour du dernier congé, date de départ, durée, date de
  reprise, contacts, avis du chef hiérarchique, statut) avec calcul
  automatique de la date de reprise, et une vue imprimable.
- **Statuts** : en attente / validée / refusée, modifiables en un clic.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optionnel, pour l'admin Django
python manage.py runserver
```

Ouvre ensuite http://127.0.0.1:8000/ dans ton navigateur.

L'interface d'administration Django (gestion brute des données) est
disponible sur http://127.0.0.1:8000/admin/ une fois un compte superuser créé.

## Structure du projet

```
gestion_conges/
├── manage.py
├── requirements.txt
├── conges_project/        # réglages Django (settings, urls)
└── conges/                 # application principale
    ├── models.py           # Employe, DemandeConge + calculs
    ├── views.py            # simulateur, CRUD employés/demandes
    ├── forms.py
    ├── admin.py
    └── templates/conges/
```

## Ajuster la règle de calcul

- Par défaut, chaque employé acquiert **2,2 jours/mois** de service
  effectif. Ce taux est modifiable individuellement sur la fiche de
  chaque employé (champ « Droit à congé »), par exemple si ta
  convention collective ou ton contrat prévoit un taux plus favorable.
- La durée du congé saisie dans une demande est en **jours calendaires**
  (le jour de départ compte comme jour 1). Si tu préfères raisonner en
  jours ouvrables (hors dimanches/jours fériés), tu peux ajuster la
  méthode `save()` du modèle `DemandeConge` dans `conges/models.py`.
- Seules les demandes au statut **« Validée »** sont déduites du solde ;
  les demandes « en attente » apparaissent séparément à titre indicatif.

## Remarques

- En local, base de données SQLite par défaut (fichier `db.sqlite3`),
  aucune configuration supplémentaire nécessaire.
- Aucune authentification n'est requise par défaut pour les pages de
  l'application (seul `/admin/` est protégé). Si plusieurs personnes y
  ont accès, pense à ajouter une authentification (`LoginRequiredMixin`
  sur les vues dans `conges/views.py`).

## Déploiement en ligne (Render + sous-domaine Hostinger)

Hostinger ne supporte Python/Django que sur ses VPS (pas sur
l'hébergement mutuel/cloud classique). On déploie donc l'app sur
**Render** (hébergeur gratuit pour petites apps Django), puis on
pointe le sous-domaine `elara.kounandi.org` vers Render depuis le DNS
de Hostinger — sans toucher au reste de `kounandi.org`.

### 1. Créer le dépôt Git

Le code doit être sur GitHub (ou GitLab) pour que Render puisse s'y
connecter.

### 2. Créer le service sur Render

1. Crée un compte sur [render.com](https://render.com) (gratuit).
2. **New → Blueprint**, connecte le dépôt GitHub : Render lit le fichier
   `render.yaml` à la racine et crée automatiquement le service web
   **et** la base Postgres gratuite, avec les variables d'environnement
   déjà pré-remplies.
   - Si tu préfères tout configurer à la main (**New → Web Service**) :
     - Build command : `./build.sh`
     - Start command : `gunicorn conges_project.wsgi:application`
     - Ajoute une base **PostgreSQL** (New → PostgreSQL, plan Free) et
       relie sa variable `DATABASE_URL` au service web.
     - Variables d'environnement à définir : `SECRET_KEY` (valeur
       aléatoire longue), `DEBUG=False`, `ALLOWED_HOSTS=elara.kounandi.org`,
       `CSRF_TRUSTED_ORIGINS=https://elara.kounandi.org`.
3. Attends la fin du premier déploiement (build + migrations
   automatiques via `build.sh`).
4. Crée un compte admin une fois en ligne : dans l'onglet **Shell** du
   service Render, lance `python manage.py createsuperuser`.

### 3. Brancher le sous-domaine elara.kounandi.org

1. Dans Render : **Settings → Custom Domains** du service web → ajoute
   `elara.kounandi.org`. Render affiche une valeur CNAME cible (type
   `xxxx.onrender.com`).
2. Dans **hPanel Hostinger** : Domaines → `kounandi.org` → **DNS / Zone
   Editor**, ajoute un enregistrement :
   - Type : `CNAME`
   - Nom/Host : `elara`
   - Cible/Valeur : la valeur donnée par Render (ex. `gestion-conges.onrender.com`)
   - TTL : par défaut
3. Attends la propagation DNS (de quelques minutes à quelques heures).
   Render détecte automatiquement le domaine et génère un certificat
   SSL gratuit une fois le CNAME actif.

### Limites du plan gratuit Render à connaître

- Le service se met en veille après ~15 minutes sans trafic : la
  première requête après une pause met 30 à 60 secondes à répondre
  (normal, pas un bug).
- La base Postgres gratuite expire au bout de 90 jours ; il faudra la
  recréer (ou passer sur un plan payant, ~7 $/mois) pour garder les
  données au-delà si tu veux une conservation à long terme sans y
  repenser.
