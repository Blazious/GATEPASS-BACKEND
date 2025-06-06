# Generated by Django 5.2.1 on 2025-05-29 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GatepassRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
                ('exit_time', models.DateTimeField()),
                ('return_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending_department', 'Pending Department Approval'), ('approved_department', 'Approved by Department'), ('rejected_department', 'Rejected by Department'), ('pending_security', 'Pending Security Approval'), ('approved_security', 'Approved by Security'), ('rejected_security', 'Rejected by Security')], default='pending_department', max_length=30)),
                ('department_approval_date', models.DateTimeField(blank=True, null=True)),
                ('security_approval_date', models.DateTimeField(blank=True, null=True)),
                ('comments', models.TextField(blank=True)),
            ],
        ),
    ]
