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
        exclude = ['user_permissions', 'groups']
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


class UserCompany(ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        fields = ['avatar_path', 'username', 'first_name', 'last_name', 'phone', 'email']


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        exclude = []


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        field = ['id', 'name']


class CommentSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        exclude = ['company']


class CompanySerializer(ModelSerializer):
    user = UserCompany()

    class Meta:
        model = Company
        exclude = ['is_checked']


class UserCompany(ModelSerializer):
    avatar_path = serializers.SerializerMethodField(source='avatar')

    def get_avatar_path(self, obj):
        if obj.avatar:
            path = '{cloud_path}{image_name}'.format(cloud_path=cloud_path, image_name=obj.avatar)
            return path

    class Meta:
        model = User
        fields = ['avatar_path', 'username', 'first_name', 'last_name', 'phone', 'email']


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
        fields = ['name','id']


class CvSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Curriculum_Vitae
        exclude = []


class ApplicationSerializer(ModelSerializer):
    cv = CvSerializer()
    user = UserSerializer()
    company = CompanySerializer()

    class Meta:
        model = Application
        exclude = []
