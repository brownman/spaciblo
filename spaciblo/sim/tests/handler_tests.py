from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase, Client
from django.core.urlresolvers import reverse

import simplejson as json

from sim.handler import *
from sim.models import *

class Thing(object):
	def __init__(self, name=None, rank=None):
		self.name = name
		self.rank = rank
		self.dink = []
	def __repr__(self): return 'Thing: %s' % self.name
	
class HandlerTest(TestCase): 
	"""A test suite for the piston handlers"""

	fixtures = ['auth.json', 'sites.json']

	def setUp(self):
		pass

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
