from django.core.management.base import BaseCommand
from core.models import Member
from datetime import date

class Command(BaseCommand):
    help = 'Updates members without birthdates to a default value (18 years ago)'

    def handle(self, *args, **options):
        # Default date of birth (18 years ago from today)
        today = date.today()
        default_dob = date(today.year - 18, today.month, today.day)
        
        # Get all members without a date of birth
        members_without_dob = Member.objects.filter(date_of_birth__isnull=True)
        count = members_without_dob.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No members found without date of birth."))
            return
        
        self.stdout.write(f"Found {count} members without date of birth. Updating...")
        
        # Update all members without a date of birth
        for member in members_without_dob:
            member.date_of_birth = default_dob
            member.save()
            self.stdout.write(f"Updated member: {member.first_name} {member.last_name} (ID: {member.id})")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} members with default date of birth: {default_dob}"))
