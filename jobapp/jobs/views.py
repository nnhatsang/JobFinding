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
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied


class CompanyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Company.objects.filter(Q(is_checked=True) & Q(active=True)).order_by('create_date')
    serializer_class = CompanySerializer
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'city__name']  # Các trường cần tìm kiếm

    def filter_queryset(self, queryset):
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q) | queryset.filter(city__name__icontains=q)

        return queryset

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

    @action(detail=True, methods=['get'], permission_classes=[OwnerCompanyPermission])
    def employees(self, request, pk=None):
        company = self.get_object()  # Lấy đối tượng công ty dựa trên pk
        employees = company.employees.all()  # Lấy danh sách các employee của công ty

        # Tùy chọn lọc theo tên employee, ví dụ: ?kw=John
        kw = self.request.query_params.get('kw')
        if kw is not None:
            employees = employees.filter(user__username__icontains=kw)

        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = City.objects.filter(active=True).prefetch_related('companies', 'jobs')
    serializer_class = CitySerializer
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name']  # Các trường cần tìm kiếm

    def filter_queryset(self, queryset):
        # Lọc theo tên thành phố
        q = self.request.query_params.get("search")
        if q:
            queryset = queryset.filter(name__icontains=q)

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
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']  # Các trường cần tìm kiếm

    def filter_queryset(self, queryset):
        # Lọc theo tên công việc và mô tả
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q) | queryset.filter(description__icontains=q)

        # Lọc theo mức lương
        salary_from = self.request.query_params.get('salary_from')
        salary_to = self.request.query_params.get('salary_to')
        if salary_from and salary_to:
            queryset = queryset.filter(salary_from__gte=salary_from, salary_to__lte=salary_to)
        elif salary_from:
            queryset = queryset.filter(salary_from__gte=salary_from)
        elif salary_to:
            queryset = queryset.filter(salary_to__lte=salary_to)

        # Lọc theo tên chuyên ngành (major name)
        major_name = self.request.query_params.get('major_name')
        if major_name:
            queryset = queryset.filter(majors__name__icontains=major_name)

        # Lọc theo độ tuổi
        age_from = self.request.query_params.get('age_from')
        age_to = self.request.query_params.get('age_to')
        if age_from and age_to:
            queryset = queryset.filter(Q(age_from__lte=age_to) & Q(age_to__gte=age_from))
        elif age_from:
            queryset = queryset.filter(age_to__gte=age_from)
        elif age_to:
            queryset = queryset.filter(age_from__lte=age_to)

        # Lọc theo tên thành phố (city name)
        city_name = self.request.query_params.get('city_name')
        if city_name:
            queryset = queryset.filter(city__name__icontains=city_name)

        return queryset

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated, OwnerEmployeePermission, OwnerCompanyPermission])
    def create_job(self, request):
        # Lấy thông tin người dùng đăng nhập
        user = self.request.user
        role_name = user.role.name

        # Kiểm tra role_name nếu không phải là "Company" hoặc "Employee" thì không được thêm công việc
        if role_name not in ["Company", "Employee"]:
            raise PermissionDenied("You don't have the required role to create a job.")

        try:
            # Lấy thông tin employee từ thông tin người dùng
            employee = Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        major_ids = request.data.get('major_ids', [])  # Lấy danh sách major_ids từ request

        job_data = {
            "company": employee.company.id,
            "name": request.data.get('name'),
            "description": request.data.get('description'),
            "salary_from": request.data.get('salary_from'),
            "salary_to": request.data.get('salary_to'),
            "age_from": request.data.get('age_from'),
            "age_to": request.data.get('age_to'),

            "position": request.data.get('position'),
            "degree_required": request.data.get('degree_required'),
            "end_date": request.data.get('end_date'),
            "city": request.data.get('city'),
            "end_date": request.data.get('end_date'),
            "job_required": request.data.get('job_required'),
            "type_job": request.data.get('type_job'),

            # Các trường thông tin khác của công việc
            "employee": employee.id
        }

        job_serializer = AddJobSerializer(data=job_data)
        job_serializer.is_valid(raise_exception=True)
        new_job = job_serializer.save()
        for major_id in major_ids:
            major = Major.objects.get(pk=major_id)
            job_serializer.majors.add(major)

        return Response(JobSerializer(new_job).data, status=status.HTTP_201_CREATED)


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

        if role_id is not None:
            try:
                role = Role.objects.get(id=role_id)
                if role.name not in ['Candidate', 'Company']:
                    return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({'error': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            role_name = request.data.get('role_name', None)  # Lấy tên role từ request
            if role_name == 'Company':
                try:
                    role = Role.objects.get(name=role_name)
                except ObjectDoesNotExist:
                    return Response({'error': 'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                role = Role.objects.get(id=4)  # Chọn role mặc định

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

    @action(methods=['post'], url_path='change_password', detail=True)
    def change_password(self, request, pk):
        user = request.user
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
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
            role_name = user.role.name

            if role_name in ["Company", "Employee"]:
                if role_name == "Company":
                    queryset = Company.objects.filter(user=user)
                else:
                    employee = Employee.objects.get(user=user)
                    queryset = Company.objects.filter(id=employee.company.id)
            else:
                queryset = Company.objects.none()
        else:
            queryset = Company.objects.none()

        return queryset

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

        role_name = request.data.get('role')
        if role_name not in ['Company', 'Employee', 'Candidate']:
            return Response({"error": "Invalid role name"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'email': request.data.get('email'),
            'avatar': request.data.get('avatar'),
            'dob': request.data.get('dob'),
            'description': request.data.get('description'),
            'gender': request.data.get('gender'),
            'phone': request.data.get('phone'),
            'address': request.data.get('address')
        }

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        if role_name == 'Company':
            company_data = {
                'user': user.id,
                'name': request.data.get('name'),
                'email': request.data.get('email'),
                'logo': request.data.get('logo'),
                'address': request.data.get('company_address'),
                'city': request.data.get('city_id'),
                'description': request.data.get('company_description'),
                'is_checked': request.data.get('is_checked')
            }
            company_serializer = CompanySerializer(data=company_data)
            company_serializer.is_valid(raise_exception=True)
            company = company_serializer.save()

        elif role_name == 'Employee':
            employee_data = {
                'user': user.id,
                'company': company.id,
                'role': Role.objects.get(name='Employee').id
            }
            employee_serializer = EmployeeSerializer(data=employee_data)
            employee_serializer.is_valid(raise_exception=True)
            employee = employee_serializer.save()

        # Nếu role là Candidate, sẽ không cần tạo thêm đối tượng

        return Response({"message": "Employee created successfully"}, status=status.HTTP_201_CREATED)


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


class EmployeeCompanyViewset(viewsets.ViewSet, generics.UpdateAPIView, ):
    queryset = Employee.objects.all()
    serializer_class = JobSerializer
    pagination_class = CompanyPaginator
    permission_classes = [IsAuthenticated, OwnerEmployeePermission | OwnerCompanyPermission]


class CvViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = Curriculum_Vitae.objects.filter(is_deleted=False)
    serializer_class = CvSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [OwnerPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Curriculum_Vitae.objects.filter(user=self.request.user).order_by('-update_date')
        return Curriculum_Vitae.objects.none()

    @action(detail=False, methods=['post'])
    def create_cv(self, request):
        serializer = AddCvSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationViewset(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [OwnerPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Application.objects.filter(user=self.request.user).order_by('-update_date')
        return Application.objects.none()

    @action(detail=False, methods=['post'])
    def create_application(self, request):
        user = self.request.user
        job_id = request.data.get('job_id')  # Lấy thông tin job từ request data
        cv_id = request.data.get('cv_id')  # Lấy thông tin CV từ request data

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        cv = None
        if cv_id:
            try:
                cv = Curriculum_Vitae.objects.get(id=cv_id)
            except Curriculum_Vitae.DoesNotExist:
                return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)

        application_data = {
            "user": user.id,
            "job": job.id,
            "cv": cv.id if cv else None,  # Lưu cv_id nếu có hoặc None nếu không có
            "cover_letter": request.data.get('cover_letter'),
            # Các trường thông tin khác của application
        }

        application_serializer = ApplicationSerializer(data=application_data)
        application_serializer.is_valid(raise_exception=True)
        new_application = application_serializer.save()

        return Response(ApplicationSerializer(new_application).data, status=status.HTTP_201_CREATED)

# xử lý blog cho các bài đăng blog
class BlogViewSet(viewsets.ViewSet,generics.ListAPIView,generics.CreateAPIView):
    queryset = Blog.objects.filter(active=True)
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update']:
            return [UserOwnerPermission()]
        return [permissions.AllowAny()]

class AdminCompanyViewSet(viewsets.ViewSet,generics.ListAPIView,generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = CompanyPaginator
    permission_classes = [AdminPermission]
    filter_fields = ['is_checked', 'active']  # Cho phép lọc theo các trường is_checked và active

    @action(methods=['put'], detail=True, url_path='approve')
    def approve_company(self, request, pk):
        company = self.get_object()

        if company.is_checked:
            return Response({'detail': 'Company is already approved.'}, status=status.HTTP_400_BAD_REQUEST)

        company.is_checked = True
        company.save()

        return Response({'detail': 'Company approved successfully.'}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()




#
#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return Response(data={'message': "Login successfully"}, status=status.HTTP_202_ACCEPTED)
#         else:
#             return Response(data={'error_msg': "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def logout_view(request):
#     logout(request)
#     return Response(status=status.HTTP_200_OK)
#
#
# class AuthInfo(APIView):
#     def get(self, request):
#         return Response(data=settings.OAUTH2_INFO, status=status.HTTP_200_OK)
#
#
# class GoogleSocialAuthView(GenericAPIView):
#     serializer_class = GoogleSocialAuthSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth_token'])
#         return Response(data, status=status.HTTP_200_OK)
#
#
# class FacebookSocialAuthView(GenericAPIView):
#     serializer_class = FacebookSocialAuthSerializer
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth_token'])
#         return Response(data, status=status.HTTP_200_OK)
#
#
# class SendMailAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         email = request.data.get('email')
#         subject = request.data.get('subject')
#         content = request.data.get('content')
#         error_msg = None
#         if email and subject and content:
#             send_email = EmailMessage(subject, content, to=[email])
#             send_email.send()
#         else:
#             error_msg = "Send mail failed !!!"
#         if not error_msg:
#             return Response(data={
#                 'status': 'Send mail successfully',
#                 'to': email,
#                 'subject': subject,
#                 'content': content
#             }, status=status.HTTP_200_OK)
#         return Response(data={'error_msg': error_msg},
#                         status=status.HTTP_400_BAD_REQUEST)
