"""A library for manipulating Obj and Mtl data.

NOTE: These data structures use 0-based indexing (like the rest of python), even though Obj uses 1 based indexing.

"""

from sim.glge import Group, Object, Material, Mesh

class Loader:
	def prep_line(self, line):
		if len(line.strip()) == 0: return None
		if line[0] == '#': return None
		if line.count('#') == 0: return line
		return line.split('#', 1)[0].strip()

	def inner_parse(self, input):
		for line in input.split('\n'):
			line = self.prep_line(line)
			if not line: continue
			tokens = line.split(' ')
			if not self.PARSE_FUNCTIONS.has_key(tokens[0].lower()): continue
			self.PARSE_FUNCTIONS[tokens[0].lower()](tokens)

class ObjMaterial:	
	def __init__(self, name, specular=[0.5,0.5,0.5], ambient=[0.5,0.5,0.5], diffuse=[0.5,0.5,0.5], alpha=1.0, phong_specular=1, illumination=2, ambient_map=None, diffuse_map=None, specular_map=None, alpha_map=None, bump_map=None):
		self.name = name
		self.specular = specular # Ks 1.0 1.0 1.0
		self.ambient = ambient #Ka 1.0 1.0 1.0
		self.diffuse = diffuse #Kd 1.0 1.0 1.0
		self.alpha = alpha #d 1.0 or Tr 1.0 
		self.phong_specular = phong_specular # Ns [0.0-1000.0]
		self.illumination = illumination # illum [0 - 2]
		
		# texture maps, all of these are file names
		self.specular_map = specular_map #map_Ks file.tga
		self.ambient_map = ambient_map #map_Ka file.tga
		self.diffuse_map = diffuse_map #map_Kd file.tga
		self.alpha_map = alpha_map # map_d file.tgz 
		self.bump_map = bump_map #map_Bump file.tga or bump file.tga

	class HydrationMeta:
		attributes = ['name', 'alpha', 'phong_specular', 'illumination', 'ambient_map', 'diffuse_map', 'specular_map', 'alpha_map', 'bump_map']
		raw_nodes = ['specular', 'ambient', 'diffuse']

class MtlLib:
	def __init__(self):
		self.materials = [] # an array ObjMaterial objects
		
	class HydrationMeta:
		nodes = ['materials']

class MtlLibLoader(Loader):
	def __init__(self):
		self.lib = None
		self.material = None
		
		self.PARSE_FUNCTIONS = {
			'newmtl':self.parse_newmtl,
			'ks':self.parse_ks,
			'ka':self.parse_ka,
			'kd':self.parse_kd,
			'd':self.parse_d,
			'tr':self.parse_d,
			'ns':self.parse_ns,
			'illum':self.parse_illum,
			'map_ks':self.parse_map_ks,
			'map_ka':self.parse_map_ka,
			'map_kd':self.parse_map_kd,
			'map_d':self.parse_map_d,
			'map_bump':self.parse_map_bump,
			'bump':self.parse_map_bump,
			'#':self.parse_pound
		}

	def parse(self, input):
		self.lib = MtlLib()
		self.material = None

		self.inner_parse(input)

		if self.material: self.lib.materials.append(self.material)

		return self.lib

	def parse_newmtl(self, tokens):
		name = ' '.join(tokens[1:])
		if self.material: self.lib.materials.append(self.material)
		self.material = ObjMaterial(name)

	def parse_ks(self, tokens): self.material.specular = [float(f) for f in tokens[1:]]
		
	def parse_ka(self, tokens): self.material.ambient = [float(f) for f in tokens[1:]]

	def parse_kd(self, tokens): self.material.diffuse = [float(f) for f in tokens[1:]]

	def parse_d(self, tokens): self.material.alpha = float(tokens[1])

	def parse_ns(self, tokens): self.material.phong_specular = float(tokens[1])

	def parse_illum(self, tokens): self.material.illumination = int(tokens[1])

	def parse_map_ks(self, tokens): self.material.specular_map = ' '.join(tokens[1:])

	def parse_map_ka(self, tokens): self.material.ambient_map = ' '.join(tokens[1:])

	def parse_map_kd(self, tokens): self.material.diffuse_map = ' '.join(tokens[1:])

	def parse_map_d(self, tokens): self.material.alpha_map = ' '.join(tokens[1:])

	def parse_map_bump(self, tokens): self.material.bump_map = ' '.join(tokens[1:])

	def parse_pound(self, tokens): pass

