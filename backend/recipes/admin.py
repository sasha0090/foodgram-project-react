from django.contrib import admin

from . import models


class IngredientInline(admin.TabularInline):
    model = models.RecipeIngredients
    extra = 0
    min_num = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "get_favorite"]
    list_filter = ["author", "tags"]
    search_fields = ["name", "author__username", "tags__name"]
    inlines = [IngredientInline]

    def get_favorite(self, obj):
        return obj.favorite.count()

    get_favorite.short_description = "В избранном"


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    list_filter = ["measurement_unit"]
    search_fields = ["name"]


admin.site.register(models.ShoppingCart)
admin.site.register(models.Tag)
admin.site.register(models.RecipeIngredients)
admin.site.register(models.FavoriteRecipe)
