#home/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import CalorieEntry, FoodItem, UserTarget

@staff_member_required
def index(request):
    # Calculate today's calories
    today = timezone.now().date()
    todays_entries = CalorieEntry.objects.filter(user=request.user, date=today)
    todays_calories = todays_entries.aggregate(Sum('food_item__calories'))['food_item__calories__sum'] or 0

    # Retrieve the calories data for the current week
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_entries = CalorieEntry.objects.filter(user=request.user, date__range=[week_start, week_end])
    week_data = week_entries.values('date').annotate(total_calories=Sum('food_item__calories')).order_by('date')

    week_labels = [entry['date'].strftime('%a') for entry in week_data]
    week_calories = [entry['total_calories'] or 0 for entry in week_data]

    # Retrieve the food distribution data
    food_items = FoodItem.objects.filter(calorieentry__user=request.user).annotate(total_calories=Sum('calorieentry__food_item__calories')).order_by('-total_calories')

    food_labels = [item.name for item in food_items]
    food_data = [item.total_calories or 0 for item in food_items]

    # Retrieve the user's target calories
    try:
        user_target = UserTarget.objects.get(user=request.user)
        target_calories = user_target.target_calories
    except UserTarget.DoesNotExist:
        target_calories = 2000 


    # Calculate the total calories for the week
    week_total_calories = sum(week_calories)

    week_entries = CalorieEntry.objects.filter(user=request.user, date__range=[week_start, week_end]).select_related('food_item')
    
    macronutrient_data = [
        week_entries.aggregate(Sum('food_item__carbohydrates'))['food_item__carbohydrates__sum'] or 0,
        week_entries.aggregate(Sum('food_item__protein'))['food_item__protein__sum'] or 0,
        week_entries.aggregate(Sum('food_item__fat'))['food_item__fat__sum'] or 0
    ]

    # Calculate daily calorie deficit/surplus
    deficit_surplus_data = [
        calories - target_calories
        for calories in week_calories
    ]

    # Calculate remaining calories to reach weekly goal
    weekly_goal = target_calories * 7
    weekly_goal_remaining = max(0, weekly_goal - week_total_calories)
   
    context = {
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
    return render(request, 'home/index.html', context)