from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import mixins, serializers
from .filters import CustomSearchFilter, RecipeFilter
from .mixins import GetViewSet
from .pagination import LimitPagination, OnlyDataPagination
from .permissions import IsAuthorOrStaffOrReadOnly
from .services import download_shopping_cart
from recipes import models
from users.models import Subscribe

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrStaffOrReadOnly]
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RecipeFilter
    filterset_fields = ["tags", "author__id"]
    ordering = ["-create_date"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["delete"], detail=True)
    def delete(self, request, recipe_id):
        recipe = get_object_or_404(models.Recipe, pk=recipe_id)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = OnlyDataPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(GetViewSet):
    permission_classes = [AllowAny]
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = OnlyDataPagination
    filter_backends = [CustomSearchFilter]
    search_fields = ["^name"]


class FavoriteViewSet(mixins.CreateDeleteViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FavoriteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            models.Recipe, pk=self.kwargs.get("recipe_id")
        )

        title_data = {"recipe": recipe, "user": self.request.user}

        serializer.save(**title_data)

    @action(methods=["delete"], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=recipe_id)
        favorite = get_object_or_404(
            models.FavoriteRecipe, user=user, recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            models.Recipe, pk=self.kwargs.get("recipe_id")
        )

        title_data = {"recipe": recipe, "user": self.request.user}

        serializer.save(**title_data)

    def list(self, request, *args, **kwargs):
        return download_shopping_cart(self.request.user)

    @action(methods=["delete"], detail=True)
    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=recipe_id)
        cart = get_object_or_404(models.ShoppingCart, user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscribeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSubscribeSerializer
    pagination_class = LimitPagination

    def get_queryset(self):
        subscriber = self.request.user.subscribers.all()
        return subscriber

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get("user_id"))
        title_data = {"subscriber": self.request.user, "author": author}
        if serializer.is_valid():
            serializer.save(**title_data)

    @action(methods=["delete"], detail=True)
    def delete(self, request, user_id):
        user = self.request.user

        author = get_object_or_404(User, pk=user_id)

        subscribe = get_object_or_404(
            Subscribe, subscriber=user, author=author
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
