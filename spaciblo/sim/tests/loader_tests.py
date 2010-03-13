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

import spaciblo.settings as settings
from sim.loaders.obj import ObjLoader

class ObjTest(TransactionTestCase): 
	"""A test suite for the loading Obj files."""
	def setUp(self):
		self.testObj1 = open('example/template/moon/Moon.obj').read()

	def tearDown(self):
		pass

	def test_load(self):
		parser = ObjLoader()
		obj = parser.parse(self.testObj1)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
