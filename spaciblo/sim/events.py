"""The events used in the simulators.
The hydration code assumes that these event objects have only string attributes and has a no-param __init__.
"""

import datetime
from sim.handler import to_json, from_json
import simplejson

class SimEvent:
	"""The base class which all simulation events extend"""
	def from_json(self, json_string):
		return from_json(self, json_string)
	def to_json(self):
		self.type = self.__class__.__name__
		return to_json(self)
	@classmethod
	def dict(cls):
		return cls().__dict__
	@classmethod
	def event_name(cls):
		return cls.__name__

		
class AuthenticationRequest(SimEvent):
	"""An authentication request from a new WebSocket connection."""
	def __init__(self, session_id=None):
		self.session_id = session_id

class AuthenticationResponse(SimEvent):
	"""An authentication response from the SimServer"""
	def __init__(self, authenticated=False, username=None):
		self.authenticated = authenticated
		self.username = username

class JoinSpaceRequest(SimEvent):
	"""A request from a space client to join a space."""
	def __init__(self, space_id=None):
		self.space_id = space_id

class JoinSpaceResponse(SimEvent):
	"""A response from the SimServer indicating whether a JoinSpaceRequest is successful and what role the client may play (e.g. member, editor, ...)."""
	def __init__(self, space_id=None, joined=False, is_member=False, is_editor=False, is_admin=False, scene_doc=None):
		self.space_id = space_id
		self.joined = joined
		self.is_member = is_member
		self.is_editor = is_editor
		self.is_admin = is_admin
		self.scene_doc = scene_doc

class UserExited(SimEvent):
	"""An event which is generated when a user exists a space."""
	def __init__(self, space_id=None, username=None):
		self.space_id = space_id
		self.username = username

class AddUserThingRequest(SimEvent):
	"""A space client may send an AddUserThingRequest if they require a body in a space."""
	def __init__(self, space_id=None, username=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.username = username
		self.position = position
		self.orientation = orientation

class UserThingMoveRequest(SimEvent):
	"""A space client sends this to indicate that the user has requested a motion."""
	def __init__(self, space_id=None, username=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.username = username
		self.position = position
		self.orientation = orientation

class ThingMoved(SimEvent):
	"""The simulator generates these to indicate that a Thing is in motion."""
	def __init__(self, space_id=None, thing_id=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.thing_id = thing_id;
		self.position = position
		self.orientation = orientation

class ThingRemoved(SimEvent):
	"""The simulator generates these to indicate that a Thing has been destroyed."""
	def __init__(self, space_id=None, thing_id=None):
		self.space_id = space_id
		self.thing_id = thing_id

class ThingAdded(SimEvent):
	"""The simulator generates these to indicate that a Thing as been created."""
	def __init__(self, space_id=None, username=None, thing_id=None, template_id=None, parent_id=None, position="0,0,0", orientation="1,0,0,0", scale=1.0):
		self.space_id = space_id
		self.username = username
		self.thing_id = thing_id
		self.template_id = template_id
		self.parent_id = parent_id
		self.position = position
		self.orientation = orientation
		self.scale = scale

class UserMessage(SimEvent):
	"""A user generated chat message."""
	def __init__(self, space_id=None, username=None, message=None):
		self.space_id = space_id
		self.username = username
		self.message = message

class Heartbeat(SimEvent):
	"""A heartbeat event, used to test that the connection is alive and the remote client is not hung."""
	def __init__(self):
		self.time = datetime.datetime.now()

SIM_EVENTS = [Heartbeat, UserMessage, ThingMoved, AuthenticationRequest, AuthenticationResponse, JoinSpaceRequest, JoinSpaceResponse, UserThingMoveRequest, AddUserThingRequest, ThingAdded, ThingRemoved]

def parse_event_json(json_string):
	json_data = simplejson.loads(json_string)
	for class_object in SIM_EVENTS:
		if json_data['type'] == str(class_object.__name__):
			event = class_object()
			event.from_json(json_string)
			return event
	return None

def smart_str(value, default=None):
	if value is None: return default
	if hasattr(value, '__unicode__'): return value.__unicode__()
	return str(value)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
