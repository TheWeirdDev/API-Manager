from django.db.models import Q
from django import template
from django.db.models.functions import Length

register = template.Library()

#
# Tag filters for using it templates
#


@register.filter
def count_running(things):
    return things.annotate(text_len=Length('docker_id')).filter(Q(text_len__gt=0)).count()


@register.filter
def count_stopped(things):
    return things.filter(Q(docker_id="") | Q(docker_id=None)).count()
