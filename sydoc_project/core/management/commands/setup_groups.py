from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Profile

class Command(BaseCommand):
    help = 'Set up user groups with appropriate permissions'

    def handle(self, *args, **options):
        # Define the groups
        groups = [
            'Super Admin',
            'Admin',
            'Documentation Center',
            'Member'
        ]
        
        # Create groups
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created group: {group_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group already exists: {group_name}')
                )
        
        # Assign permissions to groups
        self.assign_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up all user groups')
        )
    
    def assign_permissions(self):
        # Get all groups
        super_admin_group = Group.objects.get(name='Super Admin')
        admin_group = Group.objects.get(name='Admin')
        doc_center_group = Group.objects.get(name='Documentation Center')
        member_group = Group.objects.get(name='Member')
        
        # Super Admin gets all permissions
        all_permissions = Permission.objects.all()
        super_admin_group.permissions.set(all_permissions)
        
        # For other groups, we'll define specific permissions
        # This is a basic setup - you can customize based on your needs
        
        # Admin group gets most permissions but not all
        admin_permissions = Permission.objects.filter(
            content_type__app_label__in=['core', 'center_panel']
        )
        admin_group.permissions.set(admin_permissions)
        
        # Documentation Center group gets permissions related to their work
        doc_center_permissions = Permission.objects.filter(
            content_type__app_label='center_panel',
            content_type__model__in=['book', 'member', 'loan', 'trainingmodule']
        )
        doc_center_group.permissions.set(doc_center_permissions)
        
        # Member group gets minimal permissions
        member_permissions = Permission.objects.filter(
            content_type__app_label='core',
            content_type__model='profile'
        )
        member_group.permissions.set(member_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Assigned permissions to groups')
        )
