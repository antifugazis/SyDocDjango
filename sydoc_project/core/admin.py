# sydoc_project/core/admin.py

from django.contrib import admin
from .models import Department, Arrondissement, Commune, DocumentationCenter, Category, Author, Book, Member, Loan, Role, Staff, TrainingModule, Quiz, StaffTrainingRecord, ArchivalSeries, ArchivalDocument, Notification, DigitalizationRequest
from django.utils.translation import gettext_lazy as _

# Register your models here.
admin.site.register(Department)
admin.site.register(Arrondissement)
admin.site.register(Commune)
admin.site.register(Category)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'date_of_death')
    search_fields = ('first_name', 'last_name')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'documentation_center', 'isbn', 'category', 'is_digital', 'quantity_available', 'total_quantity', 'status', 'acquisition_date')
    list_filter = ('documentation_center', 'category', 'is_digital', 'status', 'acquisition_date')
    search_fields = ('title', 'isbn', 'description')
    raw_id_fields = ('documentation_center',)
    filter_horizontal = ('authors',)
    fieldsets = (
        (_('Informations Générales'), {
            'fields': ('documentation_center', 'title', 'isbn', 'publication_date', 'category', 'authors', 'description')
        }),
        (_('Détails Physiques/Numériques'), {
            'fields': ('is_digital', 'file_upload', 'pages', ('quantity_available', 'total_quantity'), 'cover_image', 'status')
        }),
        (_('Acquisition'), {
            'fields': ('acquisition_date',)
        }),
    )

@admin.register(ArchivalSeries)
class ArchivalSeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'documentation_center', 'creation_date_range', 'is_active')
    list_filter = ('documentation_center', 'is_active')
    search_fields = ('name', 'description')
    raw_id_fields = ('documentation_center',)
    fieldsets = (
        (_('Informations de la Série'), {
            'fields': ('documentation_center', 'name', 'description', 'creation_date_range', 'is_active')
        }),
    )

@admin.register(ArchivalDocument)
class ArchivalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_id', 'documentation_center', 'archival_series', 'is_digital', 'status', 'acquisition_date')
    list_filter = ('documentation_center', 'archival_series', 'is_digital', 'status', 'acquisition_date')
    search_fields = ('title', 'document_id', 'description', 'creator', 'physical_location')
    raw_id_fields = ('documentation_center', 'archival_series')
    fieldsets = (
        (_('Informations Générales'), {
            'fields': ('documentation_center', 'title', 'document_id', 'archival_series', 'description', ('creation_date', 'creator'))
        }),
        (_('Détails Physiques/Numériques'), {
            'fields': ('physical_location', 'is_digital', 'digital_file')
        }),
        (_('Statut & Acquisition'), {
            'fields': ('status', 'acquisition_date')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient_center', 'recipient_staff', 'sender_user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('recipient_center', 'recipient_staff', 'sender_user', 'notification_type', 'is_read', 'created_at')
    search_fields = ('message', 'recipient_center__name', 'recipient_staff__first_name', 'recipient_staff__last_name', 'sender_user__username')
    raw_id_fields = ('recipient_center', 'recipient_staff', 'sender_user')
    fieldsets = (
        (_('Détails de la Notification'), {
            'fields': (('recipient_center', 'recipient_staff'), 'message', ('notification_type', 'is_read'), 'sender_user')
        }),

    )

@admin.register(DocumentationCenter)
class DocumentationCenterAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'department', 'is_blocked', 'is_active',
        'trial_start_date', 'trial_end_date', 'get_remaining_trial_days'
    )
    list_filter = ('is_blocked', 'is_active', 'department', 'creation_date')
    search_fields = ('name', 'email', 'responsible_full_name')
    readonly_fields = ('creation_date',)
    fieldsets = (
        (_('Informations sur le Centre'), {
            'fields': ('name', 'email', ('phone1', 'phone2'), 'full_address', ('department', 'arrondissement', 'commune'))
        }),
        (_('Informations sur le Responsable'), {
            'fields': ('responsible_full_name', ('responsible_phone1', 'responsible_phone2'), 'responsible_address', 'responsible_email')
        }),
        (_('Informations Système & Essai'), {
            'fields': ('creation_date', ('trial_start_date', 'trial_end_date'), 'monthly_fee', 'is_blocked', 'is_active')
        }),
        (_('Quotas de Gestion (Illimité si -1)'), {
            'fields': ('quota_physical_books', 'quota_ebooks', 'quota_trainings', 'quota_archives'),
            'classes': ('collapse',),
        }),
    )

    def get_remaining_trial_days(self, obj):
        return obj.get_remaining_trial_days()
    get_remaining_trial_days.short_description = _("Jours restants d'essai")

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'full_name', 'documentation_center', 'membership_type', 'is_active', 'date_joined')
    list_filter = ('documentation_center', 'membership_type', 'is_active')
    search_fields = ('member_id', 'first_name', 'last_name', 'email', 'phone_number')
    raw_id_fields = ('documentation_center',)
    fieldsets = (
        (_('Informations du Membre'), {
            'fields': ('documentation_center', 'member_id', ('first_name', 'last_name'), ('email', 'phone_number'), 'address')
        }),
        (_('Statut & Adhésion'), {
            'fields': ('membership_type', 'is_active')
        }),
    )

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'loan_date', 'due_date', 'return_date', 'status')
    list_filter = ('status', 'loan_date', 'due_date', 'return_date')
    search_fields = ('book__title', 'member__first_name', 'member__last_name', 'member__member_id')
    raw_id_fields = ('book', 'member')
    autocomplete_fields = ('book', 'member')
    fieldsets = (
        (_('Détails du Prêt'), {
            'fields': ('book', 'member', ('loan_date', 'due_date'), ('return_date', 'status'))
        }),
    )


