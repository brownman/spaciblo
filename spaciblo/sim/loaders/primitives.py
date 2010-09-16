
from sim.glge import Scene,  Object,  Mesh,  Material

def create_plane(color=None):
	"""Returns a glge.Object which is a two triangle plane"""
	plane = Object()
	plane.mesh = Mesh()
	plane.mesh.positions = [1.000, 1.000, 0.000, 
							-1.000, 1.000, 0.000, 
							-1.000, -1.000, 0.000, 
							1.000, 1.000, 0.000, 
							-1.000, -1.000, 0.000, 
							1.000, -1.000, 0.000]
							
	plane.mesh.normals = [-0.000, 0.000, 1.000, 
							-0.000, 0.000, 1.000, 
							-0.000, 0.000, 1.000, 
							0.000, -0.000, 1.000, 
							0.000, -0.000, 1.000, 
							0.000, -0.000, 1.000]
							
	plane.mesh.UV = [0.000, 0.000,
					1.000, 0.000, 
					1.000, 1.000, 
					0.000, 0.000, 
					1.000, 1.000, 
					0.000, 1.000]

	plane.mesh.faces = [0, 1, 2, 3, 4, 5]
	plane.material = Material()
	plane.material.color = color or [1, 0.5, 0.5, 1]
	return plane

def create_box(color=None):
	"""Returns a glge.Object which is a cube"""
	box = Object()
	box.mesh = Mesh()
	box.mesh.positions = [1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 0.99999899999999997, 1.0, 1.0000009999999999, 1.0, -1.0, 1.0, 0.99999899999999997, 1.0, 1.0000009999999999, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
	box.mesh.faces = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
	box.material = Material()
	box.material.color = color or [1, 0.5, 0.5, 1]
	return box
