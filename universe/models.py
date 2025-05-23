from django.db import models
from django_countries.fields import CountryField


class Formation(models.Model):
    TYPE_CHOICES = [
        ('professionnel', 'Professionnel'),
        ('langues', 'Langues Vivantes'),
    ]
    name = models.CharField(max_length=100, verbose_name="Nom de la formation")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de formation")

    def __str__(self):
        return self.name

class Inscription(models.Model):  # <-- LA CLASSE INSCRIPTION EST ICI
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    email = models.EmailField(verbose_name="Adresse e-mail", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    country = CountryField(verbose_name="Pays")
    city = models.CharField(max_length=100, verbose_name="Ville")
    address = models.TextField(verbose_name="Adresse")
    formations = models.ManyToManyField(Formation, verbose_name="Formations choisies")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    def __str__(self):
        formations_list = ", ".join([formation.name for formation in self.formations.all()])
        return f"{self.first_name} {self.last_name} - {formations_list}"
    

class MembreEquipe(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='equipe/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.role}"


# Modèle pour les avis des utilisateurs
class Avis(models.Model):
    utilisateur = models.CharField(max_length=100)
    commentaire = models.TextField()
    note = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avis de {self.utilisateur} - {self.note}/5"

class InfosPlateforme(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


# Modèle pour la tarification (Pricing)
class Pricing(models.Model):
    nom = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    avantages = models.TextField()  # Liste des avantages sous forme de texte

    def __str__(self):
        return f"{self.nom} - {self.prix}CFA"


# Modèle pour les partenaires
class Partenaire(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partenaires/', blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nom