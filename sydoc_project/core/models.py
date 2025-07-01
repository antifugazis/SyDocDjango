from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey  
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
# sydoc_project/core/models.py

# Basic Geographical Models
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("Département")
        verbose_name_plural = _("Départements")
        ordering = ['name']

    def __str__(self):
        return self.name

class Arrondissement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='arrondissements')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Arrondissement")
        verbose_name_plural = _("Arrondissements")
        unique_together = ('department', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class Commune(models.Model):
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.CASCADE, related_name='communes')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Commune")
        verbose_name_plural = _("Communes")
        unique_together = ('arrondissement', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.arrondissement.name})"

# Documentation Center Model
class DocumentationCenter(models.Model):
    # Center Information
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nom du Centre"))
    email = models.EmailField(unique=True, verbose_name=_("E-mail du Centre (Officiel)"))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être entré au format : '+999999999'. Jusqu'à 15 chiffres autorisés.")
    )
    phone1 = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name=_("Téléphone 1"))
    phone2 = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name=_("Téléphone 2"))
    full_address = models.TextField(verbose_name=_("Adresse Complète"))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name=_("Département"))
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Arrondissement"))
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Commune"))

    # Responsible Information
    responsible_full_name = models.CharField(max_length=255, verbose_name=_("Nom Complet du Responsable"))
    responsible_phone1 = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name=_("Téléphone Responsable 1"))
    responsible_phone2 = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True, verbose_name=_("Téléphone Responsable 2"))
    responsible_address = models.TextField(verbose_name=_("Adresse du Responsable"))
    responsible_email = models.EmailField(verbose_name=_("E-mail Personnel du Responsable"))

    # System Information / Trial Period
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de Création du Compte"))
    trial_start_date = models.DateField(default=timezone.now, verbose_name=_("Date de Début d'Essai"))
    trial_end_date = models.DateField(verbose_name=_("Date de Fin d'Essai"))
    is_blocked = models.BooleanField(default=False, verbose_name=_("Compte Bloqué"))
    is_active = models.BooleanField(default=True, verbose_name=_("Compte Actif"))
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Montant Mensuel à Payer"))


    # Quotas (for future use, based on documentation)
    quota_physical_books = models.IntegerField(default=-1, verbose_name=_("Quota Livres Physiques (-1 pour illimité)"))
    quota_ebooks = models.IntegerField(default=-1, verbose_name=_("Quota Ebooks (-1 pour illimité)"))
    quota_trainings = models.IntegerField(default=-1, verbose_name=_("Quota Formations (-1 pour illimité)"))
    quota_archives = models.IntegerField(default=-1, verbose_name=_("Quota Archives (-1 pour illimité)"))

    class Meta:
        verbose_name = _("Centre de Documentation")
        verbose_name_plural = _("Centres de Documentation")
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_trial_expired(self):
        """Checks if the trial period has expired."""
        return timezone.now().date() > self.trial_end_date

    def get_remaining_trial_days(self):
        """Returns the number of remaining days in the trial period."""
        if self.is_trial_expired():
            return 0
        remaining_days = (self.trial_end_date - timezone.now().date()).days
        return remaining_days

    def save(self, *args, **kwargs):
        # Example: Automatically block if trial is expired on save (can be managed by a periodic task too)
        if self.pk and self.is_trial_expired() and not self.is_blocked:
            self.is_blocked = True
            print(f"DEBUG: Centre '{self.name}' bloqué car la période d'essai a expiré.") # For debugging
        super().save(*args, **kwargs)



class ArchivalSeries(models.Model):
    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='archival_series', verbose_name='Centre de Documentation')
    name = models.CharField(max_length=255, verbose_name='Nom de la Série Archivistique')
    description = models.TextField(blank=True, verbose_name='Description de la Série')
    creation_date_range = models.CharField(max_length=100, blank=True, verbose_name='Période de Création (ex: 1900-1950)')
    is_active = models.BooleanField(default=True, verbose_name='Série Active')

    class Meta:
        verbose_name = 'Série Archivistique'
        verbose_name_plural = 'Séries Archivilistiques'
        unique_together = ('documentation_center', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.documentation_center.name})"


