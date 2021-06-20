from django.db.models import Q
from django import template
from django.db.models.functions import Length

register = template.Library()

#
# Tag filters for using it templates
#
