from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_book_price'), # Change to the last known good migration
        # ... keep any other valid dependencies if they exist
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Prix (Gourdes)'),
        ),
    ]
