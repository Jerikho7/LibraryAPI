from rest_framework.pagination import PageNumberPagination


class Paginator(PageNumberPagination):
    """
    Пагинатор для списков объектов с настраиваемым размером страницы.

    Attributes:
        page_size (int): Размер страницы по умолчанию (10 элементов).
        page_size_query_param (str): Параметр запроса для указания размера страницы ('page_size').
        max_page_size (int): Максимальный размер страницы (50 элементов).
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
