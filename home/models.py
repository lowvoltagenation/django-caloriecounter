#home/models.py
from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField(default=0)
    carbohydrates = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    fat = models.FloatField(default=0)

    def __str__(self):
        return self.name

class CalorieEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField()

class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField()

class UserTarget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_calories = models.IntegerField(default=2000)

    def __str__(self):
        return f"{self.user.username}'s Target"