# Generated migration to remove whatsapp fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0002_sale_customer_phone_sale_whatsapp_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='customer_phone',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='whatsapp_sent',
        ),
    ]
