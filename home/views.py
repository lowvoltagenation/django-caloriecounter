#home/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
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

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_entries = CalorieEntry.objects.filter(user=user, date__range=[week_start, week_end])
    week_data = week_entries.values('date').annotate(total_calories=Sum(F('quantity') * F('food_item__calories'), output_field=FloatField())).order_by('date')
    week_labels = [entry['date'].strftime('%a') for entry in week_data]
    week_calories = [entry['total_calories'] or 0 for entry in week_data]

    food_items = FoodItem.objects.filter(calorieentry__user=user).annotate(total_calories=Sum(F('calorieentry__quantity') * F('calories'), output_field=FloatField())).order_by('-total_calories')
    food_labels = [item.name for item in food_items]
    food_data = [item.total_calories or 0 for item in food_items]

    try:
        user_target = UserTarget.objects.get(user=user)
        target_calories = user_target.target_calories
    except UserTarget.DoesNotExist:
        target_calories = 2300

    week_total_calories = sum(week_calories)
    week_entries = week_entries.select_related('food_item')
    macronutrient_data = [
        week_entries.aggregate(total_carbohydrates=Sum(F('quantity') * F('food_item__carbohydrates'), output_field=FloatField()))['total_carbohydrates'] or 0,
        week_entries.aggregate(total_protein=Sum(F('quantity') * F('food_item__protein'), output_field=FloatField()))['total_protein'] or 0,
        week_entries.aggregate(total_fat=Sum(F('quantity') * F('food_item__fat'), output_field=FloatField()))['total_fat'] or 0
    ]

    deficit_surplus_data = [calories - target_calories for calories in week_calories]
    weekly_goal = target_calories * 7
    weekly_goal_remaining = max(0, weekly_goal - week_total_calories)

    return {
        'todays_calories': todays_calories,
        'target_calories': target_calories,
        'week_total_calories': week_total_calories,
        'week_labels': week_labels,
        'week_calories': week_calories,
        'food_labels': food_labels,
        'food_data': food_data,
        'week_entries': week_entries,
        'macronutrient_data': macronutrient_data,
        'deficit_surplus_data': deficit_surplus_data,
        'weekly_goal_remaining': weekly_goal_remaining,
    }


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def index(request):
    context = get_user_data(request.user)
    return render(request, 'home/index.html', context)


from django.shortcuts import render

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    context = get_user_data(user)
    return render(request, 'home/index.html', context)
