from django.db.models import Q
from django import template

register = template.Library()


@register.filter
def count_running(things):
    return things.filter(~Q(docker_id="")).count()


@register.filter
def count_stopped(things):
    return things.filter(Q(docker_id="") | Q(docker_id=None)).count()


@register.simple_tag
def define(val=None):
    return val
