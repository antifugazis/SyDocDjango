from django.db import models
from django.utils import timezone
from core.models import Member, Book, Loan, DocumentationCenter
from django.contrib.auth.models import User

# Create your models here.

class AgeVerificationFailure(models.Model):
    """
    Model to track loan attempts that were refused due to age restrictions.
    This helps members understand why certain loans were denied and keeps a record
    for administrators.
    """
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        related_name='age_verification_failures',
        verbose_name='Membre'
    )
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name='age_verification_failures',
        verbose_name='Livre/Ouvrage'
    )
    attempted_at = models.DateTimeField(
        default=timezone.now, 
        verbose_name='Date de la tentative'
    )
    member_age = models.PositiveIntegerField(
        verbose_name='Âge du Membre au moment de la tentative'
    )
    required_age = models.PositiveIntegerField(
        verbose_name='Âge minimum requis pour le livre'
    )
    
    class Meta:
        verbose_name = 'Échec de vérification d\'âge'
        verbose_name_plural = 'Échecs de vérification d\'âge'
        ordering = ['-attempted_at']
        unique_together = ['member', 'book', 'attempted_at']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.book.title} (âge {self.member_age}, requis {self.required_age})"
    
    @property
    def is_age_suitable(self):
        """
        Returns True if the member's age is suitable for the book.
        """
        return self.member_age >= self.required_age


class Complaint(models.Model):
    """
    Model to store complaints/help requests from users.
    """
    full_name = models.CharField(
        max_length=255,
        verbose_name='Nom complet'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    phone1 = models.CharField(
        max_length=20,
        verbose_name='Téléphone 1'
    )
    phone2 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Téléphone 2'
    )
    request = models.TextField(
        verbose_name='Requête'
    )
    documentation_center = models.ForeignKey(
        DocumentationCenter,
        on_delete=models.CASCADE,
        related_name='complaints',
        verbose_name='Centre de Documentation'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints',
        verbose_name='Créé par'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date de création'
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Résolu'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de résolution'
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_complaints',
        verbose_name='Résolu par'
    )
    resolution_notes = models.TextField(
        blank=True,
        verbose_name='Notes de résolution'
    )
    
    class Meta:
        verbose_name = 'Doléance'
        verbose_name_plural = 'Doléances'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Doléance de {self.full_name} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def resolve(self, user, notes=''):
        """
        Mark the complaint as resolved.
        """
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()
