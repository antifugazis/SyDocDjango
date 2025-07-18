# Generated by Django 4.2.23 on 2025-07-11 13:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_alter_archivaldocument_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrainingSubject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Training Subject",
                "verbose_name_plural": "Training Subjects",
                "ordering": ["name"],
            },
        ),
    ]
