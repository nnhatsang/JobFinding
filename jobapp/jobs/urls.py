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
r.register('blogs', views.BlogViewSet)

urlpatterns = [
    path('', include(r.urls)),

    # path('admin/', admin_site.urls),

    # path('send_mail/', views.SendMailAPIView.as_view(), name='send_mail'),
    # path('oauth2_info/', views.AuthInfo.as_view(), name='oauth2-info'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    #
    # path('social_auth/google/', views.GoogleSocialAuthView.as_view(), name="google_auth"),
    # path('social_auth/facebook/', views.FacebookSocialAuthView.as_view(), name="facebook_auth"),

]
