from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "get_favorite"]
    list_filter = ["author", "tags"]
    search_fields = ["name"]
    inlines = [IngredientInline]

    def get_favorite(self, obj):
        favorite_total = obj.favorite.count()
        return favorite_total

    get_favorite.short_description = "В избранном"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    list_filter = ["measurement_unit"]
    search_fields = ["name"]


admin.site.register(ShoppingCart)
admin.site.register(Tag)
admin.site.register(RecipeIngredients)
admin.site.register(FavoriteRecipe)
