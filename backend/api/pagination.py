from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Пользовательская пагинация для API.
    Размер страницы устанавливается из настроек.
    """
    page_size = settings.CUSTOM_PAGE_SIZE
    page_size_query_param = 'limit'
