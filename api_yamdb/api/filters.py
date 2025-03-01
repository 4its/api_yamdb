from rest_framework import filters


class GenreCategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        genre_slug = request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        category_slug = request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
