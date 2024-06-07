#home/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Sum, F, FloatField
from django.utils import timezone
from datetime import timedelta
from .models import CalorieEntry, FoodItem, UserTarget
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

def get_user_data(user):
    today = timezone.localtime(timezone.now()).date()
    todays_entries = CalorieEntry.objects.filter(user=user, date=today)
    todays_calories = todays_entries.aggregate(total_calories=Sum(F('quantity') * F('food_item__calories'), output_field=FloatField()))['total_calories'] or 0

    past_7_days_start = today - timedelta(days=6)
    past_7_days_entries = CalorieEntry.objects.filter(user=user, date__range=[past_7_days_start, today])
    past_7_days_data = past_7_days_entries.values('date').annotate(
        total_calories=Sum(F('quantity') * F('food_item__calories'), output_field=FloatField()),
        total_carbohydrates=Sum(F('quantity') * F('food_item__carbohydrates'), output_field=FloatField()),
        total_protein=Sum(F('quantity') * F('food_item__protein'), output_field=FloatField()),
        total_fat=Sum(F('quantity') * F('food_item__fat'), output_field=FloatField())
    ).order_by('date')    
    past_7_days_labels = [entry['date'].strftime('%a') for entry in past_7_days_data]
    past_7_days_calories = [entry['total_calories'] or 0 for entry in past_7_days_data]
    past_7_days_macros = [
    {
        'carbohydrates': entry['total_carbohydrates'] or 0,
        'protein': entry['total_protein'] or 0,
        'fat': entry['total_fat'] or 0
    }
    for entry in past_7_days_data
]
    food_items = FoodItem.objects.filter(calorieentry__user=user).annotate(total_calories=Sum(F('calorieentry__quantity') * F('calories'), output_field=FloatField())).order_by('-total_calories')
    food_labels = [item.name for item in food_items]
    food_data = [item.total_calories or 0 for item in food_items]

    try:
        user_target = UserTarget.objects.get(user=user)
        target_calories = user_target.target_calories
    except UserTarget.DoesNotExist:
        target_calories = 2300

    past_7_days_total_calories = sum(past_7_days_calories)
    past_7_days_entries = past_7_days_entries.select_related('food_item')
    macronutrient_data = [
        past_7_days_entries.aggregate(total_carbohydrates=Sum(F('quantity') * F('food_item__carbohydrates'), output_field=FloatField()))['total_carbohydrates'] or 0,
        past_7_days_entries.aggregate(total_protein=Sum(F('quantity') * F('food_item__protein'), output_field=FloatField()))['total_protein'] or 0,
        past_7_days_entries.aggregate(total_fat=Sum(F('quantity') * F('food_item__fat'), output_field=FloatField()))['total_fat'] or 0
    ]

    deficit_surplus_data = [calories - target_calories for calories in past_7_days_calories] 
    past_7_days_goal = target_calories * 7
    past_7_days_goal_remaining = max(0, past_7_days_goal - past_7_days_total_calories)

    # Calculate average calories per day for the week
    past_7_days_entries = CalorieEntry.objects.filter(user=user, date__gte=today - timedelta(days=6))
    past_7_days_total_calories = sum(entry.quantity * entry.food_item.calories for entry in past_7_days_entries)
    avg_calories_per_day = round(past_7_days_total_calories / 7)


    return {
        'todays_calories': todays_calories,
        'target_calories': target_calories,
        'past_7_days_total_calories': past_7_days_total_calories,
        'past_7_days_labels': past_7_days_labels,
        'past_7_days_calories': past_7_days_calories,
        'food_labels': food_labels,
        'food_data': food_data,
        'past_7_days_entries': past_7_days_entries,
        'macronutrient_data': macronutrient_data,
        'deficit_surplus_data': deficit_surplus_data,
        'past_7_days_goal_remaining': past_7_days_goal_remaining,
        'today': today,
        'avg_calories_per_day': avg_calories_per_day,
        'past_7_days_macros': past_7_days_macros,

    }


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def index(request):
    if request.method == 'POST':
        food_item_id = request.POST.get('food_item')
        quantity = request.POST.get('quantity')
        date = request.POST.get('date')

        food_item = get_object_or_404(FoodItem, id=food_item_id)
        user = request.user

        calorie_entry = CalorieEntry(user=user, food_item=food_item, quantity=quantity, date=date)
        calorie_entry.save()

        return redirect('index')

    food_items = FoodItem.objects.all()
    today = timezone.now().date()

    context = get_user_data(request.user)
    context['food_items'] = food_items
    context['today'] = today

    return render(request, 'home/index.html', context)


from django.shortcuts import render

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    context = get_user_data(user)
    return render(request, 'home/index.html', context)
