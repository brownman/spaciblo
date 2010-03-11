import time
import pprint
import simplejson
import datetime

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import mail

from sim.sim_server import *
from sim.websocket import *

import spaciblo.settings as settings

class SimTest(TestCase):
	def setUp(self):
		#self.sim_server = SimulationServer()
		#self.sim_server.start()
		pass

	def tearDown(self):
		#self.sim_server.stop()
		pass

	def test_sim_setup(self):
		pass
# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
