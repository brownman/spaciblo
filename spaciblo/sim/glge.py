"""
A set of objects which define the visual aspects of a 3D scene: position, orientation, motion, geometry, material, lighting...
"""

# Flag for material colour
M_COLOR = 1 
# Flag for material normal
M_NOR = 2
# Flag for material alpha
M_ALPHA = 4 
# Flag for material specular color
M_SPECCOLOR = 8 
# Flag for material specular cvalue
M_SPECULAR = 16
# Flag for material shineiness
M_SHINE = 32 
# Flag for material reflectivity
M_REFLECT = 64
# Flag for material emision
M_EMIT = 128
# Flag for material alpha
M_ALPHA = 256
# Flag for masking with textures red value
M_MSKR = 512
# Flag for masking with textures green value
M_MSKG = 1024
# Flag for masking with textures blue value
M_MSKB = 2048
# Flag for masking with textures alpha value
M_MSKA = 4096
# Flag for mapping of the height in parallax mapping
M_HEIGHT = 8192
# Enumeration for first UV layer
UV1 = 0
# Enumeration for second UV layer
UV2 = 1
# Enumeration for normal texture coords
MAP_NORM = 3
# Enumeration for object texture coords
MAP_OBJ = 4
# Enumeration for reflection coords
MAP_REF = 5
# Enumeration for environment coords
MAP_ENV = 6
# Enumeration for view coords
MAP_VIEW = 7
# Enumeration for mix blending mode
BL_MIX = 0
# Enumeration for mix blending mode
BL_MUL = 1
# Enumeration for a perspective camera
C_PERSPECTIVE=1
# Enumeration for a orthographic camera
C_ORTHO = 2
# Enumeration for no fog
FOG_NONE=1;
# Enumeration for linear fall off fog
FOG_LINEAR=2;
# Enumeration for exponential fall off fog
FOG_QUADRATIC=3;
# Enumeration for node group type
G_NODE=1;
# Enumeration for root group type
G_ROOT=2;
# Enum for XYZ rotation order
ROT_XYZ=1;
# Enum for XZY rotation order
ROT_XZY=2;
# Enum for YXZ rotation order
ROT_YXZ=3;
# Enum for YZX rotation order
ROT_YZX=4;
# Enum for ZXY rotation order
ROT_ZXY=5;
# Enum for ZYX rotation order
ROT_ZYX=6;
# Enumeration for euler rotaions mode
P_EULER=1;
# Enumeration for quaternions mode
P_QUAT=2;
# Enumeration for matrix rotation mode
P_MATRIX=3;

def copy_attributes(target, data, ignore=None):
	if not ignore: ignore = []
	for key in data:
		if not key in ignore:
			setattr(target, key, data[key])

def populate_children(target, data):
	for child_data in data['children']:
		if hasattr(child_data, 'children'):
			child = Group().populate(child_data)
		else:
			child = Object().populate(child_data)
		target.children.append(child)

def populate_class_array(target, data, cls, key_name):
	target_array = getattr(target, key_name)
	for item_data in data[key_name]:
		target_array.append(cls().populate(item_data))

class SceneBase(object):
	"""The base class which all scene elements extend."""
	def flatten(self):
		if not hasattr(self, 'children'): return [self]
		results = [self]
		for child in self.children:
			results.append(child.flatten())
		return results

	def populate(self, data):
		"""This should return self after populating it with the data (which is probably parsed from a JSON version of a Scene)"""
		raise NotImplementedError()

	@classmethod
	def node_name(cls):
		return cls.__name__

class Placeable(SceneBase):
	def __init__(self):
		print 'initing placeable'
		self.locX = 0
		self.locY = 0
		self.locZ = 0
		self.dLocX = 0
		self.dLocY = 0
		self.dLocZ = 0
		self.quatX = 0
		self.quatY = 0
		self.quatZ = 0
		self.quatW = 0
		self.rotX = 0
		self.rotY = 0
		self.rotZ = 0
		self.dRotX = 0
		self.dRotY = 0
		self.dRotZ = 0
		self.scaleX = 1
		self.scaleY = 1
		self.scaleZ = 1
		self.dScaleX = 0
		self.dScaleY = 0
		self.dScaleZ = 0
		self.matrix = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
		self.rotOrder = ROT_XYZ
		self.mode = P_EULER
		#self.lookAt = None

