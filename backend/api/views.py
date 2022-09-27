from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as df_filters
from recipes.models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscribe
from . import mixins
from .pagination import OnlyDataPagination
from . import serializers

User = get_user_model()


class RecipeFilter(df_filters.FilterSet):
    tags = df_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = df_filters.CharFilter(method='filter_is_favorited')

    is_in_shopping_cart = df_filters.CharFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value == "1":
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == "1":
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    filter_backends = [df_filters.DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ['tags', 'author']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = OnlyDataPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CustomSearchFilter(filters.SearchFilter):
    search_param = "name"


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = OnlyDataPagination
    filter_backends = [CustomSearchFilter, ]
    search_fields = ['^name', ]


class FavoriteViewSet(mixins.CreateDeleteViewSet):
    serializer_class = serializers.FavoriteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get("recipe_id"))

        title_data = {"recipe": recipe, "user": self.request.user}

        serializer.save(**title_data)

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = get_object_or_404(FavoriteRecipe, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get("recipe_id"))

        title_data = {"recipe": recipe, "user": self.request.user}

        serializer.save(**title_data)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        queryset = ShoppingCart.objects.filter(user=user)
        total_ingredients = {}
        for shopping_cart in queryset:
            recipe = shopping_cart.recipe

            recipe_ingredients = serializers.RecipeIngredientsSerializer(
                recipe.ingredientsamount, many=True).data

            for ingredient in recipe_ingredients:
                name, amount = ingredient['name'], ingredient['amount']
                measurement_unit = ingredient['measurement_unit']

                if total_ingredients.get(name):
                    total_ingredients[name] = {measurement_unit: total_ingredients[name][measurement_unit] + amount}
                else:
                    total_ingredients[name] = {measurement_unit: amount}

        filename = "my-file.txt"

        content = ""

        for ingredient in total_ingredients:
            measurement_unit, amount = total_ingredients[ingredient].popitem()

            content += f"{ingredient} ({measurement_unit}) — {amount}\n"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSubscribeSerializer

    def get_queryset(self):
        subscriber = self.request.user.subscribers.all()
        return subscriber

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get("user_id"))
        title_data = {"subscriber": self.request.user, "author": author}
        if serializer.is_valid():
            serializer.save(**title_data)

    @action(methods=['delete'], detail=True)
    def delete(self, request, user_id):
        user = self.request.user

        author = get_object_or_404(User, pk=user_id)

        subscribe = get_object_or_404(Subscribe, subscriber=user, author=author)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
