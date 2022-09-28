from django_filters import rest_framework as df_filters
from rest_framework import filters

from recipes import models


class RecipeFilter(df_filters.FilterSet):
    tags = df_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=models.Tag.objects.all(),
    )

    is_favorited = df_filters.CharFilter(method="filter_is_favorited")

    is_in_shopping_cart = df_filters.CharFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = models.Recipe
        fields = ["tags", "author"]

    def filter_is_favorited(self, queryset, name, value):
        if value == "1":
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == "1":
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class CustomSearchFilter(filters.SearchFilter):
    search_param = "name"
