import logging
log = logging.getLogger(__name__)

class ProxyBase(object):
	__slots__ = ["obj", "args", "pool"]
	def __init__(self, obj, args = None, pool = None):
		object.__setattr__(self, "obj", obj)
		object.__setattr__(self, "args", args)
		object.__setattr__(self, "pool", pool)

	def __getattribute__(self, name):
		return getattr(object.__getattribute__(self, "obj"), name)

	def __delattr__(self, name):
		delattr(object.__getattribute__(self, "obj"), name)

	def __setattr__(self, name, value):
		setattr(object.__getattribute__(self, "obj"), name, value)

	def __nonzero__(self):
		return bool(object.__getattribute__(self, "obj"))

	def __str__(self):
		return str(object.__getattribute__(self, "obj"))

	def __repr__(self):
		return repr(object.__getattribute__(self, "obj"))

	def __del__(self):
		pool = object.__getattribute__(self, "pool")
		if pool is not None:
			pool.push(object.__getattribute__(self, "obj"),object.__getattribute__(self, "args") )



class ObjectPool(object):
	special_names = [
	    '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__', 
	    '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__', 
	    '__eq__', '__float__', '__floordiv__', '__ge__'
	    '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
	    '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__', 
	    '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', 
	    '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', 
	    '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', 
	    '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__', 
	    '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__', 
	    '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__', 
	    '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', 
	    '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', 
	    '__truediv__', '__xor__', 'next',
	    ]

	def __init__(self, objtype, proxybase = ProxyBase):
		def make_method(name):
			def method(self, *args, **kw):
				return getattr(object.__getattribute__(self, "obj"), name)(*args, **kw)
			return method

		namespace = {"objclass" : objtype}
		for name in self.special_names:
			if hasattr(objtype, name):
				namespace[name] = make_method(name)
		self.proxytype = type("proxy(%s)" % objtype.__name__, (proxybase,), namespace)
		self.objtype = objtype
		self.objdict = {}

	def push(self, object, args):
		self.objdict[args].append(object)

	def get(self, *args):
		if args not in self.objdict:
			self.objdict[args] = []
		objlst = self.objdict[args]
		if len(objlst) != 0:
			obj = objlst.pop()
		else:
			if log.isEnabledFor(logging.INFO):
				log.info("Allocating frint32om object pool : %s" % str(args))
			obj = self.objtype(*args)
		return self.proxytype(obj, pool = self, args = args)

	__call__ = get

