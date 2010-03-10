from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import mail

import pprint
import simplejson
import datetime

from ground.hydration import *

class DummyDataOne:
	def __init__(self):
		self.simple_string = 'I am a string'
		self.created = datetime.datetime.now()
		self.a_list = ['one', 2, ['I', 'I', 'I']]
		self.children = [DummyDataTwo(), DummyDataTwo()]

	class HydrationMeta:
		attributes = ['simple_string', 'created']
		nodes = ['children']

class DummyDataTwo:
	def __init__(self):
		self.easy_string = "I like strings"
	class HydrationMeta:
		attributes = ['easy_string']

class DummyIDClass:
	def __init__(self):
		self.id = 42

class DummyDataThree:
	def __init__(self, some_value='not passed in'):
		self.some_value = some_value
		self.id_class = DummyIDClass()
		self.another_id_class = DummyIDClass()
	class HydrationMeta:
		attributes = ['some_value']
		ref_attributes = ['id_class', ('another_id_class', 'better_name')]
		element_name = 'fantastico'

class HydrationTest(TestCase):
	def setUp(self):
		self.dd1 = DummyDataOne()
		self.dd3 = DummyDataThree('uno')

	def tearDown(self):
		pass

	def test_api_views(self):
		dd1_json = Hydration.dehydrate(self.dd1)
		dd1_parsed = simplejson.loads(dd1_json)

		self.failUnlessEqual('DummyDataOne', dd1_parsed['type'])
		self.failUnlessEqual(len(self.dd1.children), len(dd1_parsed['children']))
		self.failUnlessEqual(self.dd1.children[1].easy_string, dd1_parsed['children'][1]['attributes']['easy_string'])
		
		dd3_json = Hydration.dehydrate(self.dd3)
		another_dd3 = DummyDataThree()
		Hydration.hydrate(another_dd3, dd3_json)
		self.failUnlessEqual('uno', another_dd3.some_value)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
