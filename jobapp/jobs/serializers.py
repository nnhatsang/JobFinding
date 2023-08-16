import datetime

from .models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from . import cloud_path


class AddCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'company', 'user', 'rating']
        extra_kwargs = {
            'user': {
                'read_only': True
            }
        }


class UserSerializer(ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_role_name(self, obj):
        return obj.role.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    role_name = serializers.SerializerMethodField()

    # role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(name__in=['Candidate', 'Company']))

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff', 'role', 'is_active', 'is_superuser']

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
        # data = validated_data.copy()
        # role_id = data.pop('role', None)  # Lấy giá trị của trường role
        # user = User(**data)
        # user.set_password(user.password)
        # user.is_active = False
        # user.save()
        # if role_id:
        #     role = Role.objects.get(id=role_id)  # Lấy đối tượng Role dựa trên khóa chính
        #     user.role = role  # Gán vai trò cho người dùng
        #     user.save()
        # return user
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
        fields = ['name']


class UserCvSerializer(ModelSerializer):
    class Meta(UserSerializer.Meta):
        exclude = ['last_login', 'date_joined', 'role', 'is_superuser', 'is_staff', 'is_active', 'user_permissions',
                   'groups']
        # fields = [
        #     'username', 'first_name', 'last_name', 'email', 'dob', 'description', 'gender', 'phone', 'address',
        #     'avatar_path',
        # ]


class CvSerializer(ModelSerializer):
    user = UserCvSerializer()

    class Meta:
        model = Curriculum_Vitae
        exclude = ['active', 'is_deleted']


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
        exclude = []


class CompanySerializer(ModelSerializer):
    image_path = serializers.SerializerMethodField(source='logo')

    def get_company_of(self, obj):
        return obj.user.username

    def get_city(self, obj):
        return obj.city.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    city = serializers.SerializerMethodField()
    company_of = serializers.SerializerMethodField()

    # def get_user(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         return UserCompany(request.user).data
    #     return None

    def get_image_path(self, obj):
        if obj.logo:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.logo)
            return path

    class Meta:
        model = Company
        fields = ['id', 'name', 'email', 'image_path', 'description', 'address', 'city', 'company_of']


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
    # company = CompanySerializer()

    def get_city(self, obj):
        return obj.city.name

    def get_company(self, obj):
        return obj.company.name

    # Thêm trường SerializerMethodField để hiển thị tên công ty
    city = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

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
    # cv = CvSerializer()

    def get_job_name(self, obj):
        return obj.job.name

    job_name = serializers.SerializerMethodField()

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
