from uuid6 import uuid7
from django.db import models

# Create your models here.

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.CharField(max_length=150, unique=True)
    gender = models.CharField(max_length=20)
    gender_probability = models.FloatField(max_length=10)
    sample_size = models.IntegerField()
    age = models.IntegerField()
    age_group = models.CharField(max_length=20)
    country_id = models.CharField(max_length=10)
    country_probability = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name