class BezTriple(SceneBase):
	def __init__(self):
		self.x1 = 0
		self.y1 = 0
		self.x = 0 #why these aren't named x2 and y2, I don't know
		self.y = 0
		self.x3 = 0
		self.y3 = 0
	def __unicode__(self):
		return "%s,%s,%s,%s,%s,%s" % (self.x1, self.y1, self.x, self.y, self.x3, self.y3)


class StepPoint(SceneBase):
	def __init__(self):
		self.x = 0
		self.y = 0
	def populate(self, data):
		copy_attributes(self, data)
		return self
	def __unicode__(self):
		return "%s,%s" % (self.x, self.y)

class AnimationCurve(SceneBase):
	def __init__(self):
		self.channel = None
		self.keyFrames = []
		self.solutions = []

	def populate(self, data):
		if not data: return None
		copy_attributes(self, data)
		return self

class AnimationVector(SceneBase):
	def __init__(self):
		self.curves = []
		self.frames = 250

	def populate(self, data):
		copy_attributes(self, data, ['curves'])
		populate_class_array(self, data, AnimationCurve, 'curves')
		return self

class Animatable(SceneBase):
	def __init__(self):
		print 'initing animatable'
		self.animationStart = None
		self.animation = None
		self.blendStart = 0
		self.blendTime = 0
		self.lastFrame = None
		self.frameRate = 25
		self.loop = True
		self.paused = False
		self.pausedTime = None

class Action(SceneBase):
	def __init__(self):
		self.channels = []

	def populate(self, data):
		copy_attributes(self, data)
		populate_class_array(self, data, ActionChannel, 'channels')
		return self

class ActionChannel(SceneBase):
	def __init__(self):
		self.animation = None

	def populate(self, data):
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class Group(Animatable, Placeable):
	def __init__(self):
		Animatable.__init__(self)
		Placeable.__init__(self)
		self.children = []
		self.group_type = G_NODE

	def populate(self, data):
		copy_attributes(self, data, ['children', 'animation'])
		populate_children(self, data)
		self.animation = AnimationCurve().populate(data['animation'])
		return self
		
class Text(Placeable, Animatable):
	def __init__(self):
		Animatable.__init__(self)
		Placeable.__init__(self)
		self.zTrans = True
		self.aspect = 1.0
		self.color = [1,1,1]
		self.text = ""
		self.font = "Times"
		self.size = 100
		self.pickType = TEXT_TEXTPICK

	def populate(self, data):
		copy_attributes(self, data, ['animation'])
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class Mesh(SceneBase):
	def __init__(self):
		self.positions = []
		self.normals = []
		self.faces = []
		self.UV = []
		self.joints = []
		self.invBind = None

	def populate(self, data):
		copy_attributes(self, data)
		return self

class Light(Placeable, Animatable):
	def __init__(self):
		Animatable.__init__(self)
		Placeable.__init__(self)
		self.constantAttenuation = 1
		self.linearAttenuation = 0.002
		self.quadraticAttenuation = 0.0008
		self.spotCosCutOff = 0.95
		self.spotPMatrix = None
		self.spotExponent = 10
		self.color = [1,1,1] 
		self.diffuse = True 
		self.specular = True 
		self.samples = 0 
		self.softness = 0.01 
		self.type = L_POINT
		self.texture = None
		self.shadowBias = 2.0
		self.castShadows = False

	def populate(self, data):
		copy_attributes(self, data, ['animation', 'texture'])
		self.texture = Texture().populate(data['texture'])
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class Camera(Placeable, Animatable):
	def __init__(self):
		Animatable.__init__(self)
		Placeable.__init__(self)
		self.fovy = 35
		self.aspect = 1.0
		self.near = 0.1
		self.far = 1000.0
		self.orthoscale = 5
		self.camera_type = C_PERSPECTIVE
		self.pMatrix = None

	def populate(self, data):
		copy_attributes(self, data, ['animation'])
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class MultiMaterial(SceneBase):
	def __init__(self):
		self.mesh = None
		self.material = None
		#self.program = None
		#self.GLShaderProgramPick = None
		#self.GLShaderProgramShadow = None
		#self.GLShaderProgram = None
	def populate(self, data):
		print data
		self.mesh = Mesh().populate(data['mesh'])
		self.material = Material().populate(data['material'])
		return self

