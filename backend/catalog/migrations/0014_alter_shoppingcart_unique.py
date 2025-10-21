# Generated manually to alter unique constraint for ShoppingCart
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0013_shoppingcart_shoppingcartitem_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="shoppingcart",
            name="unique_open_cart_per_user_brand",
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(("status", "OPEN")),
                name="unique_open_cart_per_user",
            ),
        ),
    ]
