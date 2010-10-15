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

class AddUserRequest(SimEvent):
	"""A space client may send an AddUserRequest if they require a body in a space."""
	def __init__(self, space_id=None, username=None, position=None, orientation=None):
		if not position: position = [0,0,0]
		if not orientation: orientation = [0,0,0,1]
		self.space_id = space_id
		self.username = username
		self.position = position
		self.orientation = orientation

class UserMoveRequest(SimEvent):
	"""A space client sends this to indicate that the user has requested a motion."""
	def __init__(self, space_id=None, username=None, position=None, orientation=None):
		if not position: position = [0,0,0]
		if not orientation: orientation = [0,0,0,1]
		self.space_id = space_id
		self.username = username
		self.position = position
		self.orientation = orientation

class PlaceableMoved(SimEvent):
	"""The simulator generates these to indicate that a Placeable is in motion."""
	def __init__(self, space_id=None, uid=None, position=None, orientation=None):
		if not position: position = [0,0,0]
		if not orientation: orientation = [0,0,0,1]
		self.space_id = space_id
		self.uid = uid;
		self.position = position
		self.orientation = orientation

class NodeRemoved(SimEvent):
	"""The simulator generates these to indicate that a Node has been destroyed."""
	def __init__(self, space_id=None, uid=None):
		self.space_id = space_id
		self.uid = uid

class NodeAdded(SimEvent):
	"""The simulator generates these to indicate that a Node as been created."""
	def __init__(self, space_id=None, parent_id=None, json_data=None):
		self.space_id = space_id
		self.parent_id = parent_id
		self.json_data = json_data

class UserMessage(SimEvent):
	"""A user generated chat message."""
	def __init__(self, space_id=None, username=None, message=None):
		self.space_id = space_id
		self.username = username
		self.message = message
	def __repr__(self):
		return 'UserMessage: %s, %s, %s' % (self.space_id, self.username, self.message)

class Heartbeat(SimEvent):
	"""A heartbeat event, used to test that the connection is alive and the remote client is not hung."""
	def __init__(self):
		self.time = datetime.datetime.now()

class PoolInfoRequest(SimEvent):
	"""Used to request stats information about the spaces in the pool."""
	pass

class PoolInfo(SimEvent):
	"""Information about the spaces in the pool."""
	def __init__(self, infos=None):
		"""Infos MUST be maps of simple python times"""
		if not infos: infos = []
		self.infos = infos

SIM_EVENTS = [Heartbeat, UserMessage, PlaceableMoved, AuthenticationRequest, AuthenticationResponse, JoinSpaceRequest, JoinSpaceResponse, UserMoveRequest, AddUserRequest, NodeAdded, NodeRemoved, PoolInfoRequest, PoolInfo]

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
