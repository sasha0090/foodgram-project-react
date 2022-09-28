from rest_framework import pagination
from rest_framework.response import Response


class OnlyDataPagination(pagination.PageNumberPagination):
    """Пагинация без системного текста"""

    def get_paginated_response(self, data):
        return Response(data)
