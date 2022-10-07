from django.db.models import Sum, F
from django.http import HttpResponse

from recipes.models import ShoppingCart


def download_shopping_cart(user):
    user_cart = ShoppingCart.objects.filter(user=user)
    total_ingredients = user_cart.values(
        ingredient=F("recipe__ingredients__name"),
        measurement_unit=F("recipe__ingredients__measurement_unit")
    ).annotate(amount=Sum("recipe__ingredientsamount__amount"))

    filename = "my-file.txt"
    content = '\n'.join(
        "{ingredient} ({measurement_unit}) — {amount}".format_map(ingredient)
        for ingredient in total_ingredients
    )

    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = "attachment; filename={0}".format(
        filename
    )

    return response
