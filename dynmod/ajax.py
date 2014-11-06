import json
from django.apps import apps
from django.http import HttpResponse
from django.core import serializers
from dynmod.models import DYNAMIC_FIELD_TYPES


def get_models(request):
    models = [(x, y._meta.verbose_name.title(),)
              for x, y in apps.all_models['dynmod'].iteritems()]
    return HttpResponse(json.dumps(models))


def model(request, model_name):
    result = {}
    mdl = apps.all_models['dynmod'][model_name]
    result['name'] = mdl._meta.verbose_name.title()
    result['fields'] = []
    for field in mdl._meta.fields:
        field_dict = {}
        field_dict['id'] = field.attname
        field_dict['title'] = field.verbose_name.title()
        field_dict['type'] = (k for k, v in DYNAMIC_FIELD_TYPES.iteritems()
                              if isinstance(field, v)).next()
        result['fields'].append(field_dict)
    return HttpResponse(json.dumps(result))


def model_objects(request, model_name):
    mdl = apps.all_models['dynmod'][model_name]
    data = serializers.serialize('json', mdl.objects.all())
    return HttpResponse(data)
