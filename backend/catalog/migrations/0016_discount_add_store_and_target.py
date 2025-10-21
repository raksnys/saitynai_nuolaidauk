from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0015_remove_shoppingcart_brand"),
    ]

    operations = [
        migrations.AddField(
            model_name="discount",
            name="store",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name="discounts", to="catalog.store"),
        ),
        migrations.AlterField(
            model_name="discount",
            name="target_type",
            field=models.CharField(max_length=20, choices=[('product', 'Product'), ('category', 'Category'), ('brand', 'Brand'), ('store', 'Store')]),
        ),
    ]
