import uuid
import hmac
import json
import urllib.request

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
# from . import facebook
from .models import *
from .serializers import *
from .paginators import *
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from .perms import *
from decimal import Decimal
from datetime import datetime, date
import random, hashlib
# from .utils import *
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist


class CompanyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Company.objects.filter(Q(is_checked=True) & Q(active=True)).order_by('create_date')
    serializer_class = CompanySerializer
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]

    # def get_queryset(self):
    #     query = self.queryset
    #     kw = self.request.query_params.get('kw')
    #     if kw:
    #         query = query.filter(name__icontains=kw)
    #     return query
    def list(self, request):
        queryset = self.queryset
        kw = self.request.query_params.get('kw')
        if kw:
            queryset = queryset.filter(name__icontains=kw)
        page = self.paginate_queryset(queryset)  # Sử dụng phân trang của CompanyPaginator

        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)
        # return Response(self.serializer_class(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='jobs')
    def get_jobs(self, request, pk):
        company = self.get_object()
        jobs = company.jobs.filter(active=True)

        kw = self.request.query_params.get('kw')
        if kw is not None:
            jobs = jobs.filter(name__icontains=kw)

        return Response(data=JobSerializer(jobs, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='comments')
    def comments(self, request, pk=None):
        company = self.get_object()  # Lấy đối tượng công ty dựa trên pk
        comments = Comment.objects.filter(company=company)  # Lấy danh sách bình luận của công ty
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='images')
    def get_images(self, request, pk):
        images = self.get_object().images
        return Response(data=ImageCompanySerializer(images, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class CityViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = City.objects.filter(active=True).prefetch_related('companies', 'jobs')
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = self.queryset
        kw = self.request.query_params.get('kw')

        if kw:
            queryset = queryset.filter(name__icontains=kw)
        return queryset

    @action(methods=['get'], detail=True, url_path='companies')
    def get_companies(self, request, pk):
        city = self.get_object()
        companies = city.companies.filter(is_checked=True)

        kw = self.request.query_params.get('kw')
        if kw is not None:
            companies = companies.filter(name__icontains=kw)

        return Response(data=CompanySerializer(companies, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='jobs')
    def get_jobs(self, request, pk):
        city = self.get_object()
        jobs = city.jobs.filter(active=True)

        kw = self.request.query_params.get('kw')
        if kw is not None:
            jobs = jobs.filter(name__icontains=kw)

        return Response(data=JobSerializer(jobs, many=True).data, status=status.HTTP_200_OK)


class JobViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Job.objects.filter(Q(is_checked=True) & Q(active=True))
    serializer_class = JobSerializer
    pagination_class = JobPaginator
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Lọc công việc theo tên công ty
        company_id = self.request.query_params.get('company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        # Lọc công việc theo tên công việc
        kw = self.request.query_params.get('kw')
        if kw:
            queryset = queryset.filter(name__icontains=kw)

        # Lọc công việc theo mức lương
        min_salary = self.request.query_params.get('min_salary')
        max_salary = self.request.query_params.get('max_salary')
        if min_salary and max_salary:
            queryset = queryset.filter(salary_from__gte=min_salary, salary_to__lte=max_salary)

        # Lọc công việc theo thành phố
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(city_id=city_id)

        # Lọc công việc có yêu cầu kinh nghiệm
        experience_required = self.request.query_params.get('experience_required')
        if experience_required:
            queryset = queryset.filter(experience_required=True)

        return queryset


class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['partial_update', 'update', 'retrieve', 'current_user', 'change_password',
                           'get_list_user_applications',
                           'get_list_user_cvs']:
            return [UserOwnerPermission()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        role_id = request.data.get('role', None)

        try:
            role = Role.objects.get(id=role_id)
            if role.name not in ['Candidate', 'Company']:
                return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = request.data.copy()
        user_data['role'] = role.id

        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], url_path='current_user', detail=False)
    def current_user(self, request):
        return Response(data=UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='applications', detail=False)
    def get_list_user_applications(self, request):
        user = request.user
        if user:
            applications = Application.objects.filter(user=user)
            paginator = pagination.PageNumberPagination()
            paginator.page_size = 10
            applications = paginator.paginate_queryset(applications, request)
            return paginator.get_paginated_response(ApplicationSerializer(applications, many=True).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='change_password', detail=True)
    def change_password(self, request, pk):
        user = request.user
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='cvs', detail=False)
    def get_list_user_cvs(self, request):
        user = request.user
        if user:
            cvs = Curriculum_Vitae.objects.filter(user=user)
            paginator = pagination.PageNumberPagination()
            paginator.page_size = 10
            cvs = paginator.paginate_queryset(cvs, request)
            return paginator.get_paginated_response(CvSerializer(cvs, many=True).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserCompanyViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView):
    # queryset = Company.objects.all()
    queryset = Company.objects.filter(Q(is_checked=True) & Q(active=True)).order_by('create_date')
    serializer_class = AddCompanySerializer
    pagination_class = CompanyPaginator
    permission_classes = [OwnerCompanyPermission]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Company.objects.filter(user=user)
        else:
            return Company.objects.none()

    def list(self, request):
        queryset = self.get_queryset()  # Lấy queryset dựa trên user
        kw = self.request.query_params.get('kw')  # Lấy tham số tìm kiếm
        is_checked = self.request.query_params.get('is_checked')  # Lấy tham số is_checked

        if is_checked:
            if is_checked == 'true':
                # Lọc các công ty có is_checked là True
                queryset = queryset.filter(is_checked=True)
            elif is_checked == 'false':
                # Lọc các công ty có is_checked là False
                queryset = queryset.filter(is_checked=False)

        if kw:
            queryset = queryset.filter(name__icontains=kw)  # Lọc theo tên công ty

        page = self.paginate_queryset(queryset)  # Phân trang
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def list_employee_in_company(self, request, pk=None):
        company = self.get_object()
        employees = Employee.objects.filter(company=company)
        return Response(EmployeeSerializer(employees, many=True).data)

    @action(detail=True, methods=['post'])
    def create_employee(self, request, pk=None):
        company = self.get_object()  # Lấy đối tượng công ty dựa trên pk

        # Tạo người dùng
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Tạo nhân viên
        employee_data = {
            'user': user.id,
            'company': company.id,
            'role': request.data.get('role')
        }
        employee_serializer = AddEmployee(data=employee_data)
        employee_serializer.is_valid(raise_exception=True)
        employee = employee_serializer.save()

        return Response({
            'company': CompanySerializer(company).data,
            'employee': EmployeeSerializer(employee).data
        }, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = AddCommentSerializer

    def get_permissions(self):
        if self.action in ['partial_update', 'update', 'destroy']:
            return [OwnerPermission()]
        return [permissions.IsAuthenticated()]

    def create(self, request):
        user = request.user
        if user:
            try:
                content = request.data.get('content')
                rating = request.data.get('rating')
                company = Company.objects.get(pk=request.data.get('company'))
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if company and content:
                comment = Comment.objects.create(user=user, company=company, content=content, rating=rating)
                return Response(data=AddCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"error_message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

# class EmployeeCompanyViewset(viewsets.ViewSet):
#  @action(detail=False, methods=['POST'],
#             permission_classes=[IsAuthenticated, (AdminPermission | OwnerEmployeePermission)])
#     def create_job(self, request):
#         user = request.user
#
#         try:
#             employee = Employee.objects.get(user=user)
#         except Employee.DoesNotExist:
#             return Response({"message": "Không tìm thấy nhân viên tương ứng."}, status=status.HTTP_400_BAD_REQUEST)
#
#         company = employee.company
#
#         job_data = request.data.copy()
#         job_data['employee'] = employee.id
#         job_data['company'] = company.id
#
#         serializer = JobSerializer(data=job_data)
#         serializer.is_valid(raise_exception=True)
#         job = serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
