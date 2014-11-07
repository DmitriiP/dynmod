import json
from django.apps import apps
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from dynmod.models import DYNAMIC_FIELD_TYPES


@require_http_methods(['GET'])
def get_models(request):
    models = [(x, y._meta.verbose_name.title(),)
              for x, y in apps.all_models['dynmod'].iteritems()]
    return HttpResponse(json.dumps(models))


@require_http_methods(['GET'])
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


@require_http_methods(['GET'])
def model_objects(request, model_name):
    mdl = apps.all_models['dynmod'][model_name]
    data = serializers.serialize('json', mdl.objects.all())
    return HttpResponse(data)


@require_http_methods(['PUT'])
def update_object(request):
    put = request.body
    try:
        put = json.loads(put)
    except:
        return HttpResponse('{"error": "Incorrect request format"}', status=400)

    model_name = put.get('model_name', None)
    if model_name is None or model_name not in apps.all_models['dynmod']:
        return HttpResponse('{"error": "Missing model name, or it is incorrect."}', status=400)
    mdl = apps.all_models['dynmod'][model_name]
    field = put.get('field', None)
    if field is None or field not in mdl._meta.get_all_field_names():
        return HttpResponse('{"error": "Missing field name, or it is incorrect."}', status=400)
    obj_id = int(put.get('id', '0'))
    if obj_id == 0 or not mdl.objects.filter(id=obj_id).exists():
        return HttpResponse('{"error": "Missing object id, or it is incorrect."}', status=400)
    obj = mdl.objects.get(id=obj_id)
    value = put.get('value', None)
    try:
        setattr(obj, field, value)
        obj.save()
    except (ValidationError, ValueError):
        return HttpResponse('{"error": "Value didn\'t pass validation."}', status=400)
    return HttpResponse('{"msg": "ok"}')


def is_field_valid(field_type, value):
    try:
        field = DYNAMIC_FIELD_TYPES[field_type]
        field().to_python(value)
    except (ValidationError, ValueError):
        return False
    return True


@require_http_methods(['POST'])
def validate(request):
    try:
        field_type = request.POST['type']
        value = request.POST['value']
        if not is_field_valid(field_type, value):
            return HttpResponse('{"result": 1}')
    except KeyError:
        return HttpResponse('{"result": 1}')
    return HttpResponse('{"result": 0}')


@require_http_methods(['POST'])
def add_object(request):
    data = request.body
    try:
        data = json.loads(data)
    except:
        return HttpResponse('{"error": "Incorrect request format"}', status=400)
    model_name = data.get('model', None)
    if model_name is None or model_name not in apps.all_models['dynmod']:
        return HttpResponse('{"error": "Missing model name, or it is incorrect."}', status=400)
    mdl = apps.all_models['dynmod'][model_name]
    fields = {}
    for field in data['fields']:
        if is_field_valid(field['type'], field['value']):
            fields[field['id']] = field['value']
    if len(fields) != len(data['fields']):
        return HttpResponse('{"error": "Some fields didn\'t pass validation."}', status=400)
    try:
        mdl(**fields).save()
    except (TypeError, ValueError):
        return HttpResponse('{"error": "Incorrect field values"}', status=400)
    return HttpResponse('{"msg": "ok"}', status=201)
