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
                    'view_avatar', 'role')
    list_display_links = ('username',)
    list_filter = ('role', 'is_active')
    readonly_fields = ('last_login', 'date_joined', 'avatar')

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
    list_display = ('pk', 'name', 'salary_from', 'salary_to', 'position', 'quantity', 'city',
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


admin.site.register(Permission, PermissionAdmin)
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
