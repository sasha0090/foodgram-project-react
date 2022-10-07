from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Название", max_length=30)
    color = models.CharField("Цвет", max_length=7)
    slug = models.SlugField("Слаг", unique=True, max_length=30)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=30)
    measurement_unit = models.CharField("Ед. измерения", max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]

        verbose_name = "Ингредиенты"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="own_recipes"
    )
    name = models.CharField("Название", max_length=50)
    image = models.ImageField(upload_to="recipes/")
    text = models.TextField("Описание", max_length=200)
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredients", related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    cooking_time = models.IntegerField(
        "Время приготовления", validators=[MinValueValidator(1)]
    )
    create_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, blank=True
    )
    favorite = models.ManyToManyField(
        User, through="FavoriteRecipe", related_name="recipes"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-create_date"]

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="favorite_recipes", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="favorite_recipes", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_favorite",
            )
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.recipe} - {self.user}"


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="ingredientsamount", on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, related_name="ingredientsamount", on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        "Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        return (
            f"{self.amount}{self.ingredient.measurement_unit} - "
            + f"{self.ingredient} - {self.recipe}"
        )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="shopping_cart", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="shopping_cart", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_cart",
            )
        ]

        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"Продукты из {self.recipe} в корзине у {self.user}"
