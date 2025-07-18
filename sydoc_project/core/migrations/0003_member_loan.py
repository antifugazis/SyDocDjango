# Generated by Django 4.2.23 on 2025-06-30 19:54

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_author_category_book"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
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
                (
                    "member_id",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="ID Membre"
                    ),
                ),
                ("first_name", models.CharField(max_length=100, verbose_name="Prénom")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nom")),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name="E-mail"
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Le numéro de téléphone doit être entré au format : '+999999999'. Jusqu'à 15 chiffres autorisés.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                        verbose_name="Téléphone",
                    ),
                ),
                ("address", models.TextField(blank=True, verbose_name="Adresse")),
                (
                    "date_joined",
                    models.DateField(auto_now_add=True, verbose_name="Date d'Adhésion"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                (
                    "membership_type",
                    models.CharField(
                        choices=[
                            ("student", "Étudiant"),
                            ("staff", "Personnel"),
                            ("public", "Public"),
                        ],
                        default="public",
                        max_length=50,
                        verbose_name="Type d'Adhésion",
                    ),
                ),
                (
                    "documentation_center",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="core.documentationcenter",
                        verbose_name="Centre de Documentation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Membre",
                "verbose_name_plural": "Membres",
                "ordering": ["last_name", "first_name"],
                "unique_together": {("documentation_center", "member_id")},
            },
        ),
        migrations.CreateModel(
            name="Loan",
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
                (
                    "loan_date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="Date d'Emprunt"
                    ),
                ),
                ("due_date", models.DateField(verbose_name="Date de Retour Prévue")),
                (
                    "return_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date de Retour Effective"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("borrowed", "Emprunté"),
                            ("returned", "Retourné"),
                            ("overdue", "En Retard"),
                            ("lost", "Perdu"),
                        ],
                        default="borrowed",
                        max_length=50,
                        verbose_name="Statut du Prêt",
                    ),
                ),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loans",
                        to="core.book",
                        verbose_name="Livre/Ouvrage",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loans",
                        to="core.member",
                        verbose_name="Membre Emprunteur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prêt",
                "verbose_name_plural": "Prêts",
                "ordering": ["-loan_date"],
            },
        ),
    ]
