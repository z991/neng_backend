# __author__ = itsneo1990
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    def get_next_page(self):
        if not self.page.has_next():
            return None
        return self.page.number + 1

    def get_previous_page(self):
        if not self.page.has_previous():
            return None
        return self.page.number - 1

    def get_total_page(self):
        total_count = self.page.paginator.count
        if total_count % self.page_size == 0:
            page_nums = int(total_count / self.page_size)
        else:
            page_nums = int(total_count / self.page_size) + 1
        return page_nums

    def get_paginated_response(self, data):
        for index, each in enumerate(data, start=1):
            each["index"] = index + (self.page.number - 1) * self.page_size
        return Response({
            'page_url': {
                'previous': self.get_previous_link(),
                'next': self.get_next_link(),
            },
            'page_num': {
                'next': self.get_next_page(),
                'previous': self.get_previous_page(),
                'current': self.page.number,
                'total_page': self.get_total_page(),
                'total_count': self.page.paginator.count,
            },
            'results': data
        })
