import datetime
import xml.dom.minidom as minidom

"""The hydration code assumes that these event objects have only string attributes and has a no-param __init__."""

class SimEvent:
	def hydrate_from_xml(self, doc):
		"""This default implementation assumes that the event has only string attributes."""
		meta = self.HydrationMeta
		if hasattr(meta, 'attributes'): self.set_string_attributes(getattr(meta, 'attributes'), doc)
		return self
	def set_string_attributes(self, attribute_names, doc):
		"""Take all of the named attributes and assign them to self's similarly named attributes."""
		for attribute_name in attribute_names:
			setattr(self, attribute_name, smart_str(doc.documentElement.getAttribute(attribute_name)))
	def event_name(cls):
		return cls.__name__
	event_name = classmethod(event_name)
	def tag_name(cls):
		return cls.__name__.lower()
	tag_name = classmethod(tag_name)
		
class AuthenticationRequest(SimEvent):
	def __init__(self, session_id=None):
		self.session_id = session_id
	class HydrationMeta:
		attributes = ['session_id']

class AuthenticationResponse(SimEvent):
	def __init__(self, authenticated=False, username=None):
		self.authenticated = smart_str(authenticated)
		self.username = username
	class HydrationMeta:
		attributes = ['authenticated', 'username']

class JoinSpaceRequest(SimEvent):
	def __init__(self, space_id=None):
		self.space_id = space_id
	class HydrationMeta:
		attributes = ['space_id', ]

class JoinSpaceResponse(SimEvent):
	def __init__(self, space_id=None, joined=False, is_member=False, is_editor=False, is_admin=False, scene_doc=None):
		self.space_id = space_id
		self.joined = joined
		self.is_member = is_member
		self.is_editor = is_editor
		self.is_admin = is_admin
		self.scene_doc = scene_doc
	class HydrationMeta:
		attributes = ['space_id', 'joined', 'is_member', 'is_admin', 'is_editor', 'scene_doc']

class UserExited(SimEvent):
	def __init__(self, space_id=None, username=None):
		self.space_id = space_id
		self.username = username
	class HydrationMeta:
		attributes = ['space_id', 'username']

class AddAvatarRequest(SimEvent):
	def __init__(self, space_id=None, username=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.username = username
		self.position = position
		self.orientation = orientation
	class HydrationMeta:
		attributes = ['space_id', 'username', 'position', 'orientation']

class AvatarMoveRequest(SimEvent):
	def __init__(self, space_id=None, username=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.username = username
		self.position = smart_str(position)
		self.orientation = smart_str(orientation)
	class HydrationMeta:
		attributes = ['space_id', 'username', 'position', 'orientation']

class ThingMoved(SimEvent):
	def __init__(self, space_id=None, thing_id=None, position="0,0,0", orientation="1,0,0,0"):
		self.space_id = space_id
		self.thing_id = thing_id;
		self.position = smart_str(position)
		self.orientation = smart_str(orientation)
	class HydrationMeta:
		attributes = ['space_id', 'thing_id', 'position', 'orientation']

class ThingRemoved(SimEvent):
	def __init__(self, space_id, thing_id):
		self.space_id = space_id
		self.thing_id = thing_id
	class HydrationMeta:
		attributes = ['space_id', 'thing_id']

class ThingAdded(SimEvent):
	def __init__(self, space_id, username, thing_id, parent_id, position="0,0,0", orientation="1,0,0,0", scale=1.0):
		self.space_id = space_id
		self.username = username
		self.thing_id = thing_id
		self.parent_id = parent_id
		self.position = smart_str(position)
		self.orientation = smart_str(orientation)
		self.scale = scale
	class HydrationMeta:
		attributes = ['space_id', 'username', 'thing_id', 'parent_id', 'position', 'orientation', 'scale']

class UserMessage(SimEvent):
	def __init__(self, space_id=None, username=None, message=None):
		self.space_id = space_id
		self.username = username
		self.message = message
	class HydrationMeta:
		attributes = ['space_id', 'username', 'message']

class Heartbeat(SimEvent):
	def __init__(self):
		self.time = datetime.datetime.now()
	class HydrationMeta:
		attributes = ['time']

SIM_EVENTS = [Heartbeat, UserMessage, ThingMoved, AuthenticationRequest, AuthenticationResponse, JoinSpaceRequest, JoinSpaceResponse, AvatarMoveRequest, AddAvatarRequest, ThingAdded, ThingRemoved]

def smart_str(value, default=None):
	if value is None: return default
	if hasattr(value, '__unicode__'): return value.__unicode__()
	return str(value)

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