class Obj:
	"""A data structure representing the data in an Obj file"""
	def __init__(self):
		self.mtllib = None # a string holding the name of material file
		
		self.vertices = [] # an array of floats, each three representing x,y,z coordinates
		self.normals = [] # an array of floats, each three representing a normal vector
		self.uvs = [] # an array of floats, each two representing texture u,v coordinates

		# faces is a three dimensional array of floats
		# the first dimension is the face index
		# the second dimension is the face sequence index. There are 3 for triangles, 4 for quads, ...
		# the third dimension is a triple: [vertex index, texture index, normal index]
		self.faces = []

		self.object_groups = []  # an array of arrays of form ['object name', start_face_index, num_faces]
		self.polygon_groups = [] # an array of arrays of form ['polygon name' start_face_index, num_faces]
		self.material_groups = [] # an array of arrays of form ['material name', start_face_index, num_faces]
		self.smoothing_groups = [] # an array of arrays of form [start_face_index, num_faces]

	def toGeometry(self, mtllib):
		"""Returns a GLGE object (either a Group or an Object) representing this Obj file"""
		materials = self.genMaterials(mtllib)

		if len(self.object_groups) == 0: return self.genGeometry(None, 0, len(self.faces), materials)

		root_group = Group()
		for object_group in self.object_groups:
			mat_groups = []
			for mg in self.material_groups:
				if mg[1] >= object_group[1] and mg[1] < (object_group[1] + object_group[2]): mat_groups.append(mg)
			if len(mat_groups) == 0:
				root_group.children.append(self.genGeometry(object_group[0], object_group[1], object_group[1] + object_group[2]), materials)
			else:
				for mg in mat_groups:
					root_group.children.append(self.genGeometry(mg[0], mg[1], mg[1] + mg[2], materials))
		return root_group

	def objMaterialForFace(self, face_index):
		for mg in self.material_groups:
			if face_index >= mg[1] and face_index < mg[1] + mg[2]: return mg
		return None
	
	def genMaterials(self, mtllib):
		if not mtllib: return {}
		materials = {}
		for obj_mat in mtllib.materials:
			mat = Material()
			mat.color = obj_mat.diffuse
			mat.specColor = obj_mat.specular
			mat.alpha = obj_mat.alpha
			#TODO use the other obj material attributes			
			materials[obj_mat.name] = mat
		return materials
	
	def genGeometry(self, name, face_start, face_end, materials):
		obj = Object()
		obj.mesh = Mesh()
		obj_mat = self.objMaterialForFace(face_start)
		if obj_mat and materials.has_key(obj_mat[0]):
			obj.material = materials[obj_mat[0]]
		else:
			obj.material = None
		for face in self.faces[face_start:face_end]:
			for point in face[0:3]: # TODO This is treating all faces like they are triangles, which is wrong
				vertex_offset = point[0] * 3
				obj.mesh.positions.extend([self.vertices[vertex_offset], self.vertices[vertex_offset + 1], self.vertices[vertex_offset + 2]])

				if point[1]:
					uv_offset = point[1] * 2
					obj.mesh.UV.extend([self.uvs[uv_offset], self.uvs[uv_offset + 1]])
					
				if point[2]:
					normal_offset = point[2] * 3
					obj.mesh.normals.extend([self.normals[normal_offset], self.normals[normal_offset + 1], self.normals[normal_offset + 2]])
		obj.mesh.faces = range(len(obj.mesh.positions) / 3)
		return obj

