from django.urls import path, re_path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('company', views.CompanyViewSet)
r.register('city', views.CityViewSet)

urlpatterns = [
    path('', include(r.urls)),

]