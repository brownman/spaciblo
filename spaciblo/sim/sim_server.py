#!/usr/bin/python

import sys
import time, datetime
import pprint, traceback
import Queue
import threading

import xml.dom.minidom as minidom
from websocket import WebSocketServer

class WebSocketConnection:
	"""Maintains state and an outgoing event queue for a WebSockets connection"""
	def __init__(self, client_socket, server):
		self.client_socket = client_socket
		self.server = server
		self.user = None
		self.space_id = None
		self.disconnected = False
		
		self.outgoing_events = Queue.Queue(-1)
		self.outgoing_event_thread = threading.Thread(target=self.handle_outgoing)
		self.outgoing_event_thread.setDaemon(True)
		self.outgoing_event_thread.start()

	def handle_outgoing(self):
		"""A loop which handles outgoing events.  Does not return until the connection closes."""
		while not self.disconnected:
			try:
				event = self.outgoing_events.get(block=True, timeout=5)
			except Queue.Empty:
				continue
			self.client_socket.send('\x00')
			self.client_socket.send(dehydrate_to_xml(event))
			self.client_socket.send('\xff')
		print "Exiting outgoing message loop"
		
	def pack_attributes(self, xml_element):
		result = {}
		for key in xml_element.attributes.keys():
			result[key] = xml_element.getAttribute(key)
		return result

	def handle_incoming(self):
		"""A loop which handles incoming messages.  Does not return until the connection closes."""
		import events
		from spaciblo.hydration import dehydrate_to_xml
		from sim.models import Space

		while not self.disconnected:
			incoming_data = self.client_socket.recv(4096)
			if len(incoming_data) == 0: continue
			incoming_data = incoming_data[1:len(incoming_data) - 1] # strip off the wrapper bytes
			#print 'Incoming:', incoming_data
			doc = minidom.parseString(incoming_data)
			event = None
			response_event = None
			for class_object in events.SIM_EVENTS:
				if str(doc.documentElement.tagName) == str(class_object.__name__.lower()):
					event = class_object(self.pack_attributes(doc.documentElement))
					event.hydrate_from_xml(doc)
					break

			if not event:
				print "Could not read an event from the comet data: %s" % data
				continue

			if isinstance(event, events.AuthenticationRequest):
				user = self.user_from_session_key(event.session_id)
				if user.is_authenticated():
					print "Comet authed: %s" % user.username
					self.user = user
					response_event = events.AuthenticationResponse(True, user.username)
				else:
					print "Comet auth failure with session id %s" % event.session_id
					response_event = events.AuthenticationResponse(False)
			elif isinstance(event, events.JoinSpaceRequest):
				if not self.user:
					response_event = events.JoinSpaceResponse(event.space_id)
				else:
					try:
						space = Space.objects.get(pk=event.space_id)
						allow_join, space_member = Space.objects.get_membership(space, self.user)
						response_event = events.JoinSpaceResponse(space.id, allow_join)
						if allow_join:
							self.space_id = space.id
							try:
								scene = self.server.sim_pool.get_simulator(self.space_id).scene
								response_event.scene_doc = dehydrate_to_xml(scene)
							except:
								print "Could not log in: %s" % pprint.pformat(traceback.format_exc())
						if space_member:
							response_event.is_member = True
							response_event.is_admin = space_member.is_admin
							response_event.is_editor = space_member.is_editor
					except:
						response_event = events.JoinSpaceResponse(event.space_id)
			elif self.space_id:
				simulator = self.server.sim_pool.get_simulator(self.space_id)
				if simulator:
					event.connection = self
					simulator.event_queue.put(event)
				else:
					print "Got event for absent simulator %s" % event
			else:
				print "Got unhandled event %s" % event

			if response_event:
				#print 'Outgoing: ', dehydrate_to_xml(response_event)
				self.client_socket.send('\x00')
				self.client_socket.send(dehydrate_to_xml(response_event))
				self.client_socket.send('\xff')

	def user_from_session_key(self, session_key):
		from django.conf import settings
		from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
		from django.contrib.auth.models import AnonymousUser
		from django.contrib.sessions.models import Session

		session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
		session_wrapper = session_engine.SessionStore(session_key)
		user_id = session_wrapper.get(SESSION_KEY)
		if user_id == None: return AnonymousUser()
		backend = session_wrapper.get(BACKEND_SESSION_KEY)
		if backend == None: session_wrapper.get(BACKEND_SESSION_KEY)
		auth_backend = load_backend(backend)
		if auth_backend == None: return AnonymousUser()	
		return auth_backend.get_user(user_id)
			
				
	def finish(self):
		self.disconnected = True
		print self.request, 'disconnected!'
		self.server.connections.remove(self)
		# alert the space (if any) that this user has exited only if there are no other connections for that user and space
		if self.space_id is None: return
		for connection in self.server.connections:
			if self.user == connection.user and self.space_id == connection.space_id: return
		sim = self.server.sim_pool.get_simulator(self.space_id)
		if sim is not None: sim.event_queue.put(events.UserExited(self.space_id, self.user.username))
	def __unicode__(self):
		return "CometConnection: %s user: %s space: %s" % (self.client_address, self.user, self.space_id)	

class SimulationServer:
	def __init__(self):
		self.ws_server = WebSocketServer(self.ws_callback, port=settings.WEB_SOCKETS_PORT)
		import sim.sim_pool
		self.sim_pool = sim.sim_pool.SimulatorPool(self)
	
	def start(self):
		self.sim_pool.start_all_spaces()
		self.ws_server.start()

	def send_space_event(self, space_id, event):
		pass

	def ws_callback(self, client_socket):
		ws_connection = WebSocketConnection(client_socket, self)
		ws_connection.handle_incoming()
		
	def cleanup(self):
		pass

def main():
	try:
		sim_server = SimulationServer()
		sim_server.start()
	except:
		print 'Could not start the simulation server'
		traceback.print_exc() 
		sys.exit()
		
	try:
		while True: time.sleep(100)
	except (KeyboardInterrupt, SystemExit):
		sim_server.cleanup()
		sys.exit()

if __name__ == '__main__':
	from django.core.management import setup_environ
	import settings
	setup_environ(settings)
	import sim.sim_pool
	from django.contrib.sessions.backends.db import SessionStore
	from django.contrib.auth.models import User
	main()

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
