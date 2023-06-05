from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Compte
from datetime import timedelta

@csrf_exempt
def compte_view(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire HTMX
        achat_carte_credit = bool(request.POST.get('achat_carte_credit'))
        montant = float(request.POST.get('montant'))
        
        # Enregistrer les données dans la base de données
        Compte.objects.create(
            achat_carte_credit=achat_carte_credit,
            montant=montant
        )

        return JsonResponse({'success': True})

    else:
        # Obtenir les données des comptes pour les afficher dans le tableau
        comptes = Compte.objects.all()
        return render(request, 'auto/compte.html', {'comptes': comptes})

@csrf_exempt
def minuteur_view(request):
    # Déterminer le temps restant jusqu'à la prochaine sauvegarde
    compte = Compte.objects.order_by('-heure_envoi').first()
    if compte:
        heure_derniere_envoi = compte.heure_envoi
        heure_prochaine_envoi = heure_derniere_envoi + timedelta(minutes=10)
        temps_restant = heure_prochaine_envoi - heure_derniere_envoi
    else:
        # Si aucune sauvegarde n'a été effectuée, initialiser le minuteur à 10 minutes
        temps_restant = timedelta(minutes=10)

    return render(request, 'auto/minuteur.html', {'temps_restant': temps_restant})
