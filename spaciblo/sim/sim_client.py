import Queue
import threading
import random
import datetime

from django.contrib.sessions.models import Session
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, authenticate
import django.contrib.sessions.backends.db as session_engine

from websocket import WebSocketClient
import events

class SimClient:
	def __init__(self, session_key, ws_host, ws_port, ws_origin):
		self.session_key = session_key
		self.ws_client = WebSocketClient(ws_host, ws_port, ws_origin)
		self.incoming_events = Queue.Queue(-1)

		self.should_run = True
		self.incoming_event_thread = threading.Thread(target=self.incoming_loop)
		self.incoming_event_thread.start()		


	def incoming_loop(self):
		while self.should_run:
			message = self.ws_client.receive()
			if message == None: break
			event = events.parse_event_json(message)
			self.incoming_events.put(event)

	def authenticate(self):
		self.ws_client.send(events.AuthenticationRequest(self.session_key).dehydrate())
	
	def close(self):
		self.should_run = False
		self.ws_client.close()