class ArchivalDocument(models.Model):
    STATUS_CHOICES = [
        ('available', _('Disponible')),
        ('restricted', _('Accès Restreint')),
        ('damaged', _('Endommagé')),
        ('missing', _('Manquant')),
    ]

    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='archival_documents', verbose_name='Centre de Documentation')
    title = models.CharField(max_length=255, verbose_name='Titre du Document')
    archival_series = models.ForeignKey(ArchivalSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name='Série Archivistique')
    document_id = models.CharField(max_length=100, unique=True, verbose_name='Identifiant du Document')
    description = models.TextField(blank=True, verbose_name='Description')
    creation_date = models.DateField(null=True, blank=True, verbose_name='Date de Création du Document')
    creator = models.CharField(max_length=255, blank=True, verbose_name='Créateur(s) / Auteur(s) d\'origine')
    physical_location = models.CharField(max_length=255, blank=True, verbose_name='Emplacement Physique (Cote)')
    is_digital = models.BooleanField(default=False, verbose_name='Version Numérique Disponible')
    digital_file = models.FileField(upload_to='archives/digital/', blank=True, null=True, verbose_name='Fichier Numérique (PDF, Image, etc.)')
    acquisition_date = models.DateField(default=timezone.now, verbose_name='Date d\'Acquisition/Classement')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available', verbose_name='Statut')

    class Meta:
        verbose_name = 'Document Archivistique'
        verbose_name_plural = 'Documents Archivilistiques'
        unique_together = ('documentation_center', 'document_id')
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.document_id})"

    def clean(self):
        if self.is_digital and not self.digital_file:
            raise ValidationError({'digital_file': 'Digital documents must have a file uploaded.'})
        if not self.is_digital and self.digital_file:
            raise ValidationError({'digital_file': 'Physical documents cannot have a digital file.'})



class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom du Rôle')
    description = models.TextField(blank=True, verbose_name='Description du Rôle')

    class Meta:
        verbose_name = 'Rôle'
        verbose_name_plural = 'Rôles'
        ordering = ['name']

    def __str__(self):
        return self.name


class Staff(models.Model):
    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='staff_members', verbose_name='Centre de Documentation')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(unique=True, verbose_name='E-mail Professionnel')
    phone_number = models.CharField(max_length=17, blank=True, null=True, validators=[DocumentationCenter.phone_regex], verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse Personnelle')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name='Rôle')
    date_hired = models.DateField(default=timezone.now, verbose_name='Date d\'Embauche')
    is_active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Membre du Personnel'
        verbose_name_plural = 'Membres du Personnel'
        unique_together = ('documentation_center', 'email')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role if self.role else 'No Role'})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class TrainingModule(models.Model):
    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='training_modules', verbose_name='Centre de Documentation')
    title = models.CharField(max_length=255, verbose_name='Titre du Module')
    description = models.TextField(blank=True, verbose_name='Description')
    duration_minutes = models.IntegerField(null=True, blank=True, verbose_name='Durée (minutes)')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de Création')

    class Meta:
        verbose_name = 'Module de Formation'
        verbose_name_plural = 'Modules de Formation'
        unique_together = ('documentation_center', 'title')
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.documentation_center.name})"


class Quiz(models.Model):
    training_module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='quizzes', verbose_name='Module de Formation Associé')
    title = models.CharField(max_length=255, verbose_name='Titre du Quiz')
    description = models.TextField(blank=True, verbose_name='Description')
    pass_score = models.IntegerField(default=70, verbose_name='Score de Réussite (%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de Création')

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        unique_together = ('training_module', 'title')
        ordering = ['title']

    def __str__(self):
        return f"{self.title} (pour {self.training_module.title})"


