# Generated by Django 4.2.11 on 2024-03-14 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_bouquet_description_alter_bouquetflower_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bouquet',
            name='photo',
            field=models.URLField(blank=True, null=True, verbose_name='Фото'),
        ),
    ]
