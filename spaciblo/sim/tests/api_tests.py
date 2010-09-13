from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase, Client
from django.core.urlresolvers import reverse

import simplejson as json

from sim.handler import *
from sim.models import *
from sim.management.commands.load_example_spaces import Command

class Thing(object):
	def __init__(self, name=None, rank=None):
		self.name = name
		self.rank = rank
		self.dink = []
	def __repr__(self): return 'Thing: %s' % self.name
	
class APITest(TestCase): 
	"""A test suite for the web API"""

	fixtures = ['auth.json', 'sites.json']
	root_url = '/api/sim/'
	
	def setUp(self):
		self.client = Client()
		self.command = Command()
		self.command.handle_noargs()

	def tearDown(self):
		pass

	def test_serialization(self):
		t = Thing('Amy', 'Boss Lady')
		t2 = Thing('dwong', 'dwink')
		t.dink.append(t2)
		t.dink.append(User.objects.all())
		t.dink.append({'moo':'cow', 'cheep':'bird'})
		t.dink.append((1, 2, 3, 4))
		
		parsed_obj = json.loads(to_json(t))
		self.assertEqual(len(parsed_obj['dink']), 4)
		self.assertEqual(parsed_obj['dink'][0]['name'], 'dwong')
		self.assertEqual(parsed_obj['dink'][1][0]['username'], 'trevor')
		self.assertFalse(parsed_obj['dink'][1][0].has_key('password')) #make sure that we're respecting handlers

	def test_from_json(self):
		t = Thing('Ronimal', 'Chief')
		json = to_json(t)
		t2 = from_json(Thing(), json)
		self.assertEqual(t2.name, t.name)
		self.assertEqual(t2.rank, t.rank)
		
	def test_web_api(self):
		spaces = Space.objects.all()
		self.assertTrue(len(spaces) > 0)
		
		response = self.client.get(reverse('sim.api_views.scene_document', kwargs={ 'id':spaces[0].id }))
		self.assertEqual(response.status_code, 200)
		parsed_scene = json.loads(response.content)
		
		templates = Template.objects.all()
		self.assertTrue(len(templates) > 0)
		self.assertTrue(len(templates[0].assets.all()) > 0)
		asset = templates[0].assets.all()[0]
		response = self.client.get(reverse('sim.api_views.template_asset', kwargs={'template_id':templates[0].id, 'asset_key':templates[0].get_key(asset)}))
		self.assertEqual(response.status_code, 302) # the template asset view redirects to the static file url
		response = self.client.get(reverse('sim.api_views.template_asset', kwargs={'template_id':templates[0].id, 'asset_key':templates[0].get_key(asset)}), follow=True)
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/api/sim/space/%s' % spaces[0].id, follow=True)
		self.assertEqual(response.status_code, 200)

		self.assertTrue(self.client.login(username='trevor', password='1234'))
		
