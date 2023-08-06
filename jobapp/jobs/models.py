import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

# Create your models here.

GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'), ('other', 'Other'),)
TYPE_JOB_CHOICES = (
    ('full_time', 'Full-Time'),
    ('part_time', 'Part-Time'),
    ('internship', 'Internship'),
    ('contract', 'Contract'),
)


class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Role(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    avatar = CloudinaryField('avatar', default='', null=True)
    dob = models.DateTimeField(null=True, blank=True)
    description = RichTextField(blank=True, null=False)
    gender = models.BooleanField(default=1)
    phone = models.CharField(null=False, max_length=10)
    address = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True, default=4)

    def __str__(self):
        return self.username


class City(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Company(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    logo = CloudinaryField('image', default='', null=True)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='companies')
    description = RichTextField()
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ImageCompany(BaseModel):
    image = CloudinaryField('image', default='')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, related_name='images')
    descriptions = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.descriptions


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employees')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return self.user.username


class Major(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Job(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    name = models.CharField(max_length=255)
    majors = models.ManyToManyField(Major, blank=True)  # Mối quan hệ Many-to-Many với Major
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='jobs', blank=True)
    description = models.TextField()  # Đây là trường mô tả công việc, có thể sử dụng TextField thay cho RichTextField
    salary_from = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    salary_to = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    age_from = models.IntegerField(default=0)
    age_to = models.IntegerField(default=0)
    end_date = models.DateTimeField()
    quantity = models.IntegerField(default=1)
    degree_required = models.TextField()
    is_deleted = models.BooleanField(default=False)
    sex_required = models.BooleanField(default=False)
    probationary_priod = models.IntegerField(default=1)
    position = models.CharField(max_length=100, null=False)
    type_job = models.CharField(max_length=100, choices=TYPE_JOB_CHOICES, default='full_time')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='jobs')
    experience_required = models.BooleanField(default=False)
    job_required = models.TextField()
    is_checked = models.BooleanField(default=False)


class Curriculum_Vitae(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv')
    career_goals = models.TextField()
    degree_detail = models.TextField()
    experience_detail = models.TextField()
    skill = models.TextField()
    cv_link = models.CharField(max_length=255, blank=True)
    foreignLanguage = models.TextField()
    is_deleted = models.BooleanField(default=False)  # Trạng thái ẩn của ứng viên

    def __str__(self):
        return f"CV of {self.user.username}"


class Application(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    cv = models.ForeignKey(Curriculum_Vitae, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/%Y/%m/%d/', null=True)
    apply_date = models.DateTimeField(auto_now_add=True)


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True)
    rating = models.IntegerField(default=5)

    def __str__(self):
        stars = "⭐" * self.rating
        return f"Username: {self.user.username},Role: {self.user.role},Company {self.company.name} : {self.content}: with rating {stars}"
