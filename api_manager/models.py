from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


class CommandTemplate(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    template_text = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class DatabaseInfo(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=50, unique=True)
    name_fa = models.CharField(max_length=50, unique=True)

    server_ip = models.CharField(max_length=50)
    server_name = models.CharField(max_length=100)
    server_port = models.IntegerField(null=False, default=0)

    db_name = models.CharField(max_length=50)
    db_username = models.CharField(max_length=50)
    db_password = models.CharField(max_length=100)
    db_server = models.CharField(max_length=50)

    config_file_name = models.CharField(max_length=60)
    shell_command = models.TextField(max_length=500)
    template = models.ForeignKey(
        CommandTemplate, on_delete=models.SET_NULL, null=True)
    status_url = models.CharField(max_length=100, default="/")
    swagger_url = models.CharField(max_length=100, default="")

    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # A server can't have two APIs on the same port
        unique_together = (("server_ip", "server_port"),)


@receiver(pre_save, sender=DatabaseInfo)
def make_shell_command(sender, instance, **kwargs):
    """
    This function is called after creating a DatabaseInfo object
    and generates a shell command for it. This only happens once
    when the object is created, so if you change other fields manually
    you should change shell command too accordingly
    """
    # Make sure urls start with '/'
    if not instance.status_url.startswith('/'):
        instance.status_url = '/' + instance.status_url
    if not instance.swagger_url.startswith('/'):
        instance.swagger_url = '/' + instance.swagger_url

    name = instance.server_name.replace(' ', '_')
    port = instance.server_port
    config_name = instance.config_file_name.replace(' ', '_')

    template = instance.template.template_text
    template = template.replace('%port', str(port))
    template = template.replace('%name', name)
    template = template.replace('%config_path', config_name)

    instance.shell_command = template


class QueryMethod(models.Model):
    parent_db = models.ForeignKey(DatabaseInfo, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    query_text = models.TextField(max_length=500)

    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # Database can't have two methods with the same name
        unique_together = (("parent_db", "name"),)
