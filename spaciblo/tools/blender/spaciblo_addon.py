# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
	"name": "Spaciblo JSON",
	"author": "Trevor F. Smith",
	"version": (0,1),
	"blender": (2, 5, 3),
	"api": 31667,
	"location": "File > Export > Spaciblo JSON ",
	"description": "Export Spaciblo JSON",
	"warning": "",
	"category": "Import/Export"
}

import bpy, json
from bpy.props import *

# All of the flatten_* methods transform a Blender object into a plain jane python object for easy serialization.

def flatten_material(material):
	return {
		'name': material.name, 'type':material.type, 'ambient':material.ambient, 'alpha':material.alpha,
		'diffuse_color':[material.diffuse_color[0], material.diffuse_color[1], material.diffuse_color[2]],
		'specular_color':[material.specular_color[0], material.specular_color[1], material.specular_color[2]],
		'specular_alpha':material.specular_alpha
	}

def flatten_scene(scene, apply_modifiers):
	objects = [flatten_object(obj, apply_modifiers) for obj in scene.objects]
	return { 'name':scene.name, 'objects':objects }

def flatten_object(obj, apply_modifiers):
	result = {	
				'name':obj.name, 'type':obj.type,
				'scale':[obj.scale[0], obj.scale[1], obj.scale[2]],
				'location':[obj.location[0], obj.location[1], obj.location[2]],
				'rotation':[obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]]
				}
	if(obj.type != 'MESH'): return result
	if apply_modifiers:
		mesh = obj.create_mesh(bpy.context.scene, True, "PREVIEW")
	else:
		mesh = obj.data
	result['data'] = flatten_mesh(mesh)
	return result

def flatten_mesh(mesh):
	vertices = []
	for v in mesh.vertices: vertices.extend([v.co[0], v.co[1], v.co[2]])

	normals = []
	for v in mesh.vertices: normals.extend([v.normal[0], v.normal[1], v.normal[2]])

	faces = []
	for f in mesh.faces: faces.append([vi for vi in f.vertices])

	edges = []
	for e in mesh.edges: edges.extend([e.vertices[0], e.vertices[1]])

	materials = [flatten_material(m) for m in mesh.materials]

	return {'name': mesh.name, 'vertices':vertices, 'normals':normals, 'edges':edges, 'faces':faces, 'materials':materials }


def write_json(filepath, scene, apply_modifiers=True, pretty_json=False):
	file = open(filepath, "w")
	if pretty_json:
		file.write(json.dumps(flatten_scene(scene, apply_modifiers), indent=4))
	else:
		file.write(json.dumps(flatten_scene(scene, apply_modifiers)))
	file.close()

class SpacibloJSONExporter(bpy.types.Operator):
	bl_idname = "export_spaciblo.json"
	bl_label = "Export Spaciblo JSON"

	filepath = StringProperty(name="File Path", description="Filepath used for exporting the file", maxlen= 1024, default= "")
	check_existing = BoolProperty(name="Check Existing", description="Check and warn on overwriting existing files", default=True, options={'HIDDEN'})
	apply_modifiers = BoolProperty(name="Apply Modifiers", description="Use transformed mesh data from each object", default=True)
	pretty_json = BoolProperty(name="Pretty JSON", description="Indent the JSON elements (increases file size)", default=False)

	def execute(self, context):
		print('apply modifiers', self.apply_modifiers, self.pretty_json)
		write_json(self.filepath, bpy.data.scenes[0], self.apply_modifiers, self.pretty_json)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.add_fileselect(self)
		return {'RUNNING_MODAL'}

def menu_export(self, context):
	import os
	default_path = os.path.splitext(bpy.data.filepath)[0] + ".json"
	self.layout.operator(SpacibloJSONExporter.bl_idname, text="Spaciblo JSON (.json)").filepath = default_path

def register(): bpy.types.INFO_MT_file_export.append(menu_export)

def unregister(): bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__": register()