from django.core.files.base import ContentFile
from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import base64
from django.contrib.auth import get_user_model
from rest_framework.relations import SlugRelatedField

from recipes import models
from users.models import Subscribe


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', required=False)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        fields = ["id", "name", "measurement_unit", "amount"]
        model = models.RecipeIngredients


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ["email", "id", "username", "first_name", "last_name", "is_subscribed",]
        model = User

    def get_is_subscribed(self, obj):
        return False


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source='ingredientsamount'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(source='favorite_recipes')
    is_in_shopping_cart = serializers.SerializerMethodField(
        source='shopping_cart'
    )

    class Meta:
        # fields = "__all__"
        exclude = ('favorite', )
        model = models.Recipe

    def ingredients_set(self, ingredients_amount_data, recipe_instance):
        ingredients = []
        for ingredient_amount in ingredients_amount_data:
            ingredient_id = ingredient_amount["ingredient"]["id"]
            ingredient = get_object_or_404(models.Ingredient, pk=ingredient_id)
            amount = ingredient_amount['amount']

            recipe_ingredients_instance = models.RecipeIngredients(
                ingredient=ingredient, recipe=recipe_instance, amount=amount
            )
            ingredients.append(recipe_ingredients_instance)

        models.RecipeIngredients.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_amount_data = validated_data.pop('ingredientsamount')
        instance = super().create(validated_data)
        self.ingredients_set(ingredients_amount_data, instance)
        return instance

    def update(self, instance, validated_data):
        ingredients_amount_data = validated_data.pop('ingredientsamount')
        instance = super().update(instance, validated_data)
        models.RecipeIngredients.objects.filter(recipe=instance).delete()
        self.ingredients_set(ingredients_amount_data, instance)

        return instance

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        is_favorited = models.FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        is_in_shopping_cart = models.ShoppingCart.objects.filter(recipe=obj, user=user).exists()
        return is_in_shopping_cart

    def to_internal_value(self, data):
        self.fields['tags'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=models.Tag.objects.all()
        )
        return super(RecipeSerializer, self).to_internal_value(data)


class CustomRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ["id", "name", "image", "cooking_time", ]
        model = models.Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = models.FavoriteRecipe

    def validate(self, attrs):
        request = self.context.get("request")
        recipe_id = self.context.get("view").kwargs.get("recipe_id")

        review = models.FavoriteRecipe.objects.filter(
            recipe_id=recipe_id, user=request.user
        ).exists()

        if review and request.method == "POST":
            raise ValidationError(
                "Рецепт уже в избранном!"
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return CustomRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = models.ShoppingCart

    def validate(self, attrs):
        request = self.context.get("request")
        recipe_id = self.context.get("view").kwargs.get("recipe_id")

        review = models.ShoppingCart.objects.filter(
            recipe_id=recipe_id, user=request.user
        ).exists()

        if review and request.method == "POST":
            raise ValidationError(
                "Рецепт уже в списке покупок!"
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return CustomRecipeSerializer(
            instance.recipe, context=context).data


class UserSubscribeSerializer(serializers.ModelSerializer):
    subscriber = SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    author = SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        fields = "__all__"
        model = Subscribe

    def create(self, validated_data):
        subscriber = validated_data['subscriber']
        author = validated_data["author"]

        if subscriber == author:
            raise serializers.ValidationError("Нельзя подписаться на себя!")

        if subscriber.authors.filter(author=author).exists():
            raise serializers.ValidationError(
                {'detail': 'Вы уже подписаны на автора'}
            )
        return super().create(validated_data)
