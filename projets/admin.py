from django.contrib import admin
from .models import Projet
# # Register your models here.

class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre','description')
#à revoir apres probleme d'affichage

admin.site.register(Projet, ProjetAdmin)