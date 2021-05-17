from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class DatabaseInfo(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50)

    server_ip = models.CharField(max_length=50)
    server_name = models.CharField(max_length=100)
    port_number = models.IntegerField(null=False, default=0)

    db_username = models.CharField(max_length=50)
    db_password = models.CharField(max_length=100)

    config_file_name = models.CharField(max_length=60)
    shell_command = models.TextField(max_length=500)

    created_date = models.DateTimeField(default=timezone.now)
    changed_date = models.DateTimeField(null=True)


class QueryMethod(models.Model):
    parent_db = models.ForeignKey(DatabaseInfo, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    query_text = models.TextField(max_length=500)

    created_date = models.DateTimeField(default=timezone.now)
    changed_date = models.DateTimeField(null=True)
