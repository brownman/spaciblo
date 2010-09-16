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
from sim.models import Space, SpaceMember
from sim.management.commands.load_example_spaces import Command
import spaciblo.settings as settings

class SimTest(TransactionTestCase): 
	"""A test suite for the sim server and client.
	It must be a TransactionalTestCase because we're accessing the db in multiple threads."""
	
	fixtures = ['auth.json', 'sites.json']
	
	def setUp(self):
		self.command = Command()
		self.command.handle_noargs()
		self.client = Client()
		self.client2 = Client()
		self.sim_server = SimulationServer()
		self.sim_server.start()

	def tearDown(self):
		self.sim_server.stop()

	def test_sim_setup(self):
		self.client.login(username='trevor', password='1234')
		self.client2.login(username='sarah', password='1234')

		class EventHandler:
			def __init__(self):
				self.events = Queue.Queue(-1)
			def handle_event(self, event): self.events.put(event)
		event_handler = EventHandler()

		sim_client = SimClient(self.client.session.session_key, '127.0.0.1', self.sim_server.ws_server.port, '127.0.0.1:8000', event_handler=event_handler.handle_event)

		sim_client.authenticate()
		event = event_handler.events.get(True, 10)
		self.failUnless(event.authenticated)
		self.failUnlessEqual('trevor', event.username)
		self.failUnlessEqual('trevor', sim_client.username)

		space = Space.objects.all()[0]
		sim_client.join_space(space.id)
		event = event_handler.events.get(True, 10)
		self.failUnlessEqual(space.id, event.space_id)
		self.failUnless(event.joined)
		self.failUnless(sim_client.scene)
		self.failUnless(len(sim_client.scene.children) > 0)
		
		event_handler2 = EventHandler()
		sim_client2 = SimClient(self.client2.session.session_key, '127.0.0.1', self.sim_server.ws_server.port, '127.0.0.1:8000', event_handler=event_handler2.handle_event)
		sim_client2.authenticate()
		event = event_handler2.events.get(True, 10)
		self.failUnless(event.authenticated)
		
		sim_client2.join_space(space.id)
		event = event_handler2.events.get(True, 10)
		self.failUnless(event.joined == False) # client 2 is not a member yet
		user2 = User.objects.get(username='sarah')
		space_member = SpaceMember.objects.create(space=space, member=user2)
		sim_client2.join_space(space.id)
		event = event_handler2.events.get(True, 10)
		self.failUnless(event.joined == False)
		space_member.is_admin = True
		space_member.save()
		sim_client2.join_space(space.id)
		event = event_handler2.events.get(True, 10)
		self.failUnless(event.joined)
		
		sim_client.add_user()
		event = event_handler.events.get(True, 10)
		print event
		self.failUnless(event.json_data)
		event = event_handler2.events.get(True, 10)
		print event
		self.failUnless(event.json_data)

		sim_client.close()

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
