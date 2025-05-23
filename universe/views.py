from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django_countries import countries
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
from .models import Formation, Inscription, MembreEquipe, InfosPlateforme, Pricing, Partenaire, Avis
from django.forms import modelform_factory
from .models import Inscription, Formation
from .forms import FormationForm, InscriptionsForm
from django_countries.fields import CountryField
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext as _




def inscription_view(request):
    form = InscriptionsForm(request.POST or None)
    
    if request.method == 'POST':
        type_selected = request.POST.get("type_formation")
        if type_selected:
            form.fields["formations"].queryset = Formation.objects.filter(type=type_selected)
        
        if form.is_valid():
            try:
                inscription = form.save()
                messages.success(request, _("Votre inscription a été enregistrée avec succès! Nous vous contacterons bientôt."))
                return redirect('confirmation')
            except Exception as e:
                messages.error(request, _("Une erreur est survenue lors de l'enregistrement. Veuillez réessayer."))
        else:
            if 'email' in form.errors:
                messages.error(request, _("Cette adresse email est déjà utilisée."))
            if 'phone' in form.errors:
                messages.error(request, _("Ce numéro de téléphone est déjà utilisé."))
            if 'formations' in form.errors:
                messages.warning(request, _("Veuillez sélectionner au moins une formation."))
    
    # Récupération des formations par type
    formations_pro = Formation.objects.filter(type='professionnel')
    formations_langues = Formation.objects.filter(type='langues')
    
    return render(request, 'vitrine/inscription.html', {
        'form': form,
        'formations_pro': formations_pro,
        'formations_langues': formations_langues,
    })

def info(request):
    infos = InfosPlateforme.objects.all()
    return render(request, 'vitrine/info.html', {'infos': infos})

def confirmation(request):
    return render(request, 'vitrine/confirmation.html')

def get_formations(request):
    type_formation = request.GET.get('type')
    formations = Formation.objects.filter(type=type_formation).values('id', 'name')
    return JsonResponse(list(formations), safe=False)

def home(request):
    formations_pro = Formation.objects.filter(type='professionnel')
    formations_langues = Formation.objects.filter(type='langues')
    infos = InfosPlateforme.objects.all()
    pricing = Pricing.objects.all()
    partenaires = Partenaire.objects.all()
    avis = Avis.objects.all().order_by('-date')[:6]
    equipe = MembreEquipe.objects.all()

    context = {
        'formations_pro': formations_pro,
        'formations_langues': formations_langues,
        'infos': infos,
        'pricing': pricing,
        'partenaires': partenaires,
        'avis': avis,
        'equipe': equipe,
    }
    return render(request, 'vitrine/accueil.html', context)

def equipe(request):
    """
    Vue pour afficher tous les membres de l'équipe.
    """
    equipe = MembreEquipe.objects.all()
    return render(request, 'vitrine/equipe.html', {'equipe': equipe})

def about(request):
    equipe = MembreEquipe.objects.all()
    partenaires = Partenaire.objects.all()
    return render(request, 'vitrine/about.html', {'equipe': equipe, 'partenaires': partenaires})

def contact(request):
    return render(request, 'vitrine/nousRejoindre.html')

def check_formation_availability(request, formation_id):
    formation = get_object_or_404(Formation, id=formation_id)
    return JsonResponse({
        'available': formation.est_disponible(),
        'places_restantes': formation.places_disponibles
    })

class FormationListView(ListView):
    model = Formation
    template_name = 'vitrine/formations.html'
    context_object_name = 'formations'
    paginate_by = 9

    def get_queryset(self):
        queryset = Formation.objects.filter(est_active=True)
        search_query = self.request.GET.get('search', '')
        type_filter = self.request.GET.get('type', '')
        niveau_filter = self.request.GET.get('niveau', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if type_filter:
            queryset = queryset.filter(type=type_filter)

        if niveau_filter:
            queryset = queryset.filter(niveau=niveau_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = Formation.TYPE_CHOICES
        context['niveaux'] = Formation.NIVEAU_CHOICES
        return context

class FormationDetailView(DetailView):
    model = Formation
    template_name = 'vitrine/formation_detail.html'
    context_object_name = 'formation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formation = self.get_object()
        context['prix_par_heure'] = formation.prix_par_heure
        context['est_disponible'] = formation.est_disponible()
        return context

class InscriptionCreateView(CreateView):
    model = Inscription
    form_class = InscriptionsForm
    template_name = 'vitrine/inscription.html'
    success_url = reverse_lazy('inscription_success')

    def form_valid(self, form):
        try:
            # Vérifier la disponibilité des formations
            formations = form.cleaned_data.get('formations')
            for formation in formations:
                if not formation.est_disponible():
                    messages.error(self.request, f"Plus de places disponibles pour la formation {formation.name}")
                    return self.form_invalid(form)

            # Sauvegarder l'inscription
            inscription = form.save()
            
            # Réduire le nombre de places disponibles
            for formation in formations:
                formation.reduire_places()

            messages.success(self.request, "Votre inscription a été enregistrée avec succès!")
            return super().form_valid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formations'] = Formation.objects.filter(est_active=True)
        return context

class InscriptionSuccessView(ListView):
    model = Inscription
    template_name = 'vitrine/inscription_success.html'
    context_object_name = 'inscriptions'

    def get_queryset(self):
        return Inscription.objects.filter(statut='en_attente').order_by('-created_at')

class FormationCreateView(LoginRequiredMixin, CreateView):
    model = Formation
    form_class = FormationForm
    template_name = 'vitrine/formation_form.html'
    success_url = reverse_lazy('formation_list')

    def form_valid(self, form):
        messages.success(self.request, "La formation a été créée avec succès!")
        return super().form_valid(form)

class FormationUpdateView(LoginRequiredMixin, UpdateView):
    model = Formation
    form_class = FormationForm
    template_name = 'vitrine/formation_form.html'
    success_url = reverse_lazy('formation_list')

    def form_valid(self, form):
        messages.success(self.request, "La formation a été mise à jour avec succès!")
        return super().form_valid(form)

class FormationDeleteView(LoginRequiredMixin, DeleteView):
    model = Formation
    success_url = reverse_lazy('formation_list')
    template_name = 'vitrine/formation_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La formation a été supprimée avec succès!")
        return super().delete(request, *args, **kwargs)

def inscription_success(request):
    return render(request, 'vitrine/inscription_success.html')


