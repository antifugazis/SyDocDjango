from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0040_alter_activityassignment_assigned_by_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityGroupAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_assignments', to='core.activity')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_activity_groups', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_assignments', to='auth.group', verbose_name='Groupe')),
            ],
            options={
                'verbose_name': 'Affectation de Groupe à une Activité',
                'verbose_name_plural': 'Affectations de Groupes aux Activités',
                'ordering': ['-assigned_at'],
                'unique_together': {('activity', 'group')},
            },
        ),
    ]
