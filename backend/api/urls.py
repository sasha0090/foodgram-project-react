from django.urls import path, include
from rest_framework import routers

from . import views

router_v1 = routers.DefaultRouter()

router_v1.register(
    "recipes/download_shopping_cart",
    views.ShoppingCartViewSet,
    basename="download_shopping_cart",
)
router_v1.register("recipes", views.RecipeViewSet, basename="recipes",)
router_v1.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    views.FavoriteViewSet,
    basename="favorite",
)

router_v1.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    views.ShoppingCartViewSet,
    basename="shopping_cart",
)
router_v1.register(
    r"users/(?P<user_id>\d+)/subscribe",
    views.UserSubscribeViewSet,
    basename="subscribe", )


router_v1.register("tags", views.TagViewSet)
router_v1.register("ingredients", views.IngredientViewSet)


urlpatterns = [
    path("", include(router_v1.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
