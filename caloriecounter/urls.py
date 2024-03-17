
#home/views.py
from django.contrib import admin
from django.urls import path
from home.views import index


urlpatterns = [
    path('', index, name='home'),

    path('admin/', admin.site.urls),

]
