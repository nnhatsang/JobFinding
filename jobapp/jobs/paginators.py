from rest_framework import pagination


class CompanyPaginator(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'


class JobPaginator(pagination.PageNumberPagination):
    page_size = 5
    page_query_param = 'page'


class CommentPaginator(pagination.PageNumberPagination):
    page_size = 5
    page_query_param = 'page'
