
class Obj:
	def __init__(self):
		pass

class ObjLoader:
	def __init__(self):
		self.PARSE_FUNCTIONS = {
			'v':self.parse_v,
			'vt':self.parse_vt,
			'vn':self.parse_vn,
			'f':self.parse_f,
			'g':self.parse_g,
			'o':self.parse_g,
			'usemtl':self.parse_usemtl,
			's':self.parse_s,
			'#':self.parse_pound,
			'mtllib':self.parse_mtllib
		}

	def parse(self, input):
		self.obj = new Obj()
		self.group = None
		self.group_range_lower = None
		self.material_group = None
		self.material_group_range_lower = None
		self.smoothing_group = None
		self.smoothing_group_range_lower = None

		for line in input.split('\n'):
			tokens = line.split(' ')
			if len(tokens) == 0: continue
			if not self.PARSE_FUNCTIONS.has_key(tokens[0]):
				print 'Unhandled line: %s' % line
				continue
			self.PARSE_FUNCTIONS[tokens[0]](tokens)
		return self.obj
		
	def parse_v(self, tokens): pass
	def parse_vt(self, tokens): pass
	def parse_vn(self, tokens): pass
	def parse_f(self, tokens): pass
	def parse_g(self, tokens): pass
	def parse_usemtl(self, tokens): pass
	def parse_s(self, tokens): pass
	def parse_pound(self, tokens): pass
	def parse_mtllib(self, tokens): pass
