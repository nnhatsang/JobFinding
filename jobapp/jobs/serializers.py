import datetime

from .models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from . import cloud_path, google, facebook
from rest_framework.exceptions import AuthenticationFailed
from .register import register_social_user
from django.conf import settings


class AddCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'company', 'user', 'rating']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserSerializer(ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    # role = RoleSerializer()

    def get_role_name(self, obj):
        return obj.role.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    role_name = serializers.SerializerMethodField()

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_active', 'is_superuser']

        extra_kwargs = {
            'password': {
                'write_only': True
            }, 'avatar_path': {
                'read_only': True
            }, 'avatar': {
                'write_only': True
            },
            # 'role': {
            #     'write_only': True
            # }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.is_active = False
        user.save()

        return user


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


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ['name']


class ImageCompanySerializer(ModelSerializer):
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
        fields = ['id', 'name']


class UserCvSerializer(ModelSerializer):
    class Meta(UserSerializer.Meta):
        exclude = ['last_login', 'date_joined', 'role', 'is_superuser', 'is_staff', 'is_active', 'user_permissions',
                   'groups']
        # fields = [
        #     'username', 'first_name', 'last_name', 'email', 'dob', 'description', 'gender', 'phone', 'address',
        #     'avatar_path',
        # ]


class CvSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Curriculum_Vitae
        exclude = ['active']


class AddCvSerializer(ModelSerializer):
    class Meta:
        model = Curriculum_Vitae
        fields = ['id', 'career_goals', 'degree_detail', 'experience_detail', 'skill', 'cv_link', 'foreignLanguage',
                  'user']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }


class AddEmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        exclude = []


class EmployeeSerializer(ModelSerializer):
    # user = UserCompany()
    #
    # def get_company_name(self, obj):
    #     return obj.company.name
    #
    # def get_role_name(self, obj):
    #     return obj.role.name
    #
    # # Thêm trường SerializerMethodField để hiển thị tên công ty
    # company_name = serializers.SerializerMethodField()
    #
    # # Thêm trường SerializerMethodField để hiển thị tên vai trò
    # role_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        exclude = []


class CompanySerializer(ModelSerializer):
    image_path = serializers.SerializerMethodField(source='logo')

    def get_company_of(self, obj):
        return obj.user.username

    def get_city_name(self, obj):
        return obj.city.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    city_name = serializers.SerializerMethodField()
    company_of = serializers.SerializerMethodField()

    def get_image_path(self, obj):
        if obj.logo:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.logo)
            return path

    class Meta:
        model = Company
        fields = ['id', 'name', 'email', 'image_path', 'description', 'address', 'city_name', 'company_of', 'user',
                  'city', 'logo']
        extra_kwargs = {
            'city': {
                'write_only': True
            }, 'image_path': {
                'read_only': True
            }, 'logo': {
                'write_only': True
            },
        }


class AddJobSerializer(ModelSerializer):
    class Meta:
        model = Job
        exclude = ['is_deleted', 'is_checked', 'active']


class CommentSerializer(ModelSerializer):
    user = UserCvSerializer()

    class Meta:
        model = Comment
        exclude = ['company', 'active']


class JobSerializer(ModelSerializer):
    company = CompanySerializer()

    def get_city(self, obj):
        return obj.city.name

    def get_company(self, obj):
        return obj.company.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    city = serializers.SerializerMethodField()
    # company = serializers.SerializerMethodField()

    def get_majors(self, obj):
        return obj.majors.all().values_list('name', flat=True)

    # Thêm trường majors
    majors = serializers.SerializerMethodField()

    class Meta:
        model = Job
        exclude = ['is_deleted', 'is_checked', 'active', 'employee']


class AddMajor(ModelSerializer):
    class Meta:
        model = Major
        exclude = []


class ApplicationSerializer(ModelSerializer):
    cv = CvSerializer()
    user = UserSerializer()
    job = JobSerializer()

    # def get_job_name(self, obj):
    #     return obj.job.name
    #
    # job_name = serializers.SerializerMethodField()

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
        fields = ['id', 'name', 'email', 'image_path', 'description', 'address', 'city']


class AddJobSerializer(ModelSerializer):
    class Meta:
        model = Job
        exclude = ['is_deleted', 'is_checked', 'active']


class AddEmployee(ModelSerializer):
    class Meta:
        model = Employee
        exclude = []


class BlogSerializer(ModelSerializer):
    # user = UserSerializer()
    image_path = serializers.SerializerMethodField(source='image')

    def get_image_path(self, obj):
        if obj.image_blog:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.image_blog)
            return path

    class Meta:
        model = Blog
        exclude = ['image_blog']


class CommentBlogSerializer(ModelSerializer):
    user = UserCvSerializer()

    class Meta:
        model = CommentBlog
        exclude = ['blog', 'active']


class AddCommentBlogSerializer(ModelSerializer):
    class Meta:
        model = CommentBlog
        fields = ['id', 'content', 'blog']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }


class AddCVS(ModelSerializer):
    class Meta:
        model = Curriculum_Vitae
        fields = ['id', 'career_goals', 'degree_detail', 'experience_detail', 'skill', 'cv_link', 'foreignLanguage']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }

class AddApplications(ModelSerializer):
    class Meta:
        model = Application
        exclude = []
        # fields = ['id', 'cover_letter','cv','job']

        extra_kwargs = {
            'user': {
                'read_only': True
            },
        }

#
# class GoogleSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()
#
#     def validate_auth_token(self, auth_token):
#         user_data = google.Google.validate(auth_token)
#         try:
#             user_data['sub']
#         except:
#             raise serializers.ValidationError(
#                 'The token is invalid or expired. Please login again.'
#             )
#
#         if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
#             raise AuthenticationFailed('we cannot authenticate for you!!!')
#         email = user_data['email']
#         name = user_data['email']
#         provider = 'google'
#
#         return register_social_user(
#             provider=provider, email=email, name=name)
#
#
# class FacebookSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()
#
#     def validate_auth_token(self, auth_token):
#         user_data = facebook.Facebook.validate(auth_token)
#
#         try:
#             # user_id = user_data['id']
#             email = user_data['email']
#             name = user_data['name']
#             provider = 'facebook'
#             return register_social_user(
#                 provider=provider,
#                 # user_id=user_id,
#                 email=email,
#                 name=name
#             )
#         except Exception:
#
#             raise serializers.ValidationError(
#                 'The token  is invalid or expired. Please login again.'
#             )
