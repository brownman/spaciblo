import time
import pprint
import simplejson
import datetime

from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import Client
from django.contrib.sessions.models import Session

from sim.glge import Scene
from sim.handler import to_json

class SceneTest(TransactionTestCase): 
	"""A test suite for dehydrating the glge scene"""

	def setUp(self):
		pass
	def tearDown(self):
		pass

	def test_serialization(self):
		print 'running'
		scene = Scene()
		scene_json = to_json(scene)
		print scene_json

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
