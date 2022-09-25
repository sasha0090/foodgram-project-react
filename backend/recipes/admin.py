from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredients, FavoriteRecipe, ShoppingCart


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)


admin.site.register(ShoppingCart)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredients)
admin.site.register(FavoriteRecipe)