class StaffTrainingRecord(models.Model):
    staff_member = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='training_records', verbose_name='Membre du Personnel')
    training_module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='records', verbose_name='Module de Formation')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name='Quiz (optionnel)')
    completion_date = models.DateField(default=timezone.now, verbose_name='Date de Complétion')
    score = models.IntegerField(null=True, blank=True, verbose_name='Score obtenu (%)')
    passed = models.BooleanField(default=False, verbose_name='Réussi')
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'Historique de Formation du Personnel'
        verbose_name_plural = 'Historiques de Formation du Personnel'
        unique_together = ('staff_member', 'training_module', 'completion_date')
        ordering = ['-completion_date']

    def __str__(self):
        return f"{self.staff_member.full_name} - {self.training_module.title} ({'Réussi' if self.passed else 'Échoué'})"

    def clean(self):
        if self.quiz and self.quiz.training_module != self.training_module:
            raise ValidationError({'quiz': 'The selected quiz does not belong to the associated training module.'})
        if self.quiz and self.score is not None:
            self.passed = self.score >= self.quiz.pass_score

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.quiz and self.score is not None:
            self.passed = self.score >= self.quiz.pass_score
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom de la Catégorie')
    description = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    biography = models.TextField(blank=True, verbose_name='Biographie')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date de Naissance')
    date_of_death = models.DateField(null=True, blank=True, verbose_name='Date de Décès')

    class Meta:
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('on_loan', 'En Prêt'),
        ('damaged', 'Endommagé'),
        ('lost', 'Perdu'),
    ]

    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='books', verbose_name='Centre de Documentation')
    title = models.CharField(max_length=255, verbose_name='Titre')
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name='ISBN')
    publication_date = models.DateField(null=True, blank=True, verbose_name='Date de Publication')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Catégorie')
    authors = models.ManyToManyField(Author, related_name='books', verbose_name='Auteurs')
    description = models.TextField(blank=True, verbose_name='Description')
    is_digital = models.BooleanField(default=False, verbose_name='Est Numérique')
    file_upload = models.FileField(upload_to='books/digital/', blank=True, null=True, verbose_name='Fichier Numérique (PDF, EPUB, etc.)')
    pages = models.IntegerField(null=True, blank=True, verbose_name='Nombre de Pages')
    quantity_available = models.IntegerField(default=1, verbose_name='Quantité Disponible (Physique)')
    total_quantity = models.IntegerField(default=1, verbose_name='Quantité Totale (Physique)')
    acquisition_date = models.DateField(default=timezone.now, verbose_name='Date d\'Acquisition')
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True, verbose_name='Image de Couverture')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available', verbose_name='Statut')

    class Meta:
        verbose_name = 'Livre/Ouvrage'
        verbose_name_plural = 'Livres/Ouvrages'
        unique_together = ('documentation_center', 'title', 'publication_date')
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.authors.first().full_name if self.authors.exists() else 'Unknown'}"

    def clean(self):
        if self.is_digital:
            if self.quantity_available != 0 or self.total_quantity != 0:
                raise ValidationError({'is_digital': 'Digital books cannot have physical quantities.'})
            if not self.file_upload:
                raise ValidationError({'file_upload': 'Digital books must have a file uploaded.'})
        else:
            if self.file_upload:
                raise ValidationError({'file_upload': 'Physical books cannot have a file upload.'})
            if self.quantity_available > self.total_quantity:
                raise ValidationError({'quantity_available': 'Quantity available cannot be greater than total quantity.'})

    def is_available_for_loan(self):
        return self.quantity_available > 0 and not self.is_digital and self.status == 'available'

    def loan_book(self):
        if self.is_available_for_loan():
            self.quantity_available -= 1
            self.save()
            return True
        return False

    def return_book(self):
        if not self.is_digital and self.quantity_available < self.total_quantity:
            self.quantity_available += 1
            self.save()
            return True
        return False


