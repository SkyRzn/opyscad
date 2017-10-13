# -(unary) disable modifier (*)
# +(unary) highlight modifier (#)
# ~(unary) transparent modifier (%)
# * scale([x,y,z])
# / rotate([x,y,z])
# + union
# - difference
# << translate
# & intersection
# | mirror([x,y,z])


def create_args(args, kwargs, pos_arg_keys, s_arg_keys):
	for key, val in zip(pos_arg_keys, args):
		kwargs[key] = val

	for key, val in kwargs.items():
		if key in s_arg_keys:
			del(kwargs[key])
			key = '$' + key
		kwargs[key] = str(val).lower()

	res = []
	for key, val in kwargs.items():
		if key[0] == '"':
			res.append('%s="%s"' % (key[1:], val))
		else:
			res.append('%s=%s' % (key, val))

	return ', '.join(res)

def create_class(name, pos_arg_keys = None, s_arg_keys = None, has_children = False):
	if not pos_arg_keys:
		pos_arg_keys = []
	if not s_arg_keys:
		s_arg_keys = []

	class Abstract:
		children = None
		modifiers = ''
		def __init__(self, *args, **kwargs):
			self.name = name
			self.args = create_args(args, kwargs, pos_arg_keys, s_arg_keys)

		def __add__(self, x):
			if not hasattr(x, 'name'):
				raise Exception('Argument must be a pyscad object')
			elif x.name == 'union':
				x.children.append(self)
				return x
			elif self.name == 'union':
				self.children.append(x)
				return self
			return union()(self, x)

		def add(self, *args):
			for arg in args:
				self.__add__(arg)

		def __and__(self, x):
			if not hasattr(x, 'name'):
				raise Exception('Argument must be a pyscad object')
			elif x.name == 'intersection':
				x.children.append(self)
				return x
			elif self.name == 'intersection':
				self.children.append(x)
				return self
			return intersection()(self, x)

		def __sub__(self, x):
			return difference()(self, x)

		def __lshift__(self, x): # translate
			if type(x) != list:
				raise Exception('Argument must be a list')
			return translate(x)(self)

		def __mul__(self, x): # scale
			if type(x) not in (list, int):
				raise Exception('Argument must be a list or int')
			return scale(x)(self)

		def __div__(self, x): # rotate
			if type(x) != list:
				raise Exception('Argument must be a list')
			return rotate(x)(self)

		def __truediv__(self, x): # rotate (Python 3)
			return self.__div__(x)

		def __or__(self, x): # mirror
			if type(x) != list:
				raise Exception('Argument must be a list')
			return mirror(x)(self)

		def __neg__(self): # disable (*)
			if '*' not in self.modifiers:
				self.modifiers += '* '
			return self

		def __pos__(self): # highlight (#)
			if '#' not in self.modifiers:
				self.modifiers += '# '
			return self

		def __invert__(self): # transparent (%)
			if '%' not in self.modifiers:
				self.modifiers += '% '
			return self

		def __str__(self):
			return self.str(0)

		def str(self, indent = 0):
			res = '%s%s%s(%s)' % ('\t'*indent, self.modifiers, self.name, self.args)
			if self.children != None:
				children = map(lambda x: x.str(indent + 1), self.children)
				res += ' {\n%s\n%s}' % ('\n'.join(children), '\t'*indent)
			else:
				res += ';'
			return res

		def save(self, fn, ind = 0):
			f = open(fn, 'w')
			f.write(self.str(ind))
			f.close()

	class AbstractIns(Abstract):
		def __init__(self, *args, **kwargs):
			Abstract.__init__(self, *args, **kwargs)
			self.children = []

		def __call__(self, *args):
			self.children = list(args)
			return self

	if has_children:
		return AbstractIns
	else:
		return Abstract


#============= 2D primitives
square = create_class('square', ['size', 'center'])
circle = create_class('circle', ['r'], ['fn'])
polygon = create_class('polygon', ['points', 'paths', 'convexity'])

#============= 3D primitives
cube = create_class('cube', ['size', 'center'])
sphere = create_class('sphere', ['r'], ['fa', 'fs', 'fn'])
cylinder = create_class('cylinder', ['h', 'r'], ['fa', 'fs', 'fn'])
polyhedron = create_class('polyhedron', ['points', 'triangles', 'convexity'])

#============= transforms
offset = create_class('offset', ['delta', 'join_type', 'miter_limit'], has_children = True)
scale = create_class('scale', ['v'], has_children = True)
resize = create_class('resize', ['newsize', 'auto'], has_children = True)
rotate = create_class('rotate', ['a', 'v'], has_children = True)
translate = create_class('translate', ['v'], has_children = True)
mirror = create_class('mirror', ['v'], has_children = True)
multmatrix = create_class('multmatrix', ['m'], has_children = True)
color = create_class('color', ['c', 'alpha'], has_children = True)
minkowski = create_class('minkowski', has_children = True)
hull = create_class('hull', has_children = True)
render = create_class('render', ['convexity'], has_children = True)

#============= boolean operations
union = create_class('union', has_children = True)
intersection = create_class('intersection', has_children = True)
difference = create_class('difference', has_children = True)

#============= extrusions
linear_extrude = create_class('linear_extrude', ['height', 'center'], ['fn'], has_children = True)
rotate_extrude = create_class('rotate_extrude', ['convexity'], ['fn'], has_children = True)
projection = create_class('projection', ['cut'], has_children = True)
surface = create_class('surface', ['file', 'center', 'convexity'], has_children = True)

#============= modifiers
imp = create_class('import', ['"file'])

