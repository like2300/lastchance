from django import forms
from .models import Formation, Inscription
from django_countries.widgets import CountrySelectWidget
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
        }

class InscriptionsForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés.")
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '+237 6XX XXX XXX'
        })
    )

    class Meta:
        model = Inscription
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone', 'country', 'city', 'address', 'formations']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre nom'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'votre@email.com'
            }),
            'country': CountrySelectWidget(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'style': 'padding-left: 2.5rem; height: 2.5rem;'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre ville'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre adresse complète',
                'rows': 3
            }),
            'formations': forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        }
        error_messages = {
            'first_name': {
                'required': _('Le prénom est obligatoire.'),
                'max_length': _('Le prénom ne peut pas dépasser 100 caractères.')
            },
            'last_name': {
                'required': _('Le nom est obligatoire.'),
                'max_length': _('Le nom ne peut pas dépasser 100 caractères.')
            },
            'date_of_birth': {
                'required': _('La date de naissance est obligatoire.'),
                'invalid': _('Veuillez entrer une date valide.')
            },
            'email': {
                'required': _('L\'adresse email est obligatoire.'),
                'invalid': _('Veuillez entrer une adresse email valide.')
            },
            'phone': {
                'required': _('Le numéro de téléphone est obligatoire.')
            },
            'country': {
                'required': _('Le pays est obligatoire.')
            },
            'city': {
                'required': _('La ville est obligatoire.'),
                'max_length': _('Le nom de la ville ne peut pas dépasser 100 caractères.')
            },
            'address': {
                'required': _('L\'adresse est obligatoire.')
            },
            'formations': {
                'required': _('Veuillez sélectionner au moins une formation.')
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['formations'].queryset = Formation.objects.all()
        self.fields['formations'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['address'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Inscription.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Cette adresse email est déjà utilisée.'))
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Inscription.objects.filter(phone=phone).exists():
            raise forms.ValidationError(_('Ce numéro de téléphone est déjà utilisé.'))
        return phone

    def clean_formations(self):
        formations = self.cleaned_data.get('formations')
        if not formations:
            raise forms.ValidationError(_('Veuillez sélectionner au moins une formation.'))
        return formations