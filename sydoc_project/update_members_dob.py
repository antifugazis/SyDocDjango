import os
import sys
import django
from datetime import date

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sydoc_project.settings')
django.setup()

from core.models import Member

def update_members_without_dob():
    """
    Update all members without a date of birth to a default value.
    This is a temporary fix to allow loan creation to work.
    """
    # Default date of birth (18 years ago from today)
    today = date.today()
    default_dob = date(today.year - 18, today.month, today.day)
    
    # Get all members without a date of birth
    members_without_dob = Member.objects.filter(date_of_birth__isnull=True)
    count = members_without_dob.count()
    
    if count == 0:
        print("No members found without date of birth.")
        return
    
    print(f"Found {count} members without date of birth. Updating...")
    
    # Update all members without a date of birth
    for member in members_without_dob:
        member.date_of_birth = default_dob
        member.save()
        print(f"Updated member: {member.first_name} {member.last_name} (ID: {member.id})")
    
    print(f"Successfully updated {count} members with default date of birth: {default_dob}")

if __name__ == "__main__":
    update_members_without_dob()
