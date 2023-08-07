import datetime

from .models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from . import cloud_path


class AddCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'company', 'user', 'updated_date']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }


# class EmplyeeSerializer(ModelSerializer):


class UserSerializer(ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff']
        extra_kwargs = {
            'password': {
                'write_only': True
            }, 'avatar_path': {
                'read_only': True
            }, 'avatar': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.is_active = False
        user.save()
        return user


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']


class UserCompany(ModelSerializer):
    role = RoleSerializer()
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        fields = ['avatar_path', 'username', 'first_name', 'last_name', 'phone', 'email', 'role']


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ['name']


class CommentSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        exclude = ['company']


class ImageTourSerializer(ModelSerializer):
    image_path = serializers.SerializerMethodField(source='image')

    def get_image_path(self, obj):
        if obj.image:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.image)
            return path

    class Meta:
        model = ImageCompany
        fields = ['image_path', 'descriptions']
        extra_kwargs = {
            'image_path': {
                'read_only': True
            },
        }


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ['name']


class CvSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Curriculum_Vitae
        exclude = ['active', 'is_deleted']


class EmployeeSerializer(ModelSerializer):
    user = UserCompany()

    def get_company_name(self, obj):
        return obj.company.name

    def get_role_name(self, obj):
        return obj.role.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    company_name = serializers.SerializerMethodField()

    # Thêm trường SerializerMethodField để hiển thị tên vai trò
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        exclude = ['role', 'company']


class CompanySerializer(ModelSerializer):
    user = UserCompany()
    image_path = serializers.SerializerMethodField(source='logo')

    def get_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserCompany(request.user).data
        return None

    def get_image_path(self, obj):
        if obj.logo:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.logo)
            return path

    class Meta:
        model = Company
        fields = ['name', 'email', 'image_path', 'description', 'address', 'city', 'user']


class JobSerializer(ModelSerializer):
    company = CompanySerializer()
    employee = EmployeeSerializer()
    city = CitySerializer()

    def get_majors(self, obj):
        return obj.majors.all().values_list('name', flat=True)

    # Thêm trường majors
    majors = serializers.SerializerMethodField()

    class Meta:
        model = Job
        exclude = ['is_deleted', 'is_checked', 'active']


class ApplicationSerializer(ModelSerializer):
    cv = CvSerializer()
    user = UserSerializer()
    job = JobSerializer()

    class Meta:
        model = Application
        exclude = ['active']


class AddCompanySerializer(ModelSerializer):
    image_path = serializers.SerializerMethodField(source='logo')

    def get_image_path(self, obj):
        if obj.logo:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.logo)
            return path

    class Meta:
        model = Company
        fields = ['name', 'email', 'image_path', 'description', 'address', 'city']
