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
from django.db import transaction

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from datetime import datetime

current_datetime = datetime.now()


class CompanyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Company.objects.filter(Q(is_checked=True) & Q(active=True)).order_by('create_date')
    serializer_class = CompanySerializer
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    parser_classes = [MultiPartParser, ]
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

        jobs = jobs.filter(is_checked=True)

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

    def create(self, request):
        # Đảm bảo rằng role_name là "Company"
        role_name = 'Company'

        # Xác định role_id dựa trên role_name
        try:
            role = Role.objects.get(name=role_name)
            role_id = role.id
        except Role.DoesNotExist:
            # Nếu role không tồn tại, bạn có thể xử lý theo ý muốn của mình
            return Response({"error": "Role 'Company' does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'email': request.data.get('email'),
            'avatar': request.data.get('avatar'),
            'dob': request.data.get('dob'),
            'description': request.data.get('description'),
            'gender': request.data.get('gender'),
            'phone': request.data.get('phone'),
            'address': request.data.get('address'),
            'degree': request.data.get('degree'),
            'role': role_id  # Thêm role_id vào dữ liệu user
        }

        with transaction.atomic():  # Mở giao dịch
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

            company_data = {
                'user': user.id,  # Sử dụng user.id đã được tạo
                'name': request.data.get('name'),
                'email': request.data.get('email_company'),
                'logo': request.data.get('logo'),
                'address': request.data.get('company_address'),
                'city': request.data.get('city_company'),
                'description': request.data.get('company_description'),
            }

            company_serializer = CompanySerializer(data=company_data)
            company_serializer.is_valid(raise_exception=True)
            company = company_serializer.save()

            employee_data = {
                'user': user.id,
                'company': company.id,
                'role': role_id
            }

            employee_serializer = AddEmployeeSerializer(data=employee_data)
            employee_serializer.is_valid(raise_exception=True)
            employee = employee_serializer.save()

        return Response({"message": "Company created successfully"}, status=status.HTTP_201_CREATED)


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
    queryset = Job.objects.filter(Q(is_checked=True) & Q(active=True) & Q(end_date__gte=current_datetime))
    serializer_class = JobSerializer
    pagination_class = CompanyPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'company']  # Các trường cần tìm kiếm

    def filter_queryset(self, queryset):
        # Lọc theo tên công việc và mô tả
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q) | queryset.filter(description__icontains=q) | queryset.filter(
                company__name__icontains=q)

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
            queryset = queryset.filter(Q(age_from__gte=age_to) & Q(age_to__lte=age_from))
        elif age_from:
            queryset = queryset.filter(age_to__gte=age_from)
        elif age_to:
            queryset = queryset.filter(age_from__lte=age_to)

        # Lọc theo tên thành phố (city name)
        city_name = self.request.query_params.get('city_name')
        if city_name:
            queryset = queryset.filter(city__name__icontains=city_name)

        return queryset

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticated, OwnerEmployeePermission, OwnerCompanyPermission])
    def company_applications(self, request, pk=None):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current user belongs to the same company as the job
        user = self.request.user
        if user.role.name != "Company" or user.company.id != job.company.id:
            raise PermissionDenied("You don't have permission to view applications for this job.")

        applications = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

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
            "job_required": request.data.get('job_required'),
            "type_job": request.data.get('type_job'),
            "quantity": request.data.get('quantity'),
            "sex_required": request.data.get('sex_required'),
            "experience_required": request.data.get('experience_required'),

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
                           'list_applications',
                           'list_cvs']:
            return [UserOwnerPermission()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        role_name = 'Candidate'

        # Kiểm tra xem vai trò "Candidate" đã tồn tại trong cơ sở dữ liệu chưa
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            # Nếu không tồn tại, hãy tạo một vai trò mới có rolename là "Candidate"
            role = Role.objects.create(name=role_name)

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

    @action(methods=['get'], detail=False, url_path='list_cvs')
    def list_cvs(self, request, pk=None):
        # user = self.get_object()
        cvs = Curriculum_Vitae.objects.filter(user=self.request.user, is_deleted=False)
        serializer = CvSerializer(cvs, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='list_applications')
    def list_applications(self, request, pk=None):
        # user = self.get_object()
        cvs = Application.objects.filter(user=self.request.user)
        serializer = ApplicationSerializer(cvs, many=True)
        return Response(serializer.data)

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

    #

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[OwnerEmployeePermission, OwnerCompanyPermission])
    def applications(self, request, pk=None):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        applications = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

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
                'email': request.data.get('email_company'),
                'logo': request.data.get('logo'),
                'address': request.data.get('company_address'),
                'city': request.data.get('city_company'),
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


class CvViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Curriculum_Vitae.objects.filter(is_deleted=False)
    serializer_class = AddCvSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [OwnerPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Curriculum_Vitae.objects.filter(user=self.request.user).order_by('-update_date')
        return Curriculum_Vitae.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update']:
            return CvSerializer  # Change this to your desired serializer class
        return AddCvSerializer

    @action(detail=False, methods=['post'])
    def create_cv(self, request):
        serializer = AddCvSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationViewset(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView, generics.RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = AddApplications

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [OwnerPermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Application.objects.filter(user=self.request.user).order_by('-update_date')
        return Application.objects.none()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApplicationSerializer  # Change this to your desired serializer class
        return AddApplications

    @action(detail=False, methods=['post'])
    def create_application(self, request):
        user = self.request.user
        # job_id = request.data.get('job_id')  # Lấy thông tin job từ request data
        # cv_id = request.data.get('cv_id')  # Lấy thông tin CV từ request data
        #
        # try:
        #     job = Job.objects.get(id=job_id)
        # except Job.DoesNotExist:
        #     return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        #
        # cv = None
        # if cv_id:
        #     try:
        #         cv = Curriculum_Vitae.objects.get(id=cv_id)
        #     except Curriculum_Vitae.DoesNotExist:
        #         return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)
        #
        # application_data = {
        #     "user": user.id,
        #     "job": job.id,
        #     "cv": cv.id if cv else None,  # Lưu cv_id nếu có hoặc None nếu không có
        #     "cover_letter": request.data.get('cover_letter'),
        #     # Các trường thông tin khác của application
        # }

        # application_serializer = AddApplications(data=application_data)
        # application_serializer.is_valid(raise_exception=True)
        # new_application = application_serializer.save()

        serializer = AddApplications(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # return Response(ApplicationSerializer(new_application).data, status=status.HTTP_201_CREATED)


# xử lý blog cho các bài đăng blog
class BlogViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Blog.objects.filter(active=True)
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update']:
            return [UserOwnerPermission()]
        return [permissions.AllowAny()]


class AdminCompanyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
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


# stats

class StatsView(TemplateView):
    template_name = 'stats_template.html'

    def get_context_data(self, **kwargs):
        # Trích xuất dữ liệu thống kê từ các mô hình (models) và chuẩn bị dữ liệu cho biểu đồ
        user_count = User.objects.count()
        job_count = Job.objects.count()
        cv_count = Curriculum_Vitae.objects.count()
        application_count = Application.objects.count()

        # Dữ liệu biểu đồ
        chart_data = {
            'labels': ['Users', 'Jobs', 'CVs', 'Applications'],
            'datasets': [{
                'data': [user_count, job_count, cv_count, application_count],
                'label': 'Counts',
                'backgroundColor': ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(75, 192, 192, 0.2)',
                                    'rgba(153, 102, 255, 0.2)'],
                'borderColor': ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)'],
                'borderWidth': 1,
            }]
        }

        return {
            'chart_data': chart_data
        }


class StatsChart(BaseLineChartView):
    model = User  # Điều này có thể thay đổi dựa trên mô hình bạn muốn thống kê
    date_field = 'created_date'
    values_field = 'id'
    title = 'Thống kê người dùng'  # Đổi tên tùy ý


def stats(request):
    # Thống kê số lượng người dùng theo giới tính
    gender_stats = User.objects.values('gender').annotate(count=Count('id'))

    # Thống kê số lượng người dùng theo vai trò
    role_stats = User.objects.values('role__name').annotate(count=Count('id'))

    # Dữ liệu để truyền đến template
    chart_data = {
        'gender_stats': gender_stats,
        'role_stats': role_stats,
    }

    return render(request, 'stats.html', {'chart': chart_data})
