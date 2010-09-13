
from sim.glge import Scene,  Object,  Mesh,  Material

def create_plane(color=[1, 0.5, 0.5, 1]):
	"""Returns a glge.Object which is a two triangle plane"""
	box = Object()
	box.mesh = Mesh()
	box.mesh.positions = [1.000, 1.000, 0.000, 
							-1.000, 1.000, 0.000, 
							-1.000, -1.000, 0.000, 
							1.000, 1.000, 0.000, 
							-1.000, -1.000, 0.000, 
							1.000, -1.000, 0.000]
							
	box.mesh.normals = [-0.000, 0.000, 1.000, 
							-0.000, 0.000, 1.000, 
							-0.000, 0.000, 1.000, 
							0.000, -0.000, 1.000, 
							0.000, -0.000, 1.000, 
							0.000, -0.000, 1.000]
							
	box.mesh.UV = [0.000, 0.000,
					1.000, 0.000, 
					1.000, 1.000, 
					0.000, 0.000, 
					1.000, 1.000, 
					0.000, 1.000]

	box.mesh.faces = [0, 1, 2, 3, 4, 5]
	box.material = Material()
	box.material.color = color
	return box

