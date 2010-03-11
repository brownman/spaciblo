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

def echo_handler(client_socket):
	while True:
		message = []
		while True:
			data = client_socket.recv(4096)
			if not data: break
			message.append(data)
			if data.endswith('\xff'): break
		if len(message) == 0: return None
		joined = ''.join(message)
		final = joined[1:len(joined) - 1]
		client_socket.send('\x00')
		client_socket.send(final)
		client_socket.send('\xff')

class WebSocketTest(TestCase):
	def setUp(self):
		self.echo_server = WebSocketServer(echo_handler, 9990)
		self.echo_server.start()

	def tearDown(self):
		self.echo_server.stop()

	def test_sim_setup(self):
		client = WebSocketClient('127.0.0.1', self.echo_server.port, '127.0.0.1:8000')
		self.failUnlessEqual('WebSocket', client.response_headers['Upgrade'])
		message = 'I hope this works'
		client.send(message)
		self.failUnlessEqual(message, client.receive())
		message = 'Does it work twice?'
		client.send(message)
		self.failUnlessEqual(message, client.receive())
		client2 = WebSocketClient('127.0.0.1', self.echo_server.port, '127.0.0.1:8000')
		self.failUnlessEqual('WebSocket', client2.response_headers['Upgrade'])
		message = 'I hope this works'
		client2.send(message)
		self.failUnlessEqual(message, client2.receive())
		message = 'Does this still work twice?'
		client.send(message)
		self.failUnlessEqual(message, client.receive())
		client.close()
		message = 'Perhaps it works after the first has closed?'
		client2.send(message)
		self.failUnlessEqual(message, client2.receive())
		client2.close()

"""
GET / HTTP/1.1
Upgrade: WebSocket
Connection: Upgrade
Host: 127.0.0.1:9990
Origin: 127.0.0.1:8000


HTTP/1.1 101 Web Socket Protocol Handshake
Upgrade: WebSocket
Connection: Upgrade
WebSocket-Origin: 127.0.0.1:8000
WebSocket-Location: ws://127.0.0.1:9990/
WebSocket-Protocol: 9990


"""

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
