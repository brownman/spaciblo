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

from sim.sim_server import *
from sim.sim_client import *
from sim.websocket import *

import spaciblo.settings as settings

class SimTest(TransactionTestCase): 
	"""A test suite for the sim server and client.
	It must be a TransactionalTestCase because we're accessing the db in multiple threads."""
	
	fixtures = ['auth.json', 'sites.json']
	
	def setUp(self):
		self.client = Client()
		self.sim_server = SimulationServer()
		self.sim_server.start()

	def tearDown(self):
		self.sim_server.stop()

	def test_sim_setup(self):
		self.client.login(username='trevor', password='1234')

		client = SimClient(self.client.session.session_key, '127.0.0.1', self.sim_server.ws_server.port, '127.0.0.1:8000')
		client.authenticate()
		event = client.incoming_events.get(block=True, timeout=5)
		self.failUnless(event.authenticated)
		self.failUnlessEqual('trevor', event.username)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