class Object(SceneBase):
	def __init__(self):
		self.mesh = None
		self.transformMatrix = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
		self.material = None
		self.multimaterials = []
		self.zTrans = False

	def populate(self, data):
		copy_attributes(self, data, ['mesh', 'material', 'multimaterials'])
		self.mesh = Mesh().populate(data['mesh'])
		self.material = Material().populate(data['material'])
		populate_class_array(self, data, MultiMaterial, 'multimaterials')
		return self

class Texture(SceneBase):
	def __init__(self):
		#self.image = None
		self.url = None
	def __unicode__(self): return self.url

	def populate(self, data):
		copy_attributes(self, data)
		return self

class TextureCamera(SceneBase):
	def __init__(self):
		self.texture = None
		self.object = None
		self.camera = None
		self.mirrorAxis = None
		self.clipAxis = None

class TextureCube(SceneBase):
	def __init__(self):
		self.posX = 0
		self.negX = 0
		self.posY = 0
		self.negY = 0
		self.posZ = 0
		self.negZ = 0
		self.texture = None
		self.loadState = 0

	def populate(self, data):
		copy_attributes(self, data, ['texture'])
		self.texture = Texture().populate(data['texture'])
		return self

class MaterialLayer(Animatable):
	def __init__(self):
		Animatable.__init__(self)
		self.texture = None
		self.blendMode = None
		self.mapto = M_COLOR
		self.mapinput = UV1
		self.scaleX = 1
		self.offsetX = 0
		self.rotX = 0
		self.scaleY = 1
		self.offsetY = 0
		self.rotY = 0
		self.scaleZ = 1
		self.offsetZ = 0
		self.rotZ = 0
		self.dScaleX = 0
		self.dOffsetX = 0
		self.dRotX = 0
		self.dScaleY = 0
		self.dOffsetY = 0
		self.dRotY = 0
		self.dScaleZ = 0
		self.dOffsetZ = 0
		self.dRotZ = 0
		self.alpha = 1
		self.height = 0.05
		self.matrix = None
		
	def populate(self, data):
		copy_attributes(self, data, ['blendMode', 'texture', 'animation'])
		self.animation = AnimationCurve().populate(data['animation'])
		self.texture = Texture().populate(data['texture'])
		return self

class Material(Animatable):
	def __init__(self):
		Animatable.__init__(self)
		self.layers = []
		self.textures = []
		self.lights = []
		self.color = [1,1,1,1]
		self.specColor = [1,1,1]
		self.reflect = 0.8
		self.shine = 10
		self.specular = 1
		self.emit = 0
		self.alpha = 1

	def populate(self, data):
		copy_attributes(self, data, ['layers', 'textures', 'lights', 'animation'])
		populate_class_array(self, data, Texture, 'textures')
		populate_class_array(self, data, MaterialLayer, 'layers')
		populate_class_array(self, data, Light, 'lights')
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class ObjectInstance(Placeable, Animatable):
	def __init__(self):
		Animatable.__init__(self)
		Placeable.__init__(self)
		self.object = None

	def populate(self, data):
		self.object = Object().populate(data['object', 'animation'])
		self.animation = AnimationCurve().populate(data['animation'])
		return self

class Scene(Group):
	def __init__(self):
		Group.__init__(self)
		self.camera = Camera()
		self.backgroundColor = [1,1,1]
		self.fogColor = [0.5,0.5,0.5]
		self.ambientColor = [0,0,0]
		self.fogNear = 10
		self.fogFar = 80
		self.fogType = FOG_NONE
		self.children = []

	def populate(self, data):
		copy_attributes(self, data, ['children', 'camera'])
		populate_children(self, data)
		self.camera = Camera().populate(data['camera'])
		return self

SCENE_GRAPH_CLASSES = [BezTriple, StepPoint, AnimationCurve, AnimationVector, Animatable, Action, ActionChannel, Group, Text, Mesh, Light, Camera, MultiMaterial, Object, Texture, TextureCamera, TextureCube, MaterialLayer, Material, ObjectInstance, Scene]

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
