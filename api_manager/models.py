from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


class DatabaseInfo(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=50, unique=True)
    name_fa = models.CharField(max_length=50, unique=True)

    server_ip = models.CharField(max_length=50)
    server_name = models.CharField(max_length=100)
    port_number = models.IntegerField(null=False, default=0)

    db_name = models.CharField(max_length=50)
    db_username = models.CharField(max_length=50)
    db_password = models.CharField(max_length=100)

    config_file_name = models.CharField(max_length=60)
    shell_command = models.TextField(max_length=500)
    status_url = models.CharField(max_length=100)
    docker_id = models.CharField(max_length=128, default="", blank=True)
    health = models.BooleanField(default=False)

    created_date = models.DateTimeField(default=timezone.now)
    changed_date = models.DateTimeField(null=True)


@receiver(post_save, sender=DatabaseInfo)
def make_shell_command(sender, created, instance, **kwargs):
    """
    This function is called after creating a DatabaseInfo object
    and generates a shell command for it. This only happens once
    when the object is created, so if you change other fields manually
    you should change shell command too accordingly
    """
    # Make sure status url starts with '/'
    if not instance.status_url.startswith('/'):
        instance.status_url = '/' + instance.status_url
        instance.save()
    if created:
        name = instance.name_en.replace(' ', '_')
        port = instance.port_number
        config_name = instance.config_file_name.replace(' ', '_')

        # This is a template for the shell command.
        cmd = f"docker run -d --rm -v /tmp/{config_name}:/db/db.json -p {port}:80 --name {name}" \
            " cr.isfahan.ir/ir.isfahan.db2rest:400.1.18"
        instance.shell_command = cmd
        instance.save()


class QueryMethod(models.Model):
    parent_db = models.ForeignKey(DatabaseInfo, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    query_text = models.TextField(max_length=500)

    created_date = models.DateTimeField(default=timezone.now)
    changed_date = models.DateTimeField(null=True)

    class Meta:
        # Database can't have two methods with the same name
        unique_together = (("parent_db", "name"),)
