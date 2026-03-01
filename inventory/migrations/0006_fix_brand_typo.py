# Generated migration to fix brand name typo

from django.db import migrations


def fix_brand_typo(apps, schema_editor):
    """Update ROOPAAN'S to ROOPAN'S in existing products"""
    Product = apps.get_model('inventory', 'Product')
    updated_count = Product.objects.filter(brand="ROOPAAN'S").update(brand="ROOPAN'S")
    print(f"Updated {updated_count} products with correct brand name")


def reverse_brand_fix(apps, schema_editor):
    """Reverse migration (not really needed but good practice)"""
    Product = apps.get_model('inventory', 'Product')
    Product.objects.filter(brand="ROOPAN'S").update(brand="ROOPAAN'S")


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_product_brand'),
    ]

    operations = [
        migrations.RunPython(fix_brand_typo, reverse_brand_fix),
    ]
