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
from glge import Scene, Group, Object

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
					self.scene = Scene().populate(simplejson.loads(event.scene_doc))
			elif isinstance(event, events.NodeAdded):
				json = simplejson.loads(event.json_data)
				if 'children' in json:
					node = Group().populate(json)
				else:
					node = Object().populate(json)
				parent = self.scene.get_node(event.parent_id)
				parent.children.append(node)
			elif isinstance(event, events.UserExited):
				user_node = self.scene.get_user(event.username)
				if user_node: self.scene.remove_node(user_node)
			elif isinstance(event, events.PlaceableMoved):
				node = self.scene.get_node(event.uid)
				if node:
					print 'should set the new node position'
					#thing.position = Position().hydrate(event.position)
					#thing.orientation = Orientation().hydrate(event.orientation)
			else:
				print 'Unhandled incoming space event: %s' % event

			if self.event_handler: self.event_handler(event)

	def authenticate(self):
		self.ws_client.send(events.AuthenticationRequest(self.session_key).to_json())

	def join_space(self, space_id):
		self.ws_client.send(events.JoinSpaceRequest(space_id).to_json())

	def add_user(self):
		self.ws_client.send(events.AddUserRequest(self.space_id, self.username).to_json())

	def close(self):
		self.should_run = False
		self.ws_client.close()
