import uuid
import hmac
import json
import urllib.request

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics,permissions,status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from . import facebook
from .models import *
from .serializers import *
from .paginators import *
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import login, logout
from django.contrib.auth import  authenticate
from .perms import *
from decimal import Decimal
from datetime import datetime,date
import random,hashlib
from .utils import *
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.db.models import F

# class CourseViewSet(viewsets.ViewSet,generics.ListAPIView,generics.RetrieveAPIView):
#     queryset = Company.objects.filter(active=True)
# serializer_class = Com
# permission_classes = [permissions.IsAuthenticated]
