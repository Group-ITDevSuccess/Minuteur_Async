from django.db import models

# Create your models here.
class index(models.Model):
    achat_carte_credit = models.BooleanField(default=False)
    montant = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    heure_envoi = models.DateTimeField(auto_now_add=True)