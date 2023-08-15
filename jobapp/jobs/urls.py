from django.urls import path, re_path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('companies', views.CompanyViewSet, basename='companies')
r.register('cities', views.CityViewSet)
r.register('jobs', views.JobViewSet)
r.register('users', views.UserViewSet)
r.register('user_company', views.UserCompanyViewSet, basename='user-company')
r.register('comments', views.CommentViewSet)
r.register('cvs', views.CvViewSet)
r.register('employees', views.EmployeeCompanyViewset, basename='employee')
r.register('applications', views.ApplicationViewset)

urlpatterns = [
    path('', include(r.urls)),

]
