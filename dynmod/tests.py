import json
from django.test import TestCase, Client
from django.apps import apps


class AjaxGetModels(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_allowed(self):
        result = self.client.get('/ajax/get_models/')
        self.assertEqual(result.status_code, 200)

    def test_post_not_allowed(self):
        result = self.client.post('/ajax/get_models/')
        self.assertEqual(result.status_code, 405)

    def test_json_returned(self):
        result = self.client.get('/ajax/get_models/')
        try:
            json.loads(result.content)
        except ValueError:
            self.fail('Not json returned')

    def test_json_is_list(self):
        result = self.client.get('/ajax/get_models/')
        x = json.loads(result.content)
        self.assertTrue(isinstance(x, list))

    def test_json_correct_structure(self):
        result = self.client.get('/ajax/get_models/')
        def is_correct(elem):
            if len(elem) != 2:
                return False
            if isinstance(elem[0], str):
                return False
            if isinstance(elem[1], str):
                return False
            return True
        x = json.loads(result.content)
        self.assertNotIn(False, [is_correct(a) for a in x])


class AjaxUpdateObject(TestCase):
    def setUp(self):
        self.client = Client()
        self.model_names = apps.all_models['dynmod'].keys()
        mdl = apps.all_models['dynmod'][self.model_names[0]]
        x = mdl(not_a_name="x", value=12, start_date="2013-12-12", end_date="2014-12-12")
        x.save()

    def test_get_not_allowed(self):
        result = self.client.get('/ajax/update_object/')
        self.assertEqual(result.status_code, 405)

    def test_post_not_allowed(self):
        result = self.client.post('/ajax/update_object/')
        self.assertEqual(result.status_code, 405)

    def test_put_allowed(self):
        result = self.client.put('/ajax/update_object/', '{"value":"1616","id":"1","field":"value","model_name":"table"}')
        self.assertEqual(result.status_code, 200)

    def test_empty_body(self):
        result = self.client.put('/ajax/update_object/')
        self.assertEqual(result.status_code, 400)

    def test_incorrect_value(self):
        result = self.client.put('/ajax/update_object/', '{"value":"alpha","id":"1","field":"value","model_name":"table"}')
        self.assertEqual(result.status_code, 400)

    def test_not_existing_model(self):
        result = self.client.put('/ajax/update_object/', '{"value":"1616","id":"1","field":"value","model_name":"awesome_but_not_existing"}')
        self.assertEqual(result.status_code, 400)

    def test_not_existing_field(self):
        result = self.client.put('/ajax/update_object/', '{"value":"1616","id":"1","field":"value_nope","model_name":"table"}')
        self.assertEqual(result.status_code, 400)

    def test_not_existing_object(self):
        result = self.client.put('/ajax/update_object/', '{"value":"1616","id":"333","field":"value","model_name":"table"}')
        self.assertEqual(result.status_code, 400)

    def test_incorrect_date(self):
        result = self.client.put('/ajax/update_object/', '{"value":"161612122","id":"1","field":"start_date","model_name":"table"}')
        self.assertEqual(result.status_code, 400)


class AjaxAddObject(TestCase):
    def setUp(self):
        self.client = Client()
        self.model_names = apps.all_models['dynmod'].keys()
        mdl = apps.all_models['dynmod'][self.model_names[0]]
        x = mdl(not_a_name="x", value=12, start_date="2013-12-12", end_date="2014-12-12")
        x.save()

    def test_get_not_allowed(self):
        result = self.client.get('/ajax/update_object/')
        self.assertEqual(result.status_code, 405)

    def test_post_allowed(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"12","type":"int","id":"value"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 201)

    def test_following_standards(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"12","type":"int","id":"value"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertNotEqual(result.status_code, 200)

    def test_not_existing_model(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"12","type":"int","id":"value"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"ni"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)

    def test_empty_body(self):
        data = ''
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)

    def test_not_relevant(self):
        data = 'gimme a pizza'
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)

    def test_missing_field(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 201)

    def test_not_relevant_field(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"12","type":"int","id":"value"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-30","type":"date","id":"middle_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)

    def test_incorrect_value(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"puppet","type":"int","id":"value"},
                {"value":"2014-11-30","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)

    def test_incorrect_date(self):
        data = {
            "fields": [
                {"value":"a","type":"char","id":"not_a_name"},
                {"value":"123","type":"int","id":"value"},
                {"value":"cthulhu","type":"date","id":"start_date"},
                {"value":"2014-11-18","type":"date","id":"end_date"}
            ],
            "model":"table"
        }
        data = json.dumps(data)
        result = self.client.post('/ajax/add_object/', content_type='application/json', data=data)
        self.assertEqual(result.status_code, 400)
