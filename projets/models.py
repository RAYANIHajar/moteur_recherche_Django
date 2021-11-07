from django.db import models

# Create your models here.
class Projet(models.Model):
    titre=models.CharField(max_length=50)
    description=models.TextField()
    image_url=models.CharField(max_length=2000)