class ObjLoader(Loader):
	def __init__(self):
		self.PARSE_FUNCTIONS = {
			'v':self.parse_v,
			'vt':self.parse_vt,
			'vn':self.parse_vn,
			'f':self.parse_f,
			'g':self.parse_g,
			'o':self.parse_o,
			'usemtl':self.parse_usemtl,
			's':self.parse_s,
			'mtllib':self.parse_mtllib,
			'#':self.parse_pound
		}

	def parse(self, input):
		self.obj = Obj()
		self.polygon_group = None
		self.object_group = None
		self.material_group = None
		self.smoothing_group = None

		self.inner_parse(input)
			
		# Close any open groups
		if self.material_group:
			self.material_group[2] = len(self.obj.faces) - self.material_group[1]
			self.obj.material_groups.append(self.material_group)
		if self.object_group:
			self.object_group[2] = len(self.obj.faces) - self.object_group[1]
			self.obj.object_groups.append(self.object_group)
		if self.polygon_group:
			self.polygon_group[2] = len(self.obj.faces) - self.polygon_group[1]
			self.obj.polygon_groups.append(self.polygon_group)
		if self.smoothing_group:
			self.smoothing_group[1] = len(self.obj.faces) - self.smoothing_group[0]
			self.obj.smoothing_groups.append(self.smoothing_group)

		return self.obj
		
	def parse_v(self, tokens): 
		self.obj.vertices.extend([float(tokens[1]), float(tokens[2]), float(tokens[3])])
		
	def parse_vt(self, tokens):
		self.obj.uvs.extend([float(tokens[1]), float(tokens[2])])
		
	def parse_vn(self, tokens):
		self.obj.normals.extend([float(tokens[1]), float(tokens[2]), float(tokens[3])])
		
		
	def parse_index(self, token):
		"""Returns int(token) - 1 to switch from 1-index to 0-index or None if token is not an int"""
		if token == None: return None
		if len(token) == 0: return None
		return int(token) - 1

	def parse_f(self, tokens):
		face = []
		for triple in tokens[1:]:
			point = [self.parse_index(t) for t in triple.split('/')]
			while len(point) < 3: point.append(None)
			face.append(point)
		self.obj.faces.append(face)

	def parse_usemtl(self, tokens):
		mat_name = ' '.join(tokens[1:])
		if self.material_group:
			if self.material_group[0] == mat_name: return
			self.material_group[2] = len(self.obj.faces) - self.material_group[1]
			self.obj.material_groups.append(self.material_group)
			self.material_group = None
		self.material_group = [mat_name, len(self.obj.faces), None]

	def parse_o(self, tokens):
		name = ' '.join(tokens[1:])
		if self.object_group:
			if self.object_group[0] == name: return
			self.object_group[2] = len(self.obj.faces) - self.object_group[1]
			self.obj.object_groups.append(self.object_group)
			# we assume that if the object group closes then the other groups close
			if self.material_group:
				self.material_group[2] = len(self.obj.faces) - self.material_group[1]
				self.obj.material_groups.append(self.material_group)
				self.material_group = None
			if self.polygon_group:
				self.polygon_group[2] = len(self.obj.faces) - self.polygon_group[1]
				self.obj.polygon_groups.append(self.polygon_group)
				self.polygon_group = None
			if self.smoothing_group:
				self.smoothing_group[1] = len(self.obj.faces) - self.smoothing_group[0]
				self.obj.smoothing_groups.append(self.smoothing_group)
				self.smoothing_group = None
		self.object_group = [name, len(self.obj.faces), None]

	def parse_g(self, tokens):
		name = ' '.join(tokens[1:])
		if self.polygon_group:
			if self.polygon_group[0] == name: return
			self.polygon_group[2] = len(self.obj.faces) - self.polygon_group[1]
			self.obj.polygon_groups.append(self.polygon_group)
		self.polygon_group = [name, len(self.obj.faces), None]

	def parse_s(self, tokens):
		name = ' '.join(tokens[1:])
		if name == 'off':
			if self.smoothing_group:
				self.smoothing_group[2] = len(self.obj.faces) - self.smoothing_group[1]
				self.obj.smoothing_groups.append(self.smoothing_group)
				self.smoothing_group = None
		else:
			if self.smoothing_group:
				self.smoothing_group[1] = len(self.obj.faces) - self.smoothing_group[0]
				self.obj.smoothing_groups.append(self.smoothing_group)
			self.smoothing_group = [len(self.obj.faces), None]

	def parse_mtllib(self, tokens):
		self.obj.mtllib = ' '.join(tokens[1:])

	def parse_pound(self, tokens): pass # it is a comment, ignore it

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
