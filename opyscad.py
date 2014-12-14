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

def create_class(name, pos_arg_keys = None, s_arg_keys = None, has_childs = False):
	if not pos_arg_keys:
		pos_arg_keys = []
	if not s_arg_keys:
		s_arg_keys = []

	class Abstract:
		childs = None
		modifiers = ''
		def __init__(self, *args, **kwargs):
			self.name = name
			self.args = create_args(args, kwargs, pos_arg_keys, s_arg_keys)

		def __add__(self, x):
			if not hasattr(x, 'name'):
				raise Exception('Add argument must be a pyscad object')
			elif x.name == 'union':
				x.childs.append(self)
				return x
			elif self.name == 'union':
				self.childs.append(x)
				return self
			return union()(self, x)

		def __and__(self, x):
			if not hasattr(x, 'name'):
				raise Exception('Add argument must be a pyscad object')
			elif x.name == 'intersection':
				x.childs.append(self)
				return x
			elif self.name == 'intersection':
				self.childs.append(x)
				return self
			return intersection()(self, x)

		def __sub__(self, x):
			return difference()(self, x)

		def __lshift__(self, x): # translate
			if type(x) != list:
				raise Exception('Translate argument must be a list type')
			return translate(x)(self)

		def __mul__(self, x): # scale
			if type(x) not in (list, int):
				raise Exception('Scale argument must be a list or int type')
			return scale(x)(self)

		def __div__(self, x): # rotate
			if type(x) != list:
				raise Exception('Rotate argument must be a list type')
			return rotate(x)(self)

		def __or__(self, x): # mirror
			if type(x) != list:
				raise Exception('Mirror argument must be a list type')
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
			if self.childs != None:
				childs = map(lambda x: x.str(indent + 1), self.childs)
				res += ' {\n%s\n%s}' % ('\n'.join(childs), '\t'*indent)
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
			self.childs = []

		def __call__(self, *args):
			self.childs = list(args)
			return self

	if has_childs:
		return AbstractIns
	else:
		return Abstract


#============= 2D primitives
square = create_class('square', ['size', 'center'])
circle = create_class('circle', ['r'], ['fn'])
polygon = create_class('polygon', ['points', 'paths', 'convexity'])
offset = create_class('offset', ['delta', 'join_type', 'miter_limit'], has_childs = True)

#============= 3D primitives
cube = create_class('cube', ['size', 'center'])
sphere = create_class('sphere', ['r'], ['fa', 'fs', 'fn'])
cylinder = create_class('cylinder', ['h', 'r'], ['fa', 'fs', 'fn'])
polyhedron = create_class('polyhedron', ['points', 'triangles', 'convexity'])

#============= transforms
scale = create_class('scale', ['v'], has_childs = True)
resize = create_class('resize', ['newsize', 'auto'], has_childs = True)
rotate = create_class('rotate', ['a', 'v'], has_childs = True)
translate = create_class('translate', ['v'], has_childs = True)
mirror = create_class('mirror', ['v'], has_childs = True)
multmatrix = create_class('multmatrix', ['m'], has_childs = True)
color = create_class('color', ['c', 'alpha'], has_childs = True)
minkowski = create_class('minkowski', has_childs = True)
hull = create_class('hull', has_childs = True)
render = create_class('render', ['convexity'], has_childs = True)

#============= boolean operations
union = create_class('union', has_childs = True)
intersection = create_class('intersection', has_childs = True)
difference = create_class('difference', has_childs = True)

#============= extrusions
linear_extrude = create_class('linear_extrude', ['height', 'center'], ['fn'], has_childs = True)
rotate_extrude = create_class('rotate_extrude', ['convexity'], ['fn'], has_childs = True)
projection = create_class('projection', ['cut'], has_childs = True)
surface = create_class('surface', ['file', 'center', 'convexity'], has_childs = True)

#============= modifiers
imp = create_class('import', ['"filename'])

