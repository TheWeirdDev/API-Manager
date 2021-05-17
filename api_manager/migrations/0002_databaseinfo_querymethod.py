# Generated by Django 3.2.2 on 2021-05-12 08:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(max_length=50)),
                ('name_fa', models.CharField(max_length=50)),
                ('server_ip', models.CharField(max_length=50)),
                ('server_name', models.CharField(max_length=100)),
                ('port_number', models.IntegerField(default=0)),
                ('db_username', models.CharField(max_length=50)),
                ('db_password', models.CharField(max_length=100)),
                ('config_file_name', models.CharField(max_length=60)),
                ('shell_command', models.TextField(max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('changed_date', models.DateTimeField(null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QueryMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('query_text', models.TextField(max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('changed_date', models.DateTimeField(null=True)),
                ('parent_db', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_manager.databaseinfo')),
            ],
        ),
    ]