import simplejson

from models import *

"""A set of objects which define the visual aspects of a 3D scene: position, orientation, motion, geometry, material, lighting...
This code assumes a single thread game loop, so none of the classes defined in this module are thread safe.
"""

class SceneNode:
	"""The base class which all scene elements extend."""
	def node_name(cls):
		return cls.__name__
	node_name = classmethod(node_name)


class Color(SceneNode):
	"""Red, green, blue, and alpha ranging from 0.0 to 1.0.  Alpha at 0 indicates transparency."""
	def __init__(self, red=1.0, green=1.0, blue=1.0, alpha=1.0):
		self.red = red
		self.green = green
		self.blue = blue
		self.alpha = alpha
	def hydrate(self, data):
		self.red, self.green, self.blue, self.alpha = data.split(',')
		return self
	def __unicode__(self):
		return "%s,%s,%s,%s" % (self.red, self.green, self.blue, self.alpha)

class Position(SceneNode):
	"""A cartesian coordinate in 3 dimensions"""
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x
		self.y = y
		self.z = z
	def hydrate(self, data):
		self.x, self.y, self.z = data.split(',')
		return self
	def __unicode__(self):
		return "%s,%s,%s" % (self.x, self.y, self.z)
		
class Orientation(SceneNode):
	"""Your basic quaternion"""
	def __init__(self, s=1.0, x=0.0, y=0.0, z=0.0):
		self.s = s
		self.x = x
		self.y = y
		self.z = z
	def hydrate(self, data):
		self.s, self.x, self.y, self.z = data.split(',')
		return self
	def __unicode__(self):
		return "%s,%s,%s,%s" % (self.s, self.x, self.y, self.z)

class MotionFrame(SceneNode):
	"""A TCB (aka Kochanek-Bartels) spline interpolation key frame"""
	def __init__(self, knot, tension=0.0, continuity=0.0, bias=0.0, position=Position(), orientation=Orientation(), scale=1.0, linear=False):
		self.knot = knot # the position along the interpolation [0.0 - 1.0]

		self.tension = tension # (-1.0 - 1.0)
		self.continuity = continuity # (-1.0 - 1.0)
		self.bias = bias # (-1.0 - 1.0)

		self.position = position
		self.orientation = orientation
		self.scale = scale

		self.linear = linear # True for linear interpolation instead of spline
	class HydrationMeta:
		attributes = ['knot', 'tension', 'bias', 'position', 'orientation', 'scale', 'linear']

class Motion(SceneNode):
	"""A TCB (aka Kochanek-Bartels) spline interpolation path"""
	def __init__(self, frames=[], loop=False):
		self.frames = frames # an array of MotionFrames
		self.loop = loop
	class HydrationMeta:
		attributes = ['loop']
		nodes = ['frames']

class Material(SceneNode):
	def __init__(self, fill_color=Color(0.8, 0.8, 0.8), line_color=Color(0,0,0)):
		self.fill_color = fill_color
		self.line_color = line_color
		# texture
		# animated
		# double_sided
		# smooth
		# ...
	class HydrationMeta:
		attributes = ['fill_color', 'line_color']

class Face(SceneNode):
	"""indices into the vertices array of Position objects"""
	def __init__(self, position_1, position_2, position_3):
		self.position_1 = position_1 
		self.position_2 = position_2
		self.position_3 = position_3
	class HydrationMeta:
		attributes = ['position_1', 'position_2', 'position_3']

class Geometry(SceneNode):
	def __init__(self, material=Material(), vertices=[], faces=[], position=Position(), orientation=Orientation(), scale=1.0, motion=None):
		self.material = material
		self.vertices = vertices # an array of Positions objects
		self.faces = faces # an array of Face objects

		self.position = position
		self.orientation = orientation
		self.motion = motion
		self.scale = scale
		
		self.parent = None
		self.children = []
	class HydrationMeta:
		attributes = ['position', 'orientation', 'scale']
		nodes = ['material', 'vertices', 'faces', 'motion']

class Light(SceneNode):
	light_types = ['ambient', 'directional', 'point']

	def __init__(self, light_type='ambient', color=Color(0.8, 0.8, 0.8, 1.0), position=Position(400, 400, 400), orientation=Orientation(), motion=None):
		self.light_type = light_type
		self.color = color
		
		self.position = position
		self.orientation = orientation
		self.motion = motion
	class HydrationMeta:
		attributes = ['light_type', 'color', 'position', 'orientation']
		nodes = ['motion']

class Thing(SceneNode):
	"""A node in an ADG of positioned, oriented, lit, and movable geometries."""
	def __init__(self, id, template=None, position=Position(), orientation=Orientation(), scale=1.0, motion=None, user=None):
		"""A positioned object in a scene"""
		self.id = id
		self.template = template
		self.geometry = None

		self.settings = {}

		self.position = position
		self.orientation = orientation
		self.scale = scale # [0.0 - 1.0]
		self.motion = motion

		self.lights = []

		self.parent = None
		self.children = []

		self.user = user # None if not an avatar
	def get_avatar(self, username):
		for thing in self.list_things():
			if thing.user != None and thing.user.username == username: return thing
		return None
	def list_things(self, the_list=None):
		if the_list == None: the_list = []
		the_list.append(self)
		for thing in self.children: thing.list_things(the_list)
		return the_list
	def get_max_id(self):
		max_id = self.id
		for child in self.children:
			max_id = max(max_id, child.get_max_id())
		return max_id
	def remove_thing(self, thing):
		for child in self.children:
			if child.id == thing.id:
				self.children.remove(child)
				return True
			if child.remove_thing(thing): return True
		return False
		
	def add_thing(self, thing):
		self.children.append(thing)
	def hydrate(self, json_data):
		if json_data.has_key('position'): self.position.hydrate(json_data['position'])
		if json_data.has_key('orientation'): self.orientation.hydrate(json_data['orientation'])
		if json_data.has_key('template'): self.template = Template.objects.get(pk=json_data['template'])
		if json_data.has_key('children'):
			for thing_element in json_data['children']:
				child_thing = Thing(thing_element['id'])
				child_thing.hydrate(thing_element)
				self.add_thing(child_thing)
		#TODO hydrate the scale, motion, settings, lights, and user

	class HydrationMeta:
		attributes = ['id', 'position', 'orientation', 'scale']
		ref_attributes = ['template', 'parent']
		ref_by_attributes = [('user', 'username')]
		nodes = ['settings', 'lights', 'children', 'motion']

class Scene(SceneNode):
	"""A root thing and some global values which define the visual aspects of a 3D scene for a Space."""
	def __init__(self, space, background_color=Color(0.2, 0.2, 0.8)):
		self.space = space
		self.thing = None
		self.background_color = background_color
		self.hydrate(simplejson.loads(space.scene_document))
	def add_avatar(self, user, position, orientation):
		avatar_thing = Thing(self.thing.get_max_id() + 1, position=position, orientation=orientation, user=user)
		self.thing.add_thing(avatar_thing)
		return avatar_thing
	def hydrate(self, json_data):
		if json_data.has_key('Thing'):
			self.thing = Thing(json_data['Thing']['id'])
			self.thing.hydrate(json_data['Thing'])
		return self
	class HydrationMeta:
		attributes = ['background_color']
		nodes = ['thing']

SCENE_GRAPH_CLASSES = [Color, Position, Orientation, Material, MotionFrame, Motion, Light, Face, Geometry, Scene, Thing]

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
