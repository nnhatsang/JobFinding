from django.urls import path, re_path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('companies', views.CompanyViewSet)
r.register('cities', views.CityViewSet)
r.register('jobs', views.JobViewSet)
r.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(r.urls)),

]
