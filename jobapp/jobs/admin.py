from django.contrib import admin
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission, Group

from django.utils.safestring import mark_safe
from django import forms
from . import cloud_path
from .models import *
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.db.models import Count, Sum
from datetime import date
from django.urls import path




from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.

class UserForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = User
        fields = '__all__'


class CompanyForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Company
        fields = '__all__'


class BlogForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Blog
        fields = '__all__'


class MyUserAdmin(UserAdmin):
    model = User
    forms = UserForm
    search_fields = ('username', 'first_name', 'last_name')
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'last_login',
                    'is_active', 'role')
    list_display_links = ('username',)
    list_filter = ('role', 'is_active')
    readonly_fields = ('last_login', 'date_joined', 'avatar')

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     chart_url = reverse('admin:admincharts_piechart', args=['Thống kê người dùng', 'User', object_id, 'my_pie_chart'])
    #     extra_context['chart_url'] = chart_url
    #     return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def view_avatar(self, new):
        if (new.avatar):
            return mark_safe(
                # '<img src="http://127.0.0.1:8000/static/{url}" width="120" />'.format(url=new.image.name)
                "<img src='{cloud_path}{url}' alt='image' width='50' />".format(cloud_path=cloud_path, url=new.avatar)

            )


class BlogAdmin(admin.ModelAdmin):
    model = Blog
    form = BlogForm
    search_fields = ('title', 'active',)
    list_display = ('id', 'title', 'user', 'active')


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    form = CompanyForm
    search_fields = ('name', 'is_checked')
    list_display = ('id', 'view_logo', 'name', 'email', 'is_checked')
    list_display_links = ('name',)
    list_filter = ('is_checked', 'create_date')

    def view_logo(self, new):
        if (new.logo):
            return mark_safe(
                # '<img src="http://127.0.0.1:8000/static/{url}" width="120" />'.format(url=new.image.name)
                "<img src='{cloud_path}{url}' alt='image' width='50' />".format(cloud_path=cloud_path, url=new.logo)

            )


class JobAdmin(admin.ModelAdmin):
    model = Job
    search_fields = ('name',)
    list_display = ('pk', 'name', 'salary_from', 'end_date', 'company', 'is_checked', 'active',
                    )
    list_display_links = ('name',)
    list_filter = ('is_deleted', 'is_checked')


class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ('pk', 'name', 'create_date', 'update_date', 'active')
    search_fields = ('name',)
    list_filter = ('active', 'create_date', 'update_date')


class MajorAdmin(admin.ModelAdmin):
    model = Major
    list_display = ('pk', 'name', 'create_date', 'update_date', 'active')
    search_fields = ('name',)
    list_filter = ('active', 'create_date', 'update_date')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'user_role', 'company_name', 'content', 'rating_with_stars')

    def user_username(self, obj):
        return obj.user.username

    def user_role(self, obj):
        return obj.user.role.name

    def company_name(self, obj):
        return obj.company.name

    def rating_with_stars(self, obj):
        stars = "★" * obj.rating
        return stars


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'company_name', 'role')

    def user_username(self, obj):
        return obj.user.username

    def company_name(self, obj):
        return obj.company.name

    list_filter = ('company__name', 'role')


class MyAdminSite(admin.AdminSite):
    site_header = 'TRAVEL APP MANAGEMENT'
    site_title = 'Travel App Admin'

    def get_urls(self):
        return [
            path('stats/', self.stats_view)
        ] + super().get_urls()

    def stats_view(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            data_application = []
            job_total = Job.objects.count()
            company_total = Company.objects.count()

            # data_book_tour = []
            # tour_total = Job.objects.count()
            # attraction_total = Attraction.objects.count()
            # booking_total = BookTour.objects.filter(created_date__year=date.today().year).count()
            # bill_paid_total = Bill.objects.filter(payment_state=True, created_date__year=date.today().year).count()
            # results_book_tour = BookTour.objects.filter(created_date__year=date.today().year) \
            #     .annotate(month=TruncMonth('created_date')).values('month') \
            #     .annotate(c=Count('pk')).values('month', 'c')
            # bill_momo = Bill.objects.filter(payment_state=True, created_date__year=date.today().year,
            #                                 payment_type=TypeOfPayment.objects.get(pk=2)).count()
            # bill_zalopay = Bill.objects.filter(payment_state=True, created_date__year=date.today().year,
            #                                    payment_type=TypeOfPayment.objects.get(pk=3)).count()
            # bill_cash = bill_paid_total - (bill_zalopay + bill_momo)
            # bill_paid_data = [bill_cash, bill_momo, bill_zalopay]
            # for i in range(12):
            #     flag = False
            #     for rs in results_book_tour:
            #         if i + 1 == rs['month'].month:
            #             data_book_tour.append(rs['c'])
            #             flag = True
            #             break
            #     if not flag:
            #         data_book_tour.append(0)
            return TemplateResponse(request, 'admin/stats.html', {
                # 'tour_total': tour_total,
                # 'attraction_total': attraction_total,
                # 'booking_total': booking_total,
                # 'bill_paid_total': bill_paid_total,
                # 'current_year': date.today().year,
                # 'data_book_tour': data_book_tour,
                # 'bill_paid_data': bill_paid_data,
            })



admin_site = MyAdminSite(name='myadmin')

# admin.site.register(Permission, PermissionAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Curriculum_Vitae)
admin.site.register(Major, MajorAdmin)
admin.site.register(Application)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(ImageCompany)
admin.site.register(Role, RoleAdmin)
admin.site.register(City)
admin.site.register(LikeBlog)
admin.site.register(Wishlist)
admin.site.register(Blog,BlogAdmin)

