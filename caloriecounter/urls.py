from django.urls import path
from home.views import index, public_profile  # Ensure you import the view from the correct app
from django.contrib import admin
from home import views

urlpatterns = [
    path('', views.index, name='index'),

    path('', index, name='home'),
    path('admin/', admin.site.urls),  # This line correctly includes Django admin URLs with the default 'admin' namespace
    path('user/<str:username>/', public_profile, name='public-profile'),
    # other patterns
]
