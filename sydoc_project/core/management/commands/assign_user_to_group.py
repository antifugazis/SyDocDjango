from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Assign a user to a group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to assign')
        parser.add_argument('group_name', type=str, help='Name of the group to assign the user to')

    def handle(self, *args, **options):
        username = options['username']
        group_name = options['group_name']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return
        
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Group "{group_name}" does not exist')
            )
            return
        
        # Add user to group
        user.groups.add(group)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added user "{username}" to group "{group_name}"')
        )
        
        # Show current groups for the user
        user_groups = list(user.groups.values_list('name', flat=True))
        self.stdout.write(
            f'User "{username}" is now in groups: {user_groups}'
        )
