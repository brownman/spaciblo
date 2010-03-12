import Queue
import threading
import random
import datetime
import logging
import simplejson

from django.contrib.sessions.models import Session
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, authenticate
import django.contrib.sessions.backends.db as session_engine

from websocket import WebSocketClient
import events
from scene import *

class SimClient:
	def __init__(self, session_key, ws_host, ws_port, ws_origin, event_handler=None):
		self.session_key = session_key
		self.ws_client = WebSocketClient(ws_host, ws_port, ws_origin)
		self.event_handler = event_handler
		self.username = None
		self.space_id = None
		self.scene = None
		
		self.should_run = True
		self.incoming_event_thread = threading.Thread(target=self.incoming_loop)
		self.incoming_event_thread.start()		

	def incoming_loop(self):
		while self.should_run:
			message = self.ws_client.receive()
			if message == None: break
			event = events.parse_event_json(message)
			
			if isinstance(event, events.AuthenticationResponse):
				if event.authenticated:
					self.username = event.username
			elif isinstance(event, events.JoinSpaceResponse):
				if event.joined:
					self.space_id = event.space_id
					self.scene = Scene()
					self.scene.hydrate(simplejson.loads(event.scene_doc))
			elif isinstance(event, events.ThingAdded):
				thing = Thing(event.thing_id, position=Position().hydrate(event.position), orientation=Orientation().hydrate(event.orientation), scale=event.scale)
				thing.parent = self.scene.thing.get_thing(event.parent_id)
				thing.parent.add_thing(thing)
			elif isinstance(event, events.UserExited):
				user_thing = self.scene.get_user_thing(event.username)
				if user_thing: self.scene.thing.remove_thing(user_thing)
			elif isinstance(event, events.ThingMoved):
				thing = self.scene.get_thing(event.thing_id)
				if thing:
					thing.position = Position().hydrate(event.position)
					thing.orientation = Orientation().hydrate(event.orientation)
			else:
				print 'Unhandled incoming space event: %s' % event

			if self.event_handler: self.event_handler(event)

	def authenticate(self):
		self.ws_client.send(events.AuthenticationRequest(self.session_key).dehydrate())

	def join_space(self, space_id):
		self.ws_client.send(events.JoinSpaceRequest(space_id).dehydrate())

	def add_user_thing(self):
		self.ws_client.send(events.AddUserThingRequest(self.space_id, self.username).dehydrate())

	def close(self):
		self.should_run = False
		self.ws_client.close()
