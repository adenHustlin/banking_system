from rest_framework.pagination import CursorPagination, PageNumberPagination


class CursorOrPageNumberPagination:
    cursor_pagination_class = CursorPagination
    page_number_pagination_class = PageNumberPagination

    def __init__(self):
        self.cursor_pagination = self.cursor_pagination_class()
        self.page_number_pagination = self.page_number_pagination_class()

    def paginate_queryset(self, queryset, request, view=None):
        if "page" in request.query_params:
            return self.page_number_pagination.paginate_queryset(
                queryset, request, view=view
            )
        return self.cursor_pagination.paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        if (
            hasattr(self.page_number_pagination, "page")
            and self.page_number_pagination.page is not None
        ):
            return self.page_number_pagination.get_paginated_response(data)
        return self.cursor_pagination.get_paginated_response(data)
