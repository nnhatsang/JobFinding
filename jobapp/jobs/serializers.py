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



class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        exclude = []


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        field = ['name']


class CommentSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        exclude = ['company']


class CompanySerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Company
        exclude = ['company']


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        field = ['name']


class CandidateSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Candidate
        exclude = []


class CvSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Curriculum_Vitae
        exclude = []


class ApplicationSerializer(ModelSerializer):
    cv = CvSerializer()
    candidate = CandidateSerializer()
    company = CompanySerializer()

    class Meta:
        model = Application
        exclude = []
