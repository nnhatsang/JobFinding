from rest_framework import permissions


class OwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user == obj.user)


class UserOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user == obj)


class AdminPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class OwnerEmployeePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role.name == 'Employee')


class OwnerCV_AppPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role.name == 'Candidate')


class OwnerCompanyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Kiểm tra xem người dùng có quyền xem công ty này hay không
        return obj.user == request.user and request.user.role.name == 'Company'
