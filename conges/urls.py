from django.urls import path

from . import views

app_name = 'conges'

urlpatterns = [
    path('', views.SimulateurView.as_view(), name='simulateur'),

    path('employes/', views.EmployeListView.as_view(), name='employe-list'),
    path('employes/nouveau/', views.EmployeCreateView.as_view(), name='employe-create'),
    path('employes/<int:pk>/', views.EmployeDetailView.as_view(), name='employe-detail'),
    path('employes/<int:pk>/modifier/', views.EmployeUpdateView.as_view(), name='employe-update'),
    path('employes/<int:pk>/supprimer/', views.EmployeDeleteView.as_view(), name='employe-delete'),

    path('demandes/', views.DemandeListView.as_view(), name='demande-list'),
    path('demandes/nouvelle/', views.DemandeCreateView.as_view(), name='demande-create'),
    path('demandes/<int:pk>/', views.DemandeDetailView.as_view(), name='demande-detail'),
    path('demandes/<int:pk>/modifier/', views.DemandeUpdateView.as_view(), name='demande-update'),
    path('demandes/<int:pk>/supprimer/', views.DemandeDeleteView.as_view(), name='demande-delete'),
    path('demandes/<int:pk>/statut/<str:statut>/', views.changer_statut, name='demande-statut'),
]
