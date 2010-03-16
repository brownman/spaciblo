import time
import pprint
import simplejson
import datetime

from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import Client
from django.contrib.sessions.models import Session

import spaciblo.settings as settings
from sim.loaders.obj import ObjLoader, MtlLibLoader
from ground.hydration import Hydration

class ObjTest(TransactionTestCase): 
	"""A test suite for the loading Obj files."""
	def setUp(self):
		pass
	def tearDown(self):
		pass

	def test_cube(self):
		parser = ObjLoader()
		obj = parser.parse(open('example/template/Cube/cube.obj').read())
		self.assertEqual(6, len(obj.faces), 'The cube should have six faces')
		self.assertEqual(4, len(obj.faces[0]), 'The cube face should have four points')
		self.assertEqual([0,1,2,3], [point[0] for point in obj.faces[0]], 'The first face should have point vertices of [0, 1, 2, 3]: %s' % [point[0] for point in obj.faces[0]])
		self.assertEqual(1, len(obj.material_groups), 'There should be only one material')
		self.assertEqual('Material', obj.material_groups[0][0], 'Material name should be "Material"')
		self.assertEqual(1, len(obj.mtllibs), 'Should have only one mtllib')
		self.assertEqual('cube.mtl', obj.mtllibs[0], 'The mtllib should be "cube.mtl"')

		mtl_parser = MtlLibLoader()
		mtl = mtl_parser.parse(open('example/template/Cube/cube.mtl').read())
		self.assertEqual(1, len(mtl.materials), 'Should have one material %s' % len(mtl.materials))
		self.assertEqual('Material', mtl.materials[0].name, 'Incorrect material name: %s' % mtl.materials[0].name)
		self.assertEqual(96.078431, mtl.materials[0].phong_specular, 'Incorrect phong_specular %s' % mtl.materials[0].phong_specular)
		self.assertEqual([0.262127, 0.371511, 0.800000], mtl.materials[0].diffuse, 'Incorrect diffuse: %s' % mtl.materials[0].diffuse)
		
		geometry = obj.toGeometry(mtl)
		self.assertTrue(len(geometry.children) == 0, "The cube geometry should have no children")
		
	def test_moon(self):
		parser = ObjLoader()
		obj = parser.parse(open('example/template/moon/Moon.obj').read())
		self.assertEqual(1, len(obj.object_groups), 'Should have one object group')
		self.assertEqual('Globe', obj.object_groups[0][0], 'The object group should be named "Globe"')
		self.assertEqual(1, len(obj.smoothing_groups), 'Should have one smoothing group')
		self.assertEqual(0, obj.smoothing_groups[0][0], 'The smoothing group starts with the first face')
		self.assertEqual(len(obj.faces), obj.smoothing_groups[0][1], 'The smoothing group contains all of the faces')

	def test_sofa(self):
		parser = ObjLoader()
		obj = parser.parse(open('example/template/LeCorbusier Sofa/LeCorbusierSofa.obj').read())
		self.assertEqual(2236, (len(obj.vertices) / 3), 'Should have 2236 vertices: %s' % (len(obj.vertices) / 3))
		self.assertEqual(3296, len(obj.faces), 'Should have 3296 faces: %s' % len(obj.faces))
		self.assertEqual(3, len(obj.object_groups), 'Should have three object groups')
		self.assertEqual("Object01_02_-_Def", obj.object_groups[0][0], 'Object group name was %s' % obj.object_groups[0][0])
		self.assertEqual(96, obj.object_groups[0][2], 'Should have 96 faces in the first object group: %s' % obj.object_groups[0][2])
		self.assertEqual(1784, obj.object_groups[1][2], 'Should have 1784 faces in the first object group: %s' % obj.object_groups[1][2])
		self.assertEqual(1416, obj.object_groups[2][2], 'Should have 1416 faces in the first object group: %s' % obj.object_groups[2][2])
		self.assertEqual(3, len(obj.smoothing_groups), 'Should have three smoothing groups')
		self.assertEqual(obj.object_groups[2][1], obj.smoothing_groups[2][0], 'The object and smoothing groups should be the same')
		self.assertEqual(3, len(obj.material_groups), 'Should have three material groups %s' % len(obj.material_groups))

		mtl_parser = MtlLibLoader()
		mtl = mtl_parser.parse(open('example/template/LeCorbusier Sofa/LeCorbusierSofa.mtl').read())
		self.assertEqual(2, len(mtl.materials), 'Should have two materials: %s' % len(mtl.materials))
		self.assertEqual('01_-_Default', mtl.materials[1].name)
	
		geometry = obj.toGeometry(mtl)
		self.assertEqual(obj.object_groups[0][2], len(geometry.children[0].faces), 'Geometry and obj group do not have the same number of faces: %s and %s' % (obj.object_groups[0][2], len(geometry.children[0].faces)))
		self.assertEqual(obj.object_groups[1][2], len(geometry.children[1].faces), 'Geometry and obj group do not have the same number of faces: %s and %s' % (obj.object_groups[1][2], len(geometry.children[1].faces)))
		self.assertEqual(obj.object_groups[2][2], len(geometry.children[2].faces), 'Geometry and obj group do not have the same number of faces: %s and %s' % (obj.object_groups[2][2], len(geometry.children[2].faces)))

	def test_beanie(self):
		parser = ObjLoader()
		obj = parser.parse(open('example/template/Beanie/beanie.obj').read())
		self.assertEqual(152, len(obj.uvs) / 2, 'Beanie should have 152 uvs: %s' % (len(obj.uvs) / 2))
		mtl_parser = MtlLibLoader()
		mtl = mtl_parser.parse(open('example/template/Beanie/beanie.mtl').read())
		geometry = obj.toGeometry(mtl)
		# Test that all of the faces point to valid indices
		for face in geometry.faces:
			for point in face:
				self.assertTrue(point[0] < (len(geometry.vertices) / 3))
				self.assertTrue(point[1] < (len(geometry.uvs) / 2))
				self.assertTrue(point[2] < (len(geometry.normals) / 3))

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
