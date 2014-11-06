import json
from django.db import models, migrations
from django.contrib import admin


DYNAMIC_FIELD_TYPES = {
    'char': models.CharField,
    'int': models.IntegerField,
    'date': models.DateField,
    'id': models.AutoField,
}


def model_factory(name, title, fields):
    fields_dict = {}
    for field in fields:
        field_type = DYNAMIC_FIELD_TYPES[field['type']]
        if 'title' not in field:
            field['title'] = field['id'].title()
        if 'kwargs' not in field:
            field['kwargs'] = {}
            if field['type'] == 'char':
                field['kwargs']['max_length'] = 255
                field['kwargs']['blank'] = True
            if field['type'] in ['int', 'date']:
                field['kwargs']['null'] = True
        fields_dict[field['id']] = field_type(field['title'], **field['kwargs'])
    fields = [(x, y,) for x, y in fields_dict.iteritems()]

    fields_dict['__module__'] = 'dynmod.models'
    new_model = type(str(name), (models.Model,), fields_dict)
    new_model._meta.verbose_name = title
    new_model_admin = type(str(name) + 'Admin', (admin.ModelAdmin,), {})
    admin.site.register(new_model, new_model_admin)

example = json.load(open('dynmod/models.json','r'))
for ex in example:
    model_factory(ex['id'], ex['title'], ex['fields'])
