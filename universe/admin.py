from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Formation, Inscription, MembreEquipe, InfosPlateforme, Avis, Pricing, Partenaire

# Personnalisation du titre et de l'en-tête de l'interface d'administration
admin.site.site_title = _("Universe Academy")
admin.site.site_header = _("Universe Academy")
admin.site.index_title = _("Tableau de bord Universe Academy")

# Classe d'administration pour le modèle Formation
class FormationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')  # Colonnes affichées dans la liste
    list_filter = ('type',)  # Filtre par type de formation
    search_fields = ('name',)  # Recherche par nom de formation

admin.site.register(Formation, FormationAdmin)

# Classe d'administration pour le modèle MembreEquipe
class MembreEquipeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'role', 'photo')  # Colonnes affichées dans la liste
    list_filter = ('role',)  # Filtre par rôle
    search_fields = ('role', 'nom', 'prenom')  # Recherche par rôle, nom ou prénom

admin.site.register(MembreEquipe, MembreEquipeAdmin)

# Classe d'administration pour le modèle InfosPlateforme
class InfosPlateformeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'description', 'date_mise_a_jour')  # Colonnes affichées dans la liste
    search_fields = ('titre',)  # Recherche par titre

admin.site.register(InfosPlateforme, InfosPlateformeAdmin)

# Classe d'administration pour le modèle Avis
class AvisAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'note', 'date')  # Colonnes affichées dans la liste
    list_filter = ('note',)  # Filtre par note
    search_fields = ('utilisateur',)  # Recherche par utilisateur

admin.site.register(Avis, AvisAdmin)

# Classe d'administration pour le modèle Pricing (Tarification)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'description')  # Colonnes affichées dans la liste
    search_fields = ('nom',)  # Recherche par nom

admin.site.register(Pricing, PricingAdmin)

# Classe d'administration pour le modèle Partenaire
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'site_web', 'logo')  # Colonnes affichées dans la liste
    search_fields = ('nom', 'site_web')  # Recherche par nom ou site web

admin.site.register(Partenaire, PartenaireAdmin)

# Classe d'administration pour le modèle Inscription
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'get_formations', 'country', 'city', 'contact_buttons')
    list_filter = ('formations__type', 'country', 'city')  # Filtre par type de formation, pays et ville
    search_fields = ('first_name', 'last_name', 'email')  # Recherche par prénom, nom ou email

    def get_formations(self, obj):
        """Affiche les formations sélectionnées dans l'admin."""
        return ", ".join([formation.name for formation in obj.formations.all()])
    get_formations.short_description = "Formations"

    def contact_buttons(self, obj):
        """Ajoute des boutons pour contacter les inscrits."""
        whatsapp_url = f"https://wa.me/{obj.phone}"
        mailto_url = f"mailto:{obj.email}"
        call_url = f"tel:{obj.phone}"

        return format_html(
            '<a href="{}" target="_blank" style="margin-right:5px; text-decoration:none;">📩 Email</a>'
            '<a href="{}" target="_blank" style="margin-right:5px; text-decoration:none;">📞 Appel</a>'
            '<a href="{}" target="_blank" style="color:green; text-decoration:none;">💬 WhatsApp</a>',
            mailto_url, call_url, whatsapp_url
        )
    contact_buttons.allow_tags = True
    contact_buttons.short_description = "Actions"

    # Action personnalisée pour exporter les inscriptions en CSV
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inscriptions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Prénom', 'Nom', 'Email', 'Formations', 'Pays', 'Ville'])

        for inscription in queryset:
            formations = ", ".join([formation.name for formation in inscription.formations.all()])
            writer.writerow([
                inscription.first_name,
                inscription.last_name,
                inscription.email,
                formations,
                inscription.country.name,  # Utilisez `inscription.country.name` pour le nom complet du pays
                inscription.city
            ])
        return response

    export_as_csv.short_description = "Exporter les inscriptions sélectionnées en CSV"
    actions = [export_as_csv]  # Ajout de l'action personnalisée

admin.site.register(Inscription, InscriptionAdmin)