class Member(models.Model):
    MEMBERSHIP_CHOICES = [
        ('student', 'Étudiant'),
        ('staff', 'Personnel'),
        ('public', 'Public'),
    ]

    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='members', verbose_name='Centre de Documentation')
    member_id = models.CharField(max_length=50, unique=True, verbose_name='ID Membre')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    phone_number = models.CharField(max_length=17, blank=True, null=True, validators=[DocumentationCenter.phone_regex], verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse')
    date_joined = models.DateField(auto_now_add=True, verbose_name='Date d\'Adhésion')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    membership_type = models.CharField(max_length=50, choices=MEMBERSHIP_CHOICES, default='public', verbose_name='Type d\'Adhésion')

    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
        unique_together = ('documentation_center', 'member_id')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.member_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Emprunté'),
        ('returned', 'Retourné'),
        ('overdue', 'En Retard'),
        ('lost', 'Perdu'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans', verbose_name='Livre/Ouvrage')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans', verbose_name='Membre Emprunteur')
    loan_date = models.DateField(default=timezone.now, verbose_name='Date d\'Emprunt')
    due_date = models.DateField(verbose_name='Date de Retour Prévue')
    return_date = models.DateField(null=True, blank=True, verbose_name='Date de Retour Effective')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='borrowed', verbose_name='Statut du Prêt')

    class Meta:
        verbose_name = 'Prêt'
        verbose_name_plural = 'Prêts'
        ordering = ['-loan_date']

    def __str__(self):
        return f"Prêt de '{self.book.title}' à {self.member.full_name}"

    def clean(self):
        if self.due_date < self.loan_date:
            raise ValidationError({'due_date': 'Due date cannot be earlier than loan date.'})
        if self.return_date and self.return_date < self.loan_date:
            raise ValidationError({'return_date': 'Return date cannot be earlier than loan date.'})

        if self.status in ['returned', 'lost'] and not self.return_date:
            raise ValidationError({'return_date': 'Return date must be set for returned or lost loans.'})
        elif self.status in ['borrowed', 'overdue'] and self.return_date:
            raise ValidationError({'return_date': 'Return date must be null for borrowed or overdue loans.'})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = Loan.objects.get(pk=self.pk).status

        # Handle physical book loan/return
        if not self.book.is_digital:
            if is_new and self.book.is_available_for_loan():
                self.book.loan_book()
            elif self.status == 'returned' and old_status != 'returned':
                self.book.return_book()

        # Handle overdue status
        if self.status == 'borrowed' and timezone.now().date() > self.due_date:
            self.status = 'overdue'

        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', _('Système')),
        ('alert', _('Alerte')),
        ('info', _('Information')),
        ('message', _('Message')),
    ]

    recipient_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, null=True, blank=True, related_name='received_notifications', verbose_name='Centre Destinataire')
    recipient_staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, related_name='received_notifications', verbose_name='Membre du Personnel Destinataire')
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name='Expéditeur (Utilisateur Système)')
    message = models.TextField(verbose_name='Message')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='info', verbose_name='Type de Notification')
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de Création')

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification de {self.sender_user.username if self.sender_user else 'Système'} à {self.recipient_center.name if self.recipient_center else self.recipient_staff.full_name if self.recipient_staff else 'Tous'}"

    def clean(self):
        if not self.recipient_center and not self.recipient_staff:
            raise ValidationError('A notification must be targeted to either a documentation center or a staff member, or both.')


class DigitalizationRequest(models.Model):
    documentation_center = models.ForeignKey(DocumentationCenter, on_delete=models.CASCADE, related_name='digitalization_requests', verbose_name='Centre de Documentation')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Type de Contenu')
    object_id = models.PositiveIntegerField(verbose_name='ID de l\'Objet')
    content_object = GenericForeignKey('content_type', 'object_id')
    requested_by_staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Demandé par le personnel')
    request_date = models.DateField(default=timezone.now, verbose_name='Date de Demande')
    status = models.CharField(max_length=50, choices=[
        ('pending', _('En attente')),
        ('in_progress', _('En cours')),
        ('quality_check', _('Contrôle qualité')),
        ('completed', _('Terminé')),
        ('failed', _('Échoué')),
        ('cancelled', _('Annulé'))
    ], default='pending', verbose_name='Statut de la Digitalisation')
    notes = models.TextField(blank=True, verbose_name='Notes')
    completion_date = models.DateField(null=True, blank=True, verbose_name='Date de Complétion')
    digital_file_url = models.URLField(max_length=500, blank=True, verbose_name='URL du Fichier Numérique Final')

    class Meta:
        verbose_name = 'Demande de Digitalisation (Nubo)'
        verbose_name_plural = 'Demandes de Digitalisation (Nubo)'
        ordering = ['-request_date', 'status']

    def __str__(self):
        return f"Digitalisation de '{self.content_object.title if self.content_object and hasattr(self.content_object, 'title') else 'Unknown Item'}' ({self.status}) pour {self.documentation_center.name}"

    def clean(self):
        if not self.content_object:
            raise ValidationError('A content object (Book or ArchivalDocument) must be specified.')
        if not isinstance(self.content_object, (Book, ArchivalDocument)):
            raise ValidationError('The content object must be either a Book or an ArchivalDocument.')

        if self.status in ['completed', 'failed', 'cancelled'] and not self.completion_date:
            self.completion_date = timezone.now().date()

        if self.status == 'completed' and not self.digital_file_url:
            raise ValidationError({'digital_file_url': 'Digital file URL is required for completed digitalization requests.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)