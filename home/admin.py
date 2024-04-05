#home/admin.py
from django.contrib import admin
from .models import FoodItem, CalorieEntry, WeightEntry, UserTarget
from django import forms
from django.utils import timezone

class CalorieEntryForm(forms.ModelForm):
    class Meta:
        model = CalorieEntry
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localtime(timezone.now()).date().strftime('%Y-%m-%d')}),
        }

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories')

@admin.register(CalorieEntry)
class CalorieEntryAdmin(admin.ModelAdmin):
    form = CalorieEntryForm
    list_display = ('user', 'food_item', 'date', 'quantity',)
    list_filter = ('user', 'date', 'food_item')
    search_fields = ('user__username', 'food_item__name')
    list_editable = ('food_item', 'quantity', 'date')


    def get_changeform_initial_data(self, request):
        return {'user': request.user}

@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'date')

@admin.register(UserTarget)
class UserTargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_calories')
    search_fields = ('user__username',)