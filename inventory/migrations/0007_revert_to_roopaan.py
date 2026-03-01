# Migration to revert brand to ROOPAAN'S

from django.db import migrations


def revert_brand_to_roopaan(apps, schema_editor):
    """Update ROOPAN'S back to ROOPAAN'S in existing products"""
    Product = apps.get_model('inventory', 'Product')
    updated_count = Product.objects.filter(brand="ROOPAN'S").update(brand="ROOPAAN'S")
    print(f"Updated {updated_count} products to use ROOPAAN'S")


def reverse_revert(apps, schema_editor):
    """Reverse migration"""
    Product = apps.get_model('inventory', 'Product')
    Product.objects.filter(brand="ROOPAAN'S").update(brand="ROOPAN'S")


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_fix_brand_typo'),
    ]

    operations = [
        migrations.RunPython(revert_brand_to_roopaan, reverse_revert),
    ]
