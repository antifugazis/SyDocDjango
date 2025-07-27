import os
import stat
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup media directories with correct permissions'

    def handle(self, *args, **options):
        # Create media root directory if it doesn't exist
        media_dirs = [
            settings.MEDIA_ROOT,
            os.path.join(settings.MEDIA_ROOT, 'books'),
            os.path.join(settings.MEDIA_ROOT, 'books', 'covers'),
            os.path.join(settings.MEDIA_ROOT, 'books', 'digital'),
        ]
        
        for directory in media_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                # Set permissions to 755 (rwxr-xr-x)
                os.chmod(directory, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                self.stdout.write(self.style.SUCCESS(f'Created directory: {directory}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating {directory}: {e}'))
        
        # Create a test file to verify permissions
        test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('Test file for permissions')
            self.stdout.write(self.style.SUCCESS(f'Created test file: {test_file}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating test file: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Media directory setup complete!'))