admin.site.register(Role)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'documentation_center', 'role', 'email', 'is_active', 'date_hired')
    list_filter = ('documentation_center', 'role', 'is_active', 'date_hired')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    raw_id_fields = ('documentation_center',)
    fieldsets = (
        (_('Informations Personnelles'), {
            'fields': ('documentation_center', ('first_name', 'last_name'), 'email', 'phone_number', 'address')
        }),
        (_('Rôle & Statut'), {
            'fields': ('role', 'is_active', 'date_hired')
        }),
    )

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'documentation_center', 'duration_minutes', 'is_active', 'created_at')
    list_filter = ('documentation_center', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('documentation_center',)
    fieldsets = (
        (_('Informations du Module'), {
            'fields': ('documentation_center', 'title', 'description', 'duration_minutes')
        }),
        (_('Statut'), {
            'fields': ('is_active',)
        }),
    )

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'training_module', 'pass_score', 'created_at')
    list_filter = ('training_module', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('training_module',)
    fieldsets = (
        (_('Détails du Quiz'), {
            'fields': ('training_module', 'title', 'description', 'pass_score')
        }),
        
    )

@admin.register(StaffTrainingRecord)
class StaffTrainingRecordAdmin(admin.ModelAdmin):
    list_display = ('staff_member', 'training_module', 'quiz', 'completion_date', 'score', 'passed')
    list_filter = ('staff_member__documentation_center', 'training_module', 'quiz', 'passed', 'completion_date')
    search_fields = ('staff_member__first_name', 'staff_member__last_name', 'training_module__title', 'notes')
    raw_id_fields = ('staff_member', 'training_module', 'quiz')
    fieldsets = (
        (_('Détails de l\'Enregistrement'), {
            'fields': ('staff_member', 'training_module', 'quiz', 'completion_date', 'score', 'passed', 'notes')
        }),
    )

@admin.register(DigitalizationRequest)
class DigitalizationRequestAdmin(admin.ModelAdmin):
    list_display = ('documentation_center', 'content_object', 'status', 'request_date', 'completion_date', 'requested_by_staff')
    list_filter = ('documentation_center', 'status', 'request_date', 'completion_date')
    search_fields = ('documentation_center__name', 'content_object__title', 'notes')
    raw_id_fields = ('documentation_center', 'requested_by_staff')
    fieldsets = (
        (_('Demande de Digitalisation'), {
            'fields': ('documentation_center', 'content_type', 'object_id', 'requested_by_staff', 'request_date')
        }),
        (_('Statut & Détails'), {
            'fields': ('status', 'completion_date', 'digital_file_url', 'notes')
        }),
    )