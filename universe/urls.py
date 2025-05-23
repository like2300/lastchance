from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('info/', views.info, name='info'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('equipe/', views.equipe, name='equipe'),
    path('contact/', views.contact, name='contact'),
    path('get-formations/', views.get_formations, name='get_formations